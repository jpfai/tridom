#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TRIDOM — v3.3
Boundary study around C2a

Goal
----
Refine the local transition region detected around C2a in v3.2/v3.2bis.

This script:
- scans a refined local grid around C2a
- estimates MLE with the Benettin / variational equation method
- tests sensitivity to RENORM_EVERY in {5, 10, 20}
- classifies each point into:
  * CHAOS_STRONG
  * CHAOS_WEAK
  * BORDER
  * OSCILLATORY
  * UNSTABLE
- saves JSON + CSV
- generates simple diagnostic plots

Epistemic status
----------------
Numerical boundary characterization only.
This is NOT an analytical proof of chaos.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass
from itertools import product
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# GLOBAL CONFIG
# =============================================================================

SEED = 42
RNG = np.random.default_rng(SEED)

ARCS: List[Tuple[int, int]] = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]

# C2a anchor from v3.2
ANCHOR = {
    "name": "C2a",
    "topo_idx": 41,
    "perm": (0, 1, 2),
    "sigma": 10.0,
    "rho": 99.6,
    "beta": 8.0 / 3.0,
}

# Refined local grid around the critical region
SIGMA_VALS = np.linspace(9.5, 11.5, 9)
RHO_VALS = np.linspace(95.0, 105.0, 21)
BETA_VALS = np.linspace(2.4, 3.0, 9)

# Numerical integration
DT = 0.0025
BURN_STEPS = 4000
MEASURE_STEPS = 12000
TOTAL_STEPS = BURN_STEPS + MEASURE_STEPS

# Initial conditions
N_IC = 12

# Numerical control
BLOW_THRESH = 1e4
FINITE_EPS = 1e-15

# MLE / Benettin sensitivity
RENORM_GRID = [5, 10, 20]
MLE_INIT_NORM = 1e-8

# Tail diagnostics
TAIL_STEPS = 2000
VAR_THRESH = 1e-4
SPEED_THRESH = 1e-3

# Aggregate classification thresholds
MIN_BOUNDED_FRAC = 0.50
MLE_POS_THRESH_STRONG = 0.10
MLE_BORDER_EPS = 0.05
POS_LYAP_STRONG_MIN = 0.80
POS_LYAP_WEAK_MIN = 0.50

# Representative 1D cuts for plotting
SIGMA_CUT = 10.0
BETA_CUT = 2.6666666666666665  # anchor beta
SIGMA_HEATMAP = 10.0

# Matplotlib
FIG_DPI = 140


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ICResult:
    bounded: bool
    blowup: bool
    nonfinite: bool
    mle: Optional[float]
    tail_var: Optional[float]
    tail_speed: Optional[float]
    final_state: Optional[List[float]]
    n_steps_completed: int


@dataclass
class RenormMetrics:
    renorm_every: int
    bounded_frac: float
    moving_frac: float
    pos_lyap_frac: float
    mle_mean: Optional[float]
    mle_median: Optional[float]
    mle_std: Optional[float]
    n_bounded: int
    n_moving: int
    n_pos_lyap: int
    regime_local: str


@dataclass
class BoundaryCaseResult:
    anchor: str
    topo_idx: int
    perm: Tuple[int, int, int]
    topo_label: str
    perm_label: str
    effective_signature: str
    sigma: float
    rho: float
    beta: float

    # Reference metrics at renorm=10
    bounded_frac_ref: float
    moving_frac_ref: float
    pos_lyap_frac_ref: float
    mle_mean_ref: Optional[float]
    mle_median_ref: Optional[float]
    mle_std_ref: Optional[float]

    # Sensitivity metrics across RENORM_GRID
    mle_median_r5: Optional[float]
    mle_median_r10: Optional[float]
    mle_median_r20: Optional[float]
    mle_delta: Optional[float]
    mle_sign_stability: float  # fraction of sign changes over renorm grid, normalized in [0,1]
    class_v3_3: str

    # Convenience
    all_bounded: bool
    all_moving: bool
    stable_under_renorm: bool


# =============================================================================
# TOPOLOGY
# =============================================================================

def gen_dense_topologies() -> List[np.ndarray]:
    topos = []
    for signs in product([-1, 1], repeat=6):
        W = np.zeros((3, 3), dtype=float)
        for (i, j), s in zip(ARCS, signs):
            W[i, j] = float(s)
        topos.append(W)
    return topos


