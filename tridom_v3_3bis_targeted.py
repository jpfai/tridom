#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TRIDOM — v3.3bis-targeted
Multi-nucleus boundary refinement around C2a

Goal
----
Refine the critical region detected in v3.3 using 7 nuclei:
- 1 barycentric nucleus (center of mass of B)
- 6 signed nuclei (points with mle < 0 in v3.3)

This script:
- scans a local grid around each nucleus
- estimates MLE with Benettin / variational equation
- tests RENORM sensitivity in a configurable grid
- classifies each point into:
    * CHAOS_STRONG
    * CHAOS_WEAK
    * BORDER
    * OSCILLATORY
    * UNSTABLE
- extracts local A/B/C sets
- saves CSV + JSON per nucleus
- saves a global comparative summary
- generates 3 figures per nucleus:
    * heatmap MLE
    * heatmap class
    * 1D cut mle vs rho

Epistemic status
----------------
Numerical boundary refinement only.
This is NOT an analytical proof of chaos.

Usage
-----
# Fast local run
python3 tridom_v3_3bis_targeted.py --mode local

# Stronger VPS/publication-grade run
python3 tridom_v3_3bis_targeted.py --mode vps

# Run one nucleus only
python3 tridom_v3_3bis_targeted.py --mode vps --nuclei NEG5

# Run a selected subset in the order requested
python3 tridom_v3_3bis_targeted.py --mode vps --nuclei NEG5,NEG1,NEG3

Outputs
-------
For each nucleus X:
- tridom_v3_3bis_targeted_<X>_results.csv
- tridom_v3_3bis_targeted_<X>_results.json
- tridom_v3_3bis_targeted_<X>_heatmap_mle.png
- tridom_v3_3bis_targeted_<X>_heatmap_class.png
- tridom_v3_3bis_targeted_<X>_cut_mle_vs_rho.png

Global:
- tridom_v3_3bis_targeted_summary.json
- tridom_v3_3bis_targeted_summary.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from dataclasses import asdict, dataclass
from itertools import product
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# =============================================================================
# GLOBAL CONFIG
# =============================================================================

SEED = 42
ARCS: List[Tuple[int, int]] = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]

ANCHOR = {
    "name": "C2a",
    "topo_idx": 41,
    "perm": (0, 1, 2),
    "sigma": 10.0,
    "rho": 99.6,
    "beta": 8.0 / 3.0,
}

NUCLEI = [
    {"id": "BARY", "sigma": 10.3533, "rho": 100.2609, "beta": 2.6821, "kind": "barycenter"},
    {"id": "NEG1", "sigma": 9.75,   "rho":  97.5,    "beta": 2.625,  "kind": "negative"},
    {"id": "NEG2", "sigma": 10.25,  "rho": 102.5,    "beta": 2.700,  "kind": "negative"},
    {"id": "NEG3", "sigma": 10.25,  "rho": 105.0,    "beta": 2.625,  "kind": "negative"},
    {"id": "NEG4", "sigma": 9.75,   "rho":  99.5,    "beta": 2.550,  "kind": "negative"},
    {"id": "NEG5", "sigma": 10.25,  "rho": 102.0,    "beta": 2.400,  "kind": "negative"},
    {"id": "NEG6", "sigma": 10.50,  "rho": 104.0,    "beta": 2.775,  "kind": "negative"},
]

# Deterministic per-nucleus seed offsets to guarantee reproducibility across
# separate Python processes. Do not use hash(nucleus_id), which is randomized
# by Python between processes.
NUCLEUS_SEED_OFFSET = {
    "BARY": 100_000,
    "NEG1": 200_000,
    "NEG2": 300_000,
    "NEG3": 400_000,
    "NEG4": 500_000,
    "NEG5": 600_000,
    "NEG6": 700_000,
}

DT = 0.0025
MLE_INIT_NORM = 1e-8
BLOW_THRESH = 1e4
FINITE_EPS = 1e-15

VAR_THRESH = 1e-4
SPEED_THRESH = 1e-3
MIN_BOUNDED_FRAC = 0.50

MLE_POS_THRESH_STRONG = 0.10
MLE_BORDER_EPS = 0.05
POS_LYAP_STRONG_MIN = 0.80
POS_LYAP_WEAK_MIN = 0.50

FIG_DPI = 140

CLASS_TO_INT = {
    "UNSTABLE": 0,
    "OSCILLATORY": 1,
    "BORDER": 2,
    "CHAOS_WEAK": 3,
    "CHAOS_STRONG": 4,
}
INT_TO_CLASS = {v: k for k, v in CLASS_TO_INT.items()}