def topo_label(W: np.ndarray) -> str:
    parts = []
    for i, j in ARCS:
        s = "E" if W[i, j] > 0 else "I"
        parts.append(f"{i}{j}{s}")
    return ".".join(parts)


def permute_topology(W: np.ndarray, perm: Tuple[int, int, int]) -> np.ndarray:
    P = np.array(perm, dtype=int)
    Wp = np.zeros_like(W)
    for i in range(3):
        for j in range(3):
            if i != j:
                Wp[i, j] = W[P[i], P[j]]
    return Wp


def effective_signature(W: np.ndarray) -> str:
    s01 = "+" if W[0, 1] > 0 else "-"
    s10 = "+" if W[1, 0] > 0 else "-"
    s12 = "+" if W[1, 2] > 0 else "-"
    s2021 = "+" if (W[2, 0] * W[2, 1]) > 0 else "-"
    return f"W01={s01}|W10={s10}|W12={s12}|W20W21={s2021}"


# =============================================================================
# MODEL
# =============================================================================

def rhs(x: np.ndarray, W: np.ndarray, sigma: float, rho: float, beta: float) -> np.ndarray:
    """
    Signed autonomous Lorenz-like system

    x0' = sigma * W01 * (x1 - x0)
    x1' = W10 * x0 * (rho - W12*x2) - x1
    x2' = (W20*W21) * x0 * x1 - beta*x2
    """
    dx = np.zeros(3, dtype=float)
    dx[0] = sigma * W[0, 1] * (x[1] - x[0])
    dx[1] = W[1, 0] * x[0] * (rho - W[1, 2] * x[2]) - x[1]
    dx[2] = (W[2, 0] * W[2, 1]) * x[0] * x[1] - beta * x[2]
    return dx


def jacobian(x: np.ndarray, W: np.ndarray, sigma: float, rho: float, beta: float) -> np.ndarray:
    J = np.zeros((3, 3), dtype=float)

    J[0, 0] = -sigma * W[0, 1]
    J[0, 1] = sigma * W[0, 1]

    J[1, 0] = W[1, 0] * (rho - W[1, 2] * x[2])
    J[1, 1] = -1.0
    J[1, 2] = -W[1, 0] * W[1, 2] * x[0]

    s = W[2, 0] * W[2, 1]
    J[2, 0] = s * x[1]
    J[2, 1] = s * x[0]
    J[2, 2] = -beta

    return J


def state_tangent_rhs(
    x: np.ndarray,
    v: np.ndarray,
    W: np.ndarray,
    sigma: float,
    rho: float,
    beta: float,
) -> Tuple[np.ndarray, np.ndarray]:
    dx = rhs(x, W, sigma, rho, beta)
    dv = jacobian(x, W, sigma, rho, beta) @ v
    return dx, dv


def rk4_state_tangent_step(
    x: np.ndarray,
    v: np.ndarray,
    W: np.ndarray,
    sigma: float,
    rho: float,
    beta: float,
    dt: float,
) -> Tuple[np.ndarray, np.ndarray]:
    k1x, k1v = state_tangent_rhs(x, v, W, sigma, rho, beta)

    k2x, k2v = state_tangent_rhs(
        x + 0.5 * dt * k1x,
        v + 0.5 * dt * k1v,
        W, sigma, rho, beta
    )

    k3x, k3v = state_tangent_rhs(
        x + 0.5 * dt * k2x,
        v + 0.5 * dt * k2v,
        W, sigma, rho, beta
    )

    k4x, k4v = state_tangent_rhs(
        x + dt * k3x,
        v + dt * k3v,
        W, sigma, rho, beta
    )

    x_new = x + (dt / 6.0) * (k1x + 2 * k2x + 2 * k3x + k4x)
    v_new = v + (dt / 6.0) * (k1v + 2 * k2v + 2 * k3v + k4v)
    return x_new, v_new


def is_valid_state(x: np.ndarray) -> bool:
    return np.all(np.isfinite(x)) and np.max(np.abs(x)) <= BLOW_THRESH


# =============================================================================
# TRAJECTORY-LEVEL NUMERICS
# =============================================================================

def random_initial_condition(rho: float) -> np.ndarray:
    center = np.array([1.0, 1.0, max(1.0, 0.5 * rho)], dtype=float)
    return center + RNG.normal(0.0, 1.0, size=3)


def integrate_one_ic(
    W: np.ndarray,
    sigma: float,
    rho: float,
    beta: float,
    renorm_every: int,
) -> ICResult:
    x = random_initial_condition(rho)

    v = RNG.normal(0.0, 1.0, size=3)
    nv = np.linalg.norm(v)
    if nv < FINITE_EPS:
        v = np.array([1.0, 0.0, 0.0], dtype=float)
    else:
        v = (v / nv) * MLE_INIT_NORM

    tail_states: List[np.ndarray] = []
    log_sum = 0.0
    renorm_count = 0

    bounded = True
    blowup = False
    nonfinite = False
    n_steps_completed = 0

    for step in range(TOTAL_STEPS):
        x, v = rk4_state_tangent_step(x, v, W, sigma, rho, beta, DT)
        n_steps_completed = step + 1

        if not is_valid_state(x):
            bounded = False
            if not np.all(np.isfinite(x)):
                nonfinite = True
            else:
                blowup = True
            break

        if (step + 1) % renorm_every == 0:
            norm_v = np.linalg.norm(v)
            if not np.isfinite(norm_v) or norm_v < FINITE_EPS:
                bounded = False
                nonfinite = True
                break

            if step >= BURN_STEPS:
                log_sum += math.log(norm_v / MLE_INIT_NORM)
                renorm_count += 1

            v = (v / norm_v) * MLE_INIT_NORM

        if step >= TOTAL_STEPS - TAIL_STEPS:
            tail_states.append(x.copy())

    if not bounded:
        return ICResult(
            bounded=False,
            blowup=blowup,
            nonfinite=nonfinite,
            mle=None,
            tail_var=None,
            tail_speed=None,
            final_state=None,
            n_steps_completed=n_steps_completed,
        )

    tail = np.asarray(tail_states, dtype=float)
    if len(tail) < 5:
        return ICResult(
            bounded=False,
            blowup=True,
            nonfinite=False,
            mle=None,
            tail_var=None,
            tail_speed=None,
            final_state=x.tolist(),
            n_steps_completed=n_steps_completed,
        )

    diffs = np.diff(tail, axis=0)
    tail_var = float(np.mean(np.var(tail, axis=0)))
    tail_speed = float(np.mean(np.linalg.norm(diffs, axis=1)))

    if renorm_count == 0:
        mle = None
    else:
        mle = float(log_sum / (renorm_count * renorm_every * DT))

    return ICResult(
        bounded=True,
        blowup=False,
        nonfinite=False,
        mle=mle,
        tail_var=tail_var,
        tail_speed=tail_speed,
        final_state=x.tolist(),
        n_steps_completed=n_steps_completed,
    )


# =============================================================================
# AGGREGATION / CLASSIFICATION
# =============================================================================

def classify_local_regime(ic_results: Sequence[ICResult]) -> RenormMetrics:
    n_total = len(ic_results)
    bounded_runs = [r for r in ic_results if r.bounded]
    n_bounded = len(bounded_runs)
    bounded_frac = n_bounded / n_total

    if n_bounded == 0 or bounded_frac < MIN_BOUNDED_FRAC:
        return RenormMetrics(
            renorm_every=-1,
            bounded_frac=bounded_frac,
            moving_frac=0.0,
            pos_lyap_frac=0.0,
            mle_mean=None,
            mle_median=None,
            mle_std=None,
            n_bounded=n_bounded,
            n_moving=0,
            n_pos_lyap=0,
            regime_local="UNSTABLE",
        )

    moving_flags = []
    mles = []

    for r in bounded_runs:
        moving = False
        if r.tail_var is not None and r.tail_speed is not None:
            moving = (r.tail_var > VAR_THRESH) and (r.tail_speed > SPEED_THRESH)
        moving_flags.append(moving)

        if r.mle is not None and np.isfinite(r.mle):
            mles.append(r.mle)

    n_moving = int(sum(moving_flags))
    moving_frac = n_moving / n_bounded

    positive = [m for m in mles if m > 0.0]
    n_pos_lyap = len(positive)
    pos_lyap_frac = n_pos_lyap / n_bounded

    mle_mean = float(np.mean(mles)) if mles else None
    mle_median = float(np.median(mles)) if mles else None
    mle_std = float(np.std(mles)) if mles else None

    if moving_frac < 0.30:
        regime = "FIXED"
    elif mle_median is None:
        regime = "OSCILLATORY"
    elif mle_median > MLE_POS_THRESH_STRONG and pos_lyap_frac >= POS_LYAP_STRONG_MIN:
        regime = "CHAOS_STRONG"
    elif mle_median > 0.0 and pos_lyap_frac >= POS_LYAP_WEAK_MIN:
        regime = "CHAOS_WEAK"
    elif abs(mle_median) <= MLE_BORDER_EPS:
        regime = "BORDER"
    else:
        regime = "OSCILLATORY"

    return RenormMetrics(
        renorm_every=-1,
        bounded_frac=bounded_frac,
        moving_frac=moving_frac,
        pos_lyap_frac=pos_lyap_frac,
        mle_mean=mle_mean,
        mle_median=mle_median,
        mle_std=mle_std,
        n_bounded=n_bounded,
        n_moving=n_moving,
        n_pos_lyap=n_pos_lyap,
        regime_local=regime,
    )


def sign3(x: Optional[float]) -> int:
    if x is None or not np.isfinite(x):
        return 0
    if x > MLE_BORDER_EPS:
        return 1
    if x < -MLE_BORDER_EPS:
        return -1
    return 0


def sign_stability(vals: Sequence[Optional[float]]) -> float:
    """
    Returns a normalized instability score in [0,1].
    0.0 = all signs identical across renorm settings
    1.0 = maximal sign disagreement
    """
    signs = [sign3(v) for v in vals]
    pairs = [(signs[i], signs[j]) for i in range(len(signs)) for j in range(i + 1, len(signs))]
    if not pairs:
        return 0.0
    n_diff = sum(1 for a, b in pairs if a != b)
    return n_diff / len(pairs)


def final_class_from_sensitivity(
    metrics_by_k: Dict[int, RenormMetrics]
) -> Tuple[str, bool, bool, Optional[float], float]:
    ref = metrics_by_k[10]

    mle_vals = [
        metrics_by_k[5].mle_median,
        metrics_by_k[10].mle_median,
        metrics_by_k[20].mle_median,
    ]
    finite_vals = [v for v in mle_vals if v is not None and np.isfinite(v)]
    mle_delta = None if not finite_vals else float(max(finite_vals) - min(finite_vals))
    mle_sign_instability = sign_stability(mle_vals)

    all_bounded = all(m.bounded_frac >= 0.99 for m in metrics_by_k.values())
    all_moving = all(m.moving_frac >= 0.99 for m in metrics_by_k.values())

    stable_under_renorm = (
        mle_delta is not None
        and mle_delta <= 0.10
        and mle_sign_instability == 0.0
    )

    # Conservative final classification based on reference + sensitivity
    if not all_bounded:
        cls = "UNSTABLE"
    elif ref.mle_median is None:
        cls = "OSCILLATORY"
    elif ref.mle_median > MLE_POS_THRESH_STRONG and ref.pos_lyap_frac >= POS_LYAP_STRONG_MIN and stable_under_renorm:
        cls = "CHAOS_STRONG"
    elif ref.mle_median > 0.0 and ref.pos_lyap_frac >= POS_LYAP_WEAK_MIN:
        if stable_under_renorm:
            cls = "CHAOS_WEAK"
        else:
            cls = "BORDER"
    elif abs(ref.mle_median) <= MLE_BORDER_EPS:
        cls = "BORDER"
    else:
        cls = "OSCILLATORY"

    return cls, all_bounded, all_moving, mle_delta, mle_sign_instability


# =============================================================================
# v3.3 CORE
# =============================================================================

def run_case_all_renorm(
    W: np.ndarray,
    sigma: float,
    rho: float,
    beta: float,
) -> Dict[int, RenormMetrics]:
    out: Dict[int, RenormMetrics] = {}
    for k in RENORM_GRID:
        ic_results = [
            integrate_one_ic(W, sigma, rho, beta, renorm_every=k)
            for _ in range(N_IC)
        ]
        metrics = classify_local_regime(ic_results)
        metrics.renorm_every = k
        out[k] = metrics
    return out