SCRIPT_STEM = "tridom_v3_3bis_targeted"
DISPLAY_VERSION = "TRIDOM — v3.3bis-targeted"


# =============================================================================
# MODES
# =============================================================================

MODES = {
    "local": {
        "sigma_offsets": np.array([-0.25, 0.00, 0.25], dtype=float),
        "rho_offsets": np.array([-1.0, -0.5, 0.0, 0.5, 1.0], dtype=float),
        "beta_offsets": np.array([-0.10, 0.00, 0.10], dtype=float),
        "n_ic": 4,
        "burn_steps": 1500,
        "measure_steps": 4000,
        "tail_steps": 800,
        "renorm_grid": [5, 10, 20],
        "description": "fast local refinement",
    },
    "vps": {
        "sigma_offsets": np.array([-0.40, -0.20, 0.00, 0.20, 0.40], dtype=float),
        "rho_offsets": np.array([-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5], dtype=float),
        "beta_offsets": np.array([-0.15, -0.075, 0.00, 0.075, 0.15], dtype=float),
        "n_ic": 8,
        "burn_steps": 2500,
        "measure_steps": 6000,
        "tail_steps": 1200,
        "renorm_grid": [5, 10, 20],
        "description": "stronger refinement",
    },
}


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
    nucleus_id: str
    nucleus_kind: str
    center_sigma: float
    center_rho: float
    center_beta: float

    anchor: str
    topo_idx: int
    perm: Tuple[int, int, int]
    topo_label: str
    perm_label: str
    effective_signature: str
    source_mode: str
    point_id: Optional[str]
    patch_label: Optional[str]
    patch_source: Optional[str]
    center_nucleus_label: Optional[str]

    sigma: float
    rho: float
    beta: float

    bounded_frac_ref: float
    moving_frac_ref: float
    pos_lyap_frac_ref: float
    mle_mean_ref: Optional[float]
    mle_median_ref: Optional[float]
    mle_std_ref: Optional[float]

    mle_median_r5: Optional[float]
    mle_median_r10: Optional[float]
    mle_median_r20: Optional[float]

    mle_delta: Optional[float]
    mle_sign_stability: float
    class_v3_3bis: str

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
    x: np.ndarray, v: np.ndarray,
    W: np.ndarray, sigma: float, rho: float, beta: float,
) -> Tuple[np.ndarray, np.ndarray]:
    return rhs(x, W, sigma, rho, beta), jacobian(x, W, sigma, rho, beta) @ v


def rk4_state_tangent_step(
    x: np.ndarray, v: np.ndarray,
    W: np.ndarray, sigma: float, rho: float, beta: float, dt: float,
) -> Tuple[np.ndarray, np.ndarray]:
    k1x, k1v = state_tangent_rhs(x, v, W, sigma, rho, beta)
    k2x, k2v = state_tangent_rhs(x + 0.5 * dt * k1x, v + 0.5 * dt * k1v, W, sigma, rho, beta)
    k3x, k3v = state_tangent_rhs(x + 0.5 * dt * k2x, v + 0.5 * dt * k2v, W, sigma, rho, beta)
    k4x, k4v = state_tangent_rhs(x + dt * k3x, v + dt * k3v, W, sigma, rho, beta)
    x_new = x + (dt / 6.0) * (k1x + 2 * k2x + 2 * k3x + k4x)
    v_new = v + (dt / 6.0) * (k1v + 2 * k2v + 2 * k3v + k4v)
    return x_new, v_new


def is_valid_state(x: np.ndarray) -> bool:
    return np.all(np.isfinite(x)) and np.max(np.abs(x)) <= BLOW_THRESH


# =============================================================================
# TRAJECTORY NUMERICS
# =============================================================================

def make_rng(seed_offset: int) -> np.random.Generator:
    return np.random.default_rng(SEED + seed_offset)


def random_initial_condition(rho: float, rng: np.random.Generator) -> np.ndarray:
    center = np.array([1.0, 1.0, max(1.0, 0.5 * rho)], dtype=float)
    return center + rng.normal(0.0, 1.0, size=3)


def integrate_one_ic(
    W: np.ndarray, sigma: float, rho: float, beta: float,
    renorm_every: int, burn_steps: int, total_steps: int,
    tail_steps: int, rng: np.random.Generator,
) -> ICResult:
    x = random_initial_condition(rho, rng)
    v = rng.normal(0.0, 1.0, size=3)
    nv = np.linalg.norm(v)
    v = (v / nv if nv >= FINITE_EPS else np.array([1.0, 0.0, 0.0])) * MLE_INIT_NORM

    tail_states: List[np.ndarray] = []
    log_sum = 0.0
    renorm_count = 0
    bounded = True
    blowup = False
    nonfinite = False
    n_steps_completed = 0

    for step in range(total_steps):
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
            if step >= burn_steps:
                log_sum += math.log(norm_v / MLE_INIT_NORM)
                renorm_count += 1
            v = (v / norm_v) * MLE_INIT_NORM

        if step >= total_steps - tail_steps:
            tail_states.append(x.copy())

    if not bounded:
        return ICResult(False, blowup, nonfinite, None, None, None, None, n_steps_completed)

    tail = np.asarray(tail_states, dtype=float)
    if len(tail) < 5:
        return ICResult(False, True, False, None, None, None, x.tolist(), n_steps_completed)

    diffs = np.diff(tail, axis=0)
    tail_var = float(np.mean(np.var(tail, axis=0)))
    tail_speed = float(np.mean(np.linalg.norm(diffs, axis=1)))
    mle = None if renorm_count == 0 else float(log_sum / (renorm_count * renorm_every * DT))

    return ICResult(True, False, False, mle, tail_var, tail_speed, x.tolist(), n_steps_completed)


# =============================================================================
# CLASSIFICATION
# =============================================================================

def classify_local_regime(ic_results: Sequence[ICResult]) -> RenormMetrics:
    n_total = len(ic_results)
    bounded_runs = [r for r in ic_results if r.bounded]
    n_bounded = len(bounded_runs)
    bounded_frac = n_bounded / n_total

    if n_bounded == 0 or bounded_frac < MIN_BOUNDED_FRAC:
        return RenormMetrics(-1, bounded_frac, 0.0, 0.0, None, None, None, n_bounded, 0, 0, "UNSTABLE")

    moving_flags = []
    mles = []
    for r in bounded_runs:
        moving = (
            r.tail_var is not None
            and r.tail_speed is not None
            and r.tail_var > VAR_THRESH
            and r.tail_speed > SPEED_THRESH
        )
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
        -1, bounded_frac, moving_frac, pos_lyap_frac,
        mle_mean, mle_median, mle_std, n_bounded, n_moving, n_pos_lyap, regime
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
    signs = [sign3(v) for v in vals]
    pairs = [(signs[i], signs[j]) for i in range(len(signs)) for j in range(i + 1, len(signs))]
    if not pairs:
        return 0.0
    return sum(1 for a, b in pairs if a != b) / len(pairs)


_DEAD = RenormMetrics(-1, 0, 0, 0, None, None, None, 0, 0, 0, "UNSTABLE")


def final_class_from_sensitivity(
    metrics_by_k: Dict[int, RenormMetrics]
) -> Tuple[str, bool, bool, Optional[float], float]:
    ref = metrics_by_k[10]

    mle_vals = [
        metrics_by_k.get(5, _DEAD).mle_median,
        metrics_by_k.get(10, _DEAD).mle_median,
        metrics_by_k.get(20, _DEAD).mle_median,
    ]
    finite_vals = [v for v in mle_vals if v is not None and np.isfinite(v)]
    mle_delta = None if not finite_vals else float(max(finite_vals) - min(finite_vals))
    mle_sign_instability = sign_stability(mle_vals)

    all_bounded = all(m.bounded_frac >= 0.99 for m in metrics_by_k.values())
    all_moving = all(m.moving_frac >= 0.99 for m in metrics_by_k.values())
    stable = (mle_delta is not None and mle_delta <= 0.10 and mle_sign_instability == 0.0)

    if not all_bounded:
        cls = "UNSTABLE"
    elif ref.mle_median is None:
        cls = "OSCILLATORY"
    elif ref.mle_median > MLE_POS_THRESH_STRONG and ref.pos_lyap_frac >= POS_LYAP_STRONG_MIN and stable:
        cls = "CHAOS_STRONG"
    elif ref.mle_median > 0.0 and ref.pos_lyap_frac >= POS_LYAP_WEAK_MIN:
        cls = "CHAOS_WEAK" if stable else "BORDER"
    elif abs(ref.mle_median) <= MLE_BORDER_EPS:
        cls = "BORDER"
    else:
        cls = "OSCILLATORY"

    return cls, all_bounded, all_moving, mle_delta, mle_sign_instability


# =============================================================================
# CORE
# =============================================================================

def build_local_grid(nucleus: Dict, cfg: Dict) -> List[Tuple[float, float, float]]:
    out = []
    for ds in cfg["sigma_offsets"]:
        for dr in cfg["rho_offsets"]:
            for db in cfg["beta_offsets"]:
                out.append((
                    float(nucleus["sigma"] + ds),
                    float(nucleus["rho"] + dr),
                    float(nucleus["beta"] + db),
                ))
    return out