def run_v3_3() -> List[BoundaryCaseResult]:
    topologies = gen_dense_topologies()

    W0 = topologies[ANCHOR["topo_idx"]]
    W = permute_topology(W0, ANCHOR["perm"])

    topo_lbl = topo_label(W0)
    perm_lbl = topo_label(W)
    eff_sig = effective_signature(W)

    total_cases = len(SIGMA_VALS) * len(RHO_VALS) * len(BETA_VALS)

    print("=" * 88)
    print("TRIDOM — v3.3")
    print("Boundary study around C2a")
    print("=" * 88)
    print(f"Anchor      : {ANCHOR['name']}")
    print(f"Grid        : {len(SIGMA_VALS)} × {len(RHO_VALS)} × {len(BETA_VALS)} = {total_cases}")
    print(f"IC per point: {N_IC}")
    print(f"RENORM grid : {RENORM_GRID}")
    print()

    print(
        f"{'sigma':>6} {'rho':>8} {'beta':>7} {'class':>14} "
        f"{'mle_r10':>10} {'Δmle':>8} {'sign_inst':>10} {'bnd':>5} {'mov':>5}"
    )
    print("-" * 88)

    results: List[BoundaryCaseResult] = []

    for sigma in SIGMA_VALS:
        for rho in RHO_VALS:
            for beta in BETA_VALS:
                metrics_by_k = run_case_all_renorm(W, float(sigma), float(rho), float(beta))
                cls, all_bounded, all_moving, mle_delta, mle_sign_instability = final_class_from_sensitivity(metrics_by_k)

                ref = metrics_by_k[10]

                row = BoundaryCaseResult(
                    anchor=ANCHOR["name"],
                    topo_idx=ANCHOR["topo_idx"],
                    perm=ANCHOR["perm"],
                    topo_label=topo_lbl,
                    perm_label=perm_lbl,
                    effective_signature=eff_sig,
                    sigma=float(sigma),
                    rho=float(rho),
                    beta=float(beta),
                    bounded_frac_ref=float(ref.bounded_frac),
                    moving_frac_ref=float(ref.moving_frac),
                    pos_lyap_frac_ref=float(ref.pos_lyap_frac),
                    mle_mean_ref=None if ref.mle_mean is None or not np.isfinite(ref.mle_mean) else float(ref.mle_mean),
                    mle_median_ref=None if ref.mle_median is None or not np.isfinite(ref.mle_median) else float(ref.mle_median),
                    mle_std_ref=None if ref.mle_std is None or not np.isfinite(ref.mle_std) else float(ref.mle_std),
                    mle_median_r5=None if metrics_by_k[5].mle_median is None else float(metrics_by_k[5].mle_median),
                    mle_median_r10=None if metrics_by_k[10].mle_median is None else float(metrics_by_k[10].mle_median),
                    mle_median_r20=None if metrics_by_k[20].mle_median is None else float(metrics_by_k[20].mle_median),
                    mle_delta=None if mle_delta is None or not np.isfinite(mle_delta) else float(mle_delta),
                    mle_sign_stability=float(mle_sign_instability),
                    class_v3_3=cls,
                    all_bounded=bool(all_bounded),
                    all_moving=bool(all_moving),
                    stable_under_renorm=bool(
                        mle_delta is not None and np.isfinite(mle_delta) and mle_delta <= 0.10 and mle_sign_instability == 0.0
                    ),
                )
                results.append(row)

                mle_r10_str = "nan" if row.mle_median_r10 is None else f"{row.mle_median_r10:10.4f}"
                mle_delta_str = "nan" if row.mle_delta is None else f"{row.mle_delta:8.4f}"
                print(
                    f"{row.sigma:6.2f} {row.rho:8.2f} {row.beta:7.3f} {row.class_v3_3:>14} "
                    f"{mle_r10_str:>10} {mle_delta_str:>8} {row.mle_sign_stability:10.3f} "
                    f"{row.bounded_frac_ref:5.2f} {row.moving_frac_ref:5.2f}"
                )

    return results


# =============================================================================
# SUMMARY
# =============================================================================

def summarize(results: Sequence[BoundaryCaseResult]) -> None:
    print("\n" + "=" * 88)
    print("SUMMARY v3.3")
    print("=" * 88)

    classes = ["CHAOS_STRONG", "CHAOS_WEAK", "BORDER", "OSCILLATORY", "UNSTABLE"]
    counts = {c: sum(1 for r in results if r.class_v3_3 == c) for c in classes}

    for c in classes:
        print(f"{c:>14}: {counts[c]:4d} / {len(results)}")

    sortable = [r for r in results if r.mle_median_ref is not None]
    sortable.sort(key=lambda r: r.mle_median_ref, reverse=True)

    print("\nTop 10 mle_median_ref:")
    for r in sortable[:10]:
        print(
            f"  sigma={r.sigma:.2f} rho={r.rho:.2f} beta={r.beta:.3f} "
            f"| class={r.class_v3_3} | mle_r10={r.mle_median_ref:.4f} "
            f"| Δmle={0.0 if r.mle_delta is None else r.mle_delta:.4f} "
            f"| sign_inst={r.mle_sign_stability:.3f}"
        )

    borders = [r for r in results if r.class_v3_3 == "BORDER"]
    if borders:
        print("\nBoundary candidates:")
        for r in borders[:20]:
            print(
                f"  sigma={r.sigma:.2f} rho={r.rho:.2f} beta={r.beta:.3f} "
                f"| mle_r10={r.mle_median_ref:.4f} | Δmle={0.0 if r.mle_delta is None else r.mle_delta:.4f} "
                f"| sign_inst={r.mle_sign_stability:.3f}"
            )


# =============================================================================
# SAVE
# =============================================================================

def save_json(results: Sequence[BoundaryCaseResult], path: Path) -> None:
    payload = {
        "meta": {
            "seed": SEED,
            "anchor": ANCHOR,
            "sigma_vals": list(map(float, SIGMA_VALS)),
            "rho_vals": list(map(float, RHO_VALS)),
            "beta_vals": list(map(float, BETA_VALS)),
            "n_ic": N_IC,
            "dt": DT,
            "burn_steps": BURN_STEPS,
            "measure_steps": MEASURE_STEPS,
            "tail_steps": TAIL_STEPS,
            "renorm_grid": RENORM_GRID,
            "mle_init_norm": MLE_INIT_NORM,
            "mle_pos_thresh_strong": MLE_POS_THRESH_STRONG,
            "mle_border_eps": MLE_BORDER_EPS,
        },
        "results": [asdict(r) for r in results],
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def save_csv(results: Sequence[BoundaryCaseResult], path: Path) -> None:
    if not results:
        return
    fieldnames = list(asdict(results[0]).keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))


# =============================================================================
# PLOTS
# =============================================================================

CLASS_TO_INT = {
    "UNSTABLE": 0,
    "OSCILLATORY": 1,
    "BORDER": 2,
    "CHAOS_WEAK": 3,
    "CHAOS_STRONG": 4,
}
INT_TO_CLASS = {v: k for k, v in CLASS_TO_INT.items()}


def plot_mle_vs_rho(results: Sequence[BoundaryCaseResult], out_path: Path) -> None:
    subset = [
        r for r in results
        if abs(r.sigma - SIGMA_CUT) < 1e-9 and abs(r.beta - BETA_CUT) < 1e-9 and r.mle_median_ref is not None
    ]
    subset.sort(key=lambda r: r.rho)

    if not subset:
        print(f"[warn] No data for mle-vs-rho cut at sigma={SIGMA_CUT}, beta={BETA_CUT}")
        return

    xs = [r.rho for r in subset]
    ys = [r.mle_median_ref for r in subset]

    plt.figure(figsize=(8, 4.5))
    plt.plot(xs, ys, marker="o")
    plt.axhline(0.0, linewidth=1.0)
    plt.axhline(MLE_POS_THRESH_STRONG, linewidth=1.0, linestyle="--")
    plt.xlabel("rho")
    plt.ylabel("MLE median (renorm=10)")
    plt.title(f"C2a boundary cut — sigma={SIGMA_CUT:.2f}, beta={BETA_CUT:.3f}")
    plt.tight_layout()
    plt.savefig(out_path, dpi=FIG_DPI)
    plt.close()