def load_explicit_points_csv(path: str) -> List[Dict]:
    required = {"sigma", "rho", "beta"}
    points: List[Dict] = []

    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        missing = sorted(required - set(fieldnames))
        if missing:
            raise ValueError(
                f"--points-csv missing required columns: {missing}. "
                f"Available columns: {fieldnames}"
            )

        def _opt_float(row: Dict, key: str) -> Optional[float]:
            raw = row.get(key, "")
            if raw is None:
                return None
            raw = str(raw).strip()
            if raw == "":
                return None
            return float(raw)

        for i, row in enumerate(reader, start=1):
            try:
                sigma = float(row["sigma"])
                rho = float(row["rho"])
                beta = float(row["beta"])
            except Exception as exc:
                raise ValueError(
                    f"Invalid numeric values in --points-csv at row {i}: {exc}"
                ) from exc

            points.append({
                "point_id": (row.get("point_id") or f"P{i:04d}").strip(),
                "patch_label": (row.get("patch_label") or "").strip() or None,
                "patch_source": (row.get("patch_source") or "").strip() or None,
                "center_sigma": _opt_float(row, "center_sigma"),
                "center_rho": _opt_float(row, "center_rho"),
                "center_beta": _opt_float(row, "center_beta"),
                "center_nucleus": (row.get("center_nucleus") or "").strip() or None,
                "sigma": sigma,
                "rho": rho,
                "beta": beta,
            })

    if not points:
        raise ValueError("--points-csv contains no rows")

    return points


def build_targeted_pseudo_nucleus(points: Sequence[Dict]) -> Dict:
    return {
        "id": "CSV_TARGETED",
        "sigma": float(np.mean([p["sigma"] for p in points])),
        "rho": float(np.mean([p["rho"] for p in points])),
        "beta": float(np.mean([p["beta"] for p in points])),
        "kind": "targeted_csv",
    }


def run_case_all_renorm(
    W: np.ndarray, sigma: float, rho: float, beta: float,
    cfg: Dict, case_seed_base: int,
) -> Dict[int, RenormMetrics]:
    burn_steps = cfg["burn_steps"]
    total_steps = cfg["burn_steps"] + cfg["measure_steps"]
    tail_steps = cfg["tail_steps"]
    n_ic = cfg["n_ic"]
    out: Dict[int, RenormMetrics] = {}

    for rk_idx, renorm_every in enumerate(cfg["renorm_grid"]):
        ic_results = []
        for ic_idx in range(n_ic):
            rng = make_rng(case_seed_base + 1000 * rk_idx + ic_idx)
            ic_results.append(integrate_one_ic(
                W=W, sigma=sigma, rho=rho, beta=beta,
                renorm_every=renorm_every, burn_steps=burn_steps,
                total_steps=total_steps, tail_steps=tail_steps, rng=rng,
            ))
        metrics = classify_local_regime(ic_results)
        metrics.renorm_every = renorm_every
        out[renorm_every] = metrics
    return out


def run_one_nucleus(
    nucleus: Dict, cfg: Dict, W: np.ndarray,
    topo_lbl: str, perm_lbl: str, eff_sig: str,
    explicit_points: Optional[Sequence[Dict]] = None,
) -> List[BoundaryCaseResult]:
    if explicit_points is None:
        point_rows = [
            {"sigma": s, "rho": r, "beta": b}
            for (s, r, b) in build_local_grid(nucleus, cfg)
        ]
        total = len(point_rows)

        print("\n" + "=" * 96)
        print(f"NUCLEUS {nucleus['id']} ({nucleus['kind']})")
        print(f"center = ({nucleus['sigma']:.4f}, {nucleus['rho']:.4f}, {nucleus['beta']:.4f})")
        print(
            f"grid = {len(cfg['sigma_offsets'])} × {len(cfg['rho_offsets'])} × "
            f"{len(cfg['beta_offsets'])} = {total}"
        )
        print("=" * 96)
    else:
        point_rows = list(explicit_points)
        total = len(point_rows)

        print("\n" + "=" * 96)
        print(f"NUCLEUS {nucleus['id']} ({nucleus['kind']})")
        print("targeted points CSV mode")
        print(f"points = {total}")
        print(f"global center ≈ ({nucleus['sigma']:.4f}, {nucleus['rho']:.4f}, {nucleus['beta']:.4f})")
        print("=" * 96)
    print(f"{'#':>4} {'sigma':>7} {'rho':>8} {'beta':>7} {'class':>14} "
          f"{'mle_r10':>10} {'Δmle':>8} {'sign':>7} {'bnd':>5} {'mov':>5}")
    print("-" * 96)

    results: List[BoundaryCaseResult] = []
    t0 = time.perf_counter()
    nucleus_seed_offset = NUCLEUS_SEED_OFFSET.get(nucleus["id"], 800_000)

    for idx, prow in enumerate(point_rows, start=1):
        sigma = float(prow["sigma"])
        rho = float(prow["rho"])
        beta = float(prow["beta"])
        metrics_by_k = run_case_all_renorm(
            W=W,
            sigma=sigma,
            rho=rho,
            beta=beta,
            cfg=cfg,
            case_seed_base=10_000_000 + nucleus_seed_offset + idx,
        )
        cls, all_bounded, all_moving, mle_delta, mle_sign_instability = final_class_from_sensitivity(metrics_by_k)
        ref = metrics_by_k[10]

        row_center_sigma = (
            float(prow["center_sigma"])
            if explicit_points is not None and prow.get("center_sigma") is not None
            else float(nucleus["sigma"])
        )
        row_center_rho = (
            float(prow["center_rho"])
            if explicit_points is not None and prow.get("center_rho") is not None
            else float(nucleus["rho"])
        )
        row_center_beta = (
            float(prow["center_beta"])
            if explicit_points is not None and prow.get("center_beta") is not None
            else float(nucleus["beta"])
        )

        row = BoundaryCaseResult(
            nucleus_id=nucleus["id"],
            nucleus_kind=nucleus["kind"],
            center_sigma=row_center_sigma,
            center_rho=row_center_rho,
            center_beta=row_center_beta,
            anchor=ANCHOR["name"],
            topo_idx=ANCHOR["topo_idx"],
            perm=ANCHOR["perm"],
            topo_label=topo_lbl,
            perm_label=perm_lbl,
            effective_signature=eff_sig,
            source_mode="points_csv" if explicit_points is not None else "grid",
            point_id=None if explicit_points is None else prow.get("point_id"),
            patch_label=None if explicit_points is None else prow.get("patch_label"),
            patch_source=None if explicit_points is None else prow.get("patch_source"),
            center_nucleus_label=None if explicit_points is None else prow.get("center_nucleus"),
            sigma=sigma,
            rho=rho,
            beta=beta,
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
            class_v3_3bis=cls,
            all_bounded=bool(all_bounded),
            all_moving=bool(all_moving),
            stable_under_renorm=bool(
                mle_delta is not None and np.isfinite(mle_delta)
                and mle_delta <= 0.10 and mle_sign_instability == 0.0
            ),
        )
        results.append(row)

        mle_s = "nan" if row.mle_median_r10 is None else f"{row.mle_median_r10:10.4f}"
        d_s = "nan" if row.mle_delta is None else f"{row.mle_delta:8.4f}"
        elapsed = time.perf_counter() - t0
        eta = elapsed / idx * (total - idx) if idx > 0 else 0.0
        print(
            f"{idx:>4} {sigma:7.3f} {rho:8.3f} {beta:7.3f} {cls:>14} "
            f"{mle_s:>10} {d_s:>8} {row.mle_sign_stability:7.3f} "
            f"{row.bounded_frac_ref:5.2f} {row.moving_frac_ref:5.2f}  ETA {eta/60:.1f}min"
        )

    return results


# =============================================================================
# LOCAL A/B/C EXTRACTION
# =============================================================================

def extract_abc(
    rows: Sequence[BoundaryCaseResult],
) -> Tuple[List[BoundaryCaseResult], List[BoundaryCaseResult], List[BoundaryCaseResult]]:
    A = [r for r in rows if r.mle_sign_stability > 0.0]
    B = [
        r for r in rows
        if r.mle_sign_stability > 0.0
        and r.mle_median_ref is not None
        and abs(r.mle_median_ref) <= MLE_BORDER_EPS
    ]
    C = [
        r for r in rows
        if r.mle_sign_stability == 0.0
        and r.mle_delta is not None
        and r.mle_delta > 0.10
    ]
    return A, B, C


# =============================================================================
# SAVE
# =============================================================================

def save_json(rows: Sequence[BoundaryCaseResult], meta: Dict, path: Path) -> None:
    payload = {"meta": meta, "results": [asdict(r) for r in rows]}
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def save_csv(rows: Sequence[BoundaryCaseResult], path: Path) -> None:
    if not rows:
        return
    fieldnames = list(asdict(rows[0]).keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(asdict(r))


def save_summary_csv(summary_rows: List[Dict], path: Path) -> None:
    if not summary_rows:
        return
    fieldnames = list(summary_rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)


# =============================================================================
# PLOTS
# =============================================================================

def build_axes_for_nucleus(nucleus: Dict, cfg: Dict) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray(nucleus["sigma"] + cfg["sigma_offsets"], dtype=float),
        np.asarray(nucleus["rho"] + cfg["rho_offsets"], dtype=float),
        np.asarray(nucleus["beta"] + cfg["beta_offsets"], dtype=float),
    )