def build_heatmap_arrays(
    results: Sequence[BoundaryCaseResult],
    sigma_fixed: float,
) -> Tuple[np.ndarray, np.ndarray]:
    rho_to_idx = {float(v): i for i, v in enumerate(RHO_VALS)}
    beta_to_idx = {float(v): j for j, v in enumerate(BETA_VALS)}

    mle_arr = np.full((len(BETA_VALS), len(RHO_VALS)), np.nan, dtype=float)
    cls_arr = np.full((len(BETA_VALS), len(RHO_VALS)), np.nan, dtype=float)

    for r in results:
        if abs(r.sigma - sigma_fixed) > 1e-9:
            continue
        i = beta_to_idx[float(r.beta)]
        j = rho_to_idx[float(r.rho)]
        if r.mle_median_ref is not None:
            mle_arr[i, j] = r.mle_median_ref
        cls_arr[i, j] = CLASS_TO_INT[r.class_v3_3]

    return mle_arr, cls_arr


def plot_heatmap_mle(results: Sequence[BoundaryCaseResult], out_path: Path) -> None:
    mle_arr, _ = build_heatmap_arrays(results, SIGMA_HEATMAP)

    plt.figure(figsize=(9, 4.8))
    plt.imshow(
        mle_arr,
        origin="lower",
        aspect="auto",
        extent=[RHO_VALS[0], RHO_VALS[-1], BETA_VALS[0], BETA_VALS[-1]],
    )
    plt.colorbar(label="MLE median (renorm=10)")
    plt.xlabel("rho")
    plt.ylabel("beta")
    plt.title(f"C2a heatmap — MLE median at sigma={SIGMA_HEATMAP:.2f}")
    plt.tight_layout()
    plt.savefig(out_path, dpi=FIG_DPI)
    plt.close()


def plot_heatmap_class(results: Sequence[BoundaryCaseResult], out_path: Path) -> None:
    _, cls_arr = build_heatmap_arrays(results, SIGMA_HEATMAP)

    plt.figure(figsize=(9, 4.8))
    plt.imshow(
        cls_arr,
        origin="lower",
        aspect="auto",
        extent=[RHO_VALS[0], RHO_VALS[-1], BETA_VALS[0], BETA_VALS[-1]],
        vmin=0,
        vmax=4,
    )
    cb = plt.colorbar(label="class_v3_3")
    cb.set_ticks([0, 1, 2, 3, 4])
    cb.set_ticklabels([INT_TO_CLASS[i] for i in range(5)])
    plt.xlabel("rho")
    plt.ylabel("beta")
    plt.title(f"C2a heatmap — class_v3_3 at sigma={SIGMA_HEATMAP:.2f}")
    plt.tight_layout()
    plt.savefig(out_path, dpi=FIG_DPI)
    plt.close()


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    out_dir = Path(__file__).parent

    csv_path = out_dir / "tridom_v3_3_boundary_results.csv"
    json_path = out_dir / "tridom_v3_3_boundary_results.json"
    fig_cut_path = out_dir / "tridom_v3_3_cut_mle_vs_rho.png"
    fig_heatmap_mle_path = out_dir / "tridom_v3_3_heatmap_mle.png"
    fig_heatmap_class_path = out_dir / "tridom_v3_3_heatmap_class.png"

    results = run_v3_3()
    summarize(results)
    save_json(results, json_path)
    save_csv(results, csv_path)
    plot_mle_vs_rho(results, fig_cut_path)
    plot_heatmap_mle(results, fig_heatmap_mle_path)
    plot_heatmap_class(results, fig_heatmap_class_path)

    print("\n" + "=" * 88)
    print("FILES")
    print("=" * 88)
    print(f"CSV  → {csv_path}")
    print(f"JSON → {json_path}")
    print(f"FIG CUT → {fig_cut_path}")
    print(f"FIG MLE → {fig_heatmap_mle_path}")
    print(f"FIG CLASS → {fig_heatmap_class_path}")
    print("\nv3.3 completed.")


if __name__ == "__main__":
    main()