def build_heatmap_arrays(
    rows: Sequence[BoundaryCaseResult], sigma_fixed: float,
    rho_vals: np.ndarray, beta_vals: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    rho_to_idx = {float(v): i for i, v in enumerate(rho_vals)}
    beta_to_idx = {float(v): j for j, v in enumerate(beta_vals)}
    mle_arr = np.full((len(beta_vals), len(rho_vals)), np.nan, dtype=float)
    cls_arr = np.full((len(beta_vals), len(rho_vals)), np.nan, dtype=float)
    for r in rows:
        if abs(r.sigma - sigma_fixed) > 1e-9:
            continue
        i = beta_to_idx.get(float(r.beta))
        j = rho_to_idx.get(float(r.rho))
        if i is None or j is None:
            continue
        if r.mle_median_ref is not None:
            mle_arr[i, j] = r.mle_median_ref
        cls_arr[i, j] = CLASS_TO_INT[r.class_v3_3bis]
    return mle_arr, cls_arr


def plot_nucleus(nucleus: Dict, cfg: Dict, rows: Sequence[BoundaryCaseResult], out_dir: Path) -> None:
    sigma_vals, rho_vals, beta_vals = build_axes_for_nucleus(nucleus, cfg)
    sigma_heatmap = float(sigma_vals[len(sigma_vals) // 2])
    beta_cut = float(beta_vals[len(beta_vals) // 2])
    mle_arr, cls_arr = build_heatmap_arrays(rows, sigma_heatmap, rho_vals, beta_vals)

    plt.figure(figsize=(9, 4.8))
    plt.imshow(
        mle_arr,
        origin="lower",
        aspect="auto",
        extent=[rho_vals[0], rho_vals[-1], beta_vals[0], beta_vals[-1]],
    )
    plt.colorbar(label="MLE median (renorm=10)")
    plt.xlabel("rho")
    plt.ylabel("beta")
    plt.title(f"{nucleus['id']} — MLE heatmap at sigma={sigma_heatmap:.4f}")
    plt.tight_layout()
    plt.savefig(out_dir / f"{SCRIPT_STEM}_{nucleus['id']}_heatmap_mle.png", dpi=FIG_DPI)
    plt.close()

    plt.figure(figsize=(9, 4.8))
    plt.imshow(
        cls_arr,
        origin="lower",
        aspect="auto",
        extent=[rho_vals[0], rho_vals[-1], beta_vals[0], beta_vals[-1]],
        vmin=0,
        vmax=4,
    )
    cb = plt.colorbar(label="class_v3_3bis")
    cb.set_ticks([0, 1, 2, 3, 4])
    cb.set_ticklabels([INT_TO_CLASS[i] for i in range(5)])
    plt.xlabel("rho")
    plt.ylabel("beta")
    plt.title(f"{nucleus['id']} — Class heatmap at sigma={sigma_heatmap:.4f}")
    plt.tight_layout()
    plt.savefig(out_dir / f"{SCRIPT_STEM}_{nucleus['id']}_heatmap_class.png", dpi=FIG_DPI)
    plt.close()

    subset = [
        r for r in rows
        if abs(r.sigma - sigma_heatmap) < 1e-9
        and abs(r.beta - beta_cut) < 1e-9
        and r.mle_median_ref is not None
    ]
    subset.sort(key=lambda r: r.rho)
    if subset:
        xs = [r.rho for r in subset]
        ys = [r.mle_median_ref for r in subset]
        plt.figure(figsize=(8, 4.5))
        plt.plot(xs, ys, marker="o")
        plt.axhline(0.0, linewidth=1.0)
        plt.axhline(MLE_POS_THRESH_STRONG, linewidth=1.0, linestyle="--")
        plt.xlabel("rho")
        plt.ylabel("MLE median (renorm=10)")
        plt.title(f"{nucleus['id']} — Cut sigma={sigma_heatmap:.4f}, beta={beta_cut:.4f}")
        plt.tight_layout()
        plt.savefig(out_dir / f"{SCRIPT_STEM}_{nucleus['id']}_cut_mle_vs_rho.png", dpi=FIG_DPI)
        plt.close()
    else:
        print(f"[warn] no cut data for nucleus {nucleus['id']}")


# =============================================================================
# SUMMARY
# =============================================================================

def summarize_one_nucleus(rows: Sequence[BoundaryCaseResult]) -> Dict:
    A, B, C = extract_abc(rows)
    class_counts = {
        cls: sum(1 for r in rows if r.class_v3_3bis == cls)
        for cls in ["CHAOS_STRONG", "CHAOS_WEAK", "BORDER", "OSCILLATORY", "UNSTABLE"]
    }
    unique_centers = {
        (round(r.center_sigma, 12), round(r.center_rho, 12), round(r.center_beta, 12))
        for r in rows
    }
    if rows:
        if len(unique_centers) == 1:
            summary_center_sigma = rows[0].center_sigma
            summary_center_rho = rows[0].center_rho
            summary_center_beta = rows[0].center_beta
        else:
            summary_center_sigma = float(np.mean([r.center_sigma for r in rows]))
            summary_center_rho = float(np.mean([r.center_rho for r in rows]))
            summary_center_beta = float(np.mean([r.center_beta for r in rows]))
    else:
        summary_center_sigma = math.nan
        summary_center_rho = math.nan
        summary_center_beta = math.nan

    center_B = None
    if B:
        center_B = {
            "sigma": float(np.mean([r.sigma for r in B])),
            "rho": float(np.mean([r.rho for r in B])),
            "beta": float(np.mean([r.beta for r in B])),
        }
    n_negative = sum(1 for r in B if r.mle_median_ref is not None and r.mle_median_ref < 0)
    return {
        "nucleus_id": rows[0].nucleus_id if rows else "NA",
        "nucleus_kind": rows[0].nucleus_kind if rows else "NA",
        "source_mode": rows[0].source_mode if rows else "NA",
        "center_sigma": summary_center_sigma,
        "center_rho": summary_center_rho,
        "center_beta": summary_center_beta,
        "n_center_groups": len(unique_centers),
        "n_points": len(rows),
        "A_count": len(A),
        "B_count": len(B),
        "C_count": len(C),
        "B_negative_count": n_negative,
        "CHAOS_STRONG": class_counts["CHAOS_STRONG"],
        "CHAOS_WEAK": class_counts["CHAOS_WEAK"],
        "BORDER": class_counts["BORDER"],
        "OSCILLATORY": class_counts["OSCILLATORY"],
        "UNSTABLE": class_counts["UNSTABLE"],
        "B_center_sigma": None if center_B is None else center_B["sigma"],
        "B_center_rho": None if center_B is None else center_B["rho"],
        "B_center_beta": None if center_B is None else center_B["beta"],
    }


# =============================================================================
# MAIN
# =============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TRIDOM v3.3bis-targeted multi-nucleus refinement")
    parser.add_argument("--mode", choices=sorted(MODES.keys()), default="local")
    parser.add_argument("--outdir", type=str, default=".")
    parser.add_argument(
        "--points-csv",
        type=str,
        default=None,
        help=(
            "CSV explicite de points à évaluer. Colonnes requises: sigma,rho,beta. "
            "Colonnes optionnelles: point_id,patch_label,patch_source,"
            "center_sigma,center_rho,center_beta,center_nucleus."
        ),
    )
    parser.add_argument(
        "--nuclei",
        type=str,
        default=None,
        help=(
            "Comma-separated list of nucleus IDs to run "
            "(e.g. NEG5,NEG1,NEG3). Default: all nuclei."
        ),
    )
    return parser.parse_args()


def resolve_nuclei(requested_csv: Optional[str]) -> List[Dict]:
    nuclei_by_id = {n["id"]: n for n in NUCLEI}

    if not requested_csv:
        return list(NUCLEI)

    requested = [n.strip().upper() for n in requested_csv.split(",") if n.strip()]
    requested = list(dict.fromkeys(requested))  # deduplicate while preserving order

    unknown = [r for r in requested if r not in nuclei_by_id]
    if unknown:
        raise ValueError(
            f"Nucleus IDs inconnus : {unknown}. "
            f"Disponibles : {sorted(nuclei_by_id.keys())}"
        )

    return [nuclei_by_id[r] for r in requested]


def main() -> None:
    args = parse_args()
    cfg = MODES[args.mode]
    out_dir = Path(args.outdir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    explicit_points = load_explicit_points_csv(args.points_csv) if args.points_csv else None
    if explicit_points is not None:
        if args.nuclei:
            print("[info] --nuclei ignored because --points-csv is set")
        nuclei_to_run = [build_targeted_pseudo_nucleus(explicit_points)]
    else:
        nuclei_to_run = resolve_nuclei(args.nuclei)

    print("=" * 96)
    print(DISPLAY_VERSION)
    print("Multi-nucleus boundary refinement around C2a")
    print("=" * 96)
    print(f"Mode           : {args.mode}  ({cfg['description']})")
    print(f"Nuclei         : {[n['id'] for n in nuclei_to_run]}")
    print(f"Points CSV     : {args.points_csv if args.points_csv else 'None'}")
    print(f"N_IC           : {cfg['n_ic']}")
    print(f"Burn steps     : {cfg['burn_steps']}")
    print(f"Measure steps  : {cfg['measure_steps']}")
    print(f"RENORM grid    : {cfg['renorm_grid']}")
    print(f"Output dir     : {out_dir}")
    print()

    topologies = gen_dense_topologies()
    W0 = topologies[ANCHOR["topo_idx"]]
    W = permute_topology(W0, ANCHOR["perm"])
    topo_lbl = topo_label(W0)
    perm_lbl = topo_label(W)
    eff_sig = effective_signature(W)

    all_summary_rows: List[Dict] = []
    global_json_summary: Dict = {
        "meta": {
            "mode": args.mode,
            "points_csv": args.points_csv,
            "config": {
                k: (list(map(float, v)) if hasattr(v, "__len__") and not isinstance(v, (str, list)) else v)
                for k, v in cfg.items()
            },
            "anchor": ANCHOR,
            "nuclei": nuclei_to_run,
        },
        "nuclei": {},
    }

    t_global = time.perf_counter()

    for nucleus in nuclei_to_run:
        rows = run_one_nucleus(
            nucleus, cfg, W, topo_lbl, perm_lbl, eff_sig,
            explicit_points=explicit_points,
        )

        nucleus_meta = {
            "mode": args.mode,
            "points_csv": args.points_csv,
            "anchor": ANCHOR,
            "nucleus": nucleus,
            "config": {
                k: (list(map(float, v)) if hasattr(v, "__len__") and not isinstance(v, (str, list)) else v)
                for k, v in cfg.items()
            },
        }

        save_csv(rows, out_dir / f"{SCRIPT_STEM}_{nucleus['id']}_results.csv")
        save_json(rows, nucleus_meta, out_dir / f"{SCRIPT_STEM}_{nucleus['id']}_results.json")
        if explicit_points is None:
            plot_nucleus(nucleus, cfg, rows, out_dir)
        else:
            print("[info] plots skipped in --points-csv mode (non-cartesian point set)")

        nucleus_summary = summarize_one_nucleus(rows)
        all_summary_rows.append(nucleus_summary)
        global_json_summary["nuclei"][nucleus["id"]] = nucleus_summary

        print(f"\nSummary {nucleus['id']}")
        print("-" * 48)
        for k in [
            "A_count", "B_count", "C_count", "B_negative_count",
            "CHAOS_STRONG", "CHAOS_WEAK", "BORDER", "OSCILLATORY", "UNSTABLE",
        ]:
            print(f"  {k:<22}: {nucleus_summary[k]}")
        if nucleus_summary["B_center_sigma"] is not None:
            print(
                f"  B center             : "
                f"({nucleus_summary['B_center_sigma']:.4f}, "
                f"{nucleus_summary['B_center_rho']:.4f}, "
                f"{nucleus_summary['B_center_beta']:.4f})"
            )

    save_summary_csv(all_summary_rows, out_dir / f"{SCRIPT_STEM}_summary.csv")
    with (out_dir / f"{SCRIPT_STEM}_summary.json").open("w", encoding="utf-8") as f:
        json.dump(global_json_summary, f, indent=2, ensure_ascii=False)

    elapsed = time.perf_counter() - t_global

    print("\n" + "=" * 96)
    print("FILES")
    print("=" * 96)
    for nucleus in nuclei_to_run:
        nid = nucleus["id"]
        suffixes = ["_results.csv", "_results.json"]
        if explicit_points is None:
            suffixes += [
                "_heatmap_mle.png",
                "_heatmap_class.png",
                "_cut_mle_vs_rho.png",
            ]
        for suffix in suffixes:
            print(f"  {out_dir / f'{SCRIPT_STEM}_{nid}{suffix}'}")
    print(f"  {out_dir / f'{SCRIPT_STEM}_summary.csv'}")
    print(f"  {out_dir / f'{SCRIPT_STEM}_summary.json'}")
    print(f"\nTotal runtime : {elapsed / 60:.2f} min")
    print("v3.3bis-targeted completed.")

    # Interactive pause only when launched from a real TTY.
    if sys.stdin.isatty():
        try:
            input("\nAppuyez sur Entrée pour quitter...")
        except EOFError:
            pass
 

if __name__ == "__main__":
    main()