#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TRIDOM — scan_lorenz_refined_v2.py

Version v2 nettoyée pour validation méthodologique.

But :
    Scanner les 64 topologies denses signées à 3 nœuds dans un cadre
    Lorenz-like autonome, avec estimation plus propre du Lyapunov maximal,
    intégration RK4, gestion stricte des divergences numériques, et
    exposition des classes effectives réellement distinguées par le modèle.

Idée centrale :
    Le modèle reste autonome, sans forçage externe. On teste si des
    couplages croisés de type Lorenz ouvrent des régimes bornés à Lyapunov
    positif, absents du cadre additif séparé étudié auparavant.

ATTENTION ÉPISTÉMIQUE :
    - Ce script est un outil de validation numérique.
    - Un régime "Complex" signifie ici :
        "cas bornés avec mouvement non trivial et MLE positif selon ce protocole".
      Ce n'est pas, à lui seul, une preuve mathématique définitive de chaos.
    - Le modèle utilisé ne dépend pas des 6 arcs de manière symétrique :
        W[0,2] n'intervient pas directement dans la dynamique.
      La sortie expose donc aussi une "effective signature" pour éviter
      de surinterpréter des labels topologiques dégénérés.

Sorties :
    - scan_lorenz_refined_v2_results.json
    - résumé console
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from itertools import permutations, product
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np


# =============================================================================
# CONFIGURATION
# =============================================================================

SEED = 42
RNG = np.random.default_rng(SEED)

ARCS: List[Tuple[int, int]] = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]

PARAM_GRID: List[Tuple[float, float, float]] = [
    (10.0, 28.0, 8.0 / 3.0),  # Lorenz canonique
    (10.0, 28.0, 1.0),
    (10.0, 28.0, 4.0),
    (16.0, 45.0, 4.0),
    (5.0, 15.0, 8.0 / 3.0),
    (10.0, 99.6, 8.0 / 3.0),
    (14.0, 28.0, 8.0 / 3.0),
    (8.0, 28.0, 8.0 / 3.0),
]

# Intégration
N_IC = 20
N_STEPS = 4000
DT = 0.0025

# Contrôles numériques
BLOW_THRESH = 1e4
FINITE_EPS = 1e-15

# Lyapunov
LYAP_EPS = 1e-8
LYAP_TRANSIENT_STEPS = 1200
LYAP_POS_THRESH = 0.05   # seuil prudent en unités ~ 1/temps

# Fenêtre de classification
TAIL_STEPS = 1000
SPEED_THRESH = 1e-3
VAR_THRESH = 1e-4

# Seuils de classification agrégée
MIN_BOUNDED_FRAC_FOR_NONUNSTABLE = 0.50
MIN_OSC_FRAC_FOR_OSC = 0.40
MIN_OSC_FRAC_FOR_COMPLEX = 0.30
MIN_POS_LYAP_FRAC_FOR_COMPLEX = 0.30

# Permutations
USE_PERMUTATIONS = True
PERM_LIST = list(permutations([0, 1, 2])) if USE_PERMUTATIONS else [(0, 1, 2)]


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ICResult:
    bounded: bool
    nonfinite: bool
    blowup: bool
    mle: Optional[float]
    tail_var: Optional[float]
    tail_speed: Optional[float]
    final_state: Optional[List[float]]
    n_steps_completed: int


@dataclass
class CaseResult:
    topo_idx: int
    topo_label: str
    perm: Tuple[int, int, int]
    perm_label: str
    score: int
    effective_signature: str
    sigma: float
    rho: float
    beta: float
    regime: str
    bounded_frac: float
    moving_frac: float
    pos_lyap_frac: float
    mle_mean_bounded: Optional[float]
    mle_median_bounded: Optional[float]
    n_bounded: int
    n_moving: int
    n_pos_lyap: int


# =============================================================================
# TOPOLOGY UTILITIES
# =============================================================================

def gen_dense_topologies() -> List[np.ndarray]:
    topos: List[np.ndarray] = []
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


def lorenz_score_descriptive(W: np.ndarray) -> int:
    n_exc = sum(1 for i, j in ARCS if W[i, j] > 0)
    n_inh = sum(1 for i, j in ARCS if W[i, j] < 0)
    score = 0
    if n_exc >= 2:
        score += 1
    if n_inh >= 1:
        score += 1
    if n_exc >= 3 and n_inh >= 1:
        score += 1
    return score


def effective_signature(W: np.ndarray) -> str:
    s01 = "+" if W[0, 1] > 0 else "-"
    s10 = "+" if W[1, 0] > 0 else "-"
    s12 = "+" if W[1, 2] > 0 else "-"
    s2021 = "+" if (W[2, 0] * W[2, 1]) > 0 else "-"
    return f"W01={s01}|W10={s10}|W12={s12}|W20W21={s2021}"


# =============================================================================
# DYNAMICS
# =============================================================================

def lorenz_signed_rhs(x: np.ndarray, W: np.ndarray, sigma: float, rho: float, beta: float) -> np.ndarray:
    """
    Système Lorenz-like signé autonome.

    dx0 = sigma * W01 * (x1 - x0)
    dx1 = W10 * x0 * (rho - W12*x2) - x1
    dx2 = (W20*W21) * x0 * x1 - beta*x2
    """
    dx = np.zeros(3, dtype=float)
    dx[0] = sigma * W[0, 1] * (x[1] - x[0])
    dx[1] = W[1, 0] * x[0] * (rho - W[1, 2] * x[2]) - x[1]
    dx[2] = (W[2, 0] * W[2, 1]) * x[0] * x[1] - beta * x[2]
    return dx


def rk4_step(x: np.ndarray, W: np.ndarray, sigma: float, rho: float, beta: float, dt: float) -> np.ndarray:
    k1 = lorenz_signed_rhs(x, W, sigma, rho, beta)
    k2 = lorenz_signed_rhs(x + 0.5 * dt * k1, W, sigma, rho, beta)
    k3 = lorenz_signed_rhs(x + 0.5 * dt * k2, W, sigma, rho, beta)
    k4 = lorenz_signed_rhs(x + dt * k3, W, sigma, rho, beta)
    return x + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def is_state_valid(x: np.ndarray) -> bool:
    return np.all(np.isfinite(x)) and np.max(np.abs(x)) <= BLOW_THRESH


# =============================================================================
# SINGLE-RUN INTEGRATION + MLE
# =============================================================================

def random_initial_condition(rho: float) -> np.ndarray:
    center = np.array([1.0, 1.0, max(1.0, 0.5 * rho)], dtype=float)
    return center + RNG.normal(0.0, 1.0, size=3)


def integrate_one_ic(
    W: np.ndarray,
    sigma: float,
    rho: float,
    beta: float,
    n_steps: int = N_STEPS,
    dt: float = DT,
) -> ICResult:
    x = random_initial_condition(rho)
    direction = RNG.normal(0.0, 1.0, size=3)
    direction_norm = np.linalg.norm(direction)
    if direction_norm < FINITE_EPS:
        direction = np.array([1.0, 0.0, 0.0], dtype=float)
    else:
        direction = direction / direction_norm

    x_p = x + LYAP_EPS * direction

    tail_states: List[np.ndarray] = []
    lyap_sum = 0.0
    lyap_count = 0

    bounded = True
    nonfinite = False
    blowup = False
    n_steps_completed = 0

    for step in range(n_steps):
        x = rk4_step(x, W, sigma, rho, beta, dt)
        x_p = rk4_step(x_p, W, sigma, rho, beta, dt)
        n_steps_completed = step + 1

        if not is_state_valid(x) or not is_state_valid(x_p):
            bounded = False
            nonfinite = not (np.all(np.isfinite(x)) and np.all(np.isfinite(x_p)))
            blowup = not nonfinite
            break

        if step >= n_steps - TAIL_STEPS:
            tail_states.append(x.copy())

        if step >= LYAP_TRANSIENT_STEPS:
            diff = x_p - x
            norm = np.linalg.norm(diff)

            if np.isfinite(norm) and norm > FINITE_EPS:
                lyap_sum += math.log(norm / LYAP_EPS)
                lyap_count += 1
                x_p = x + (diff / norm) * LYAP_EPS
            else:
                re_dir = RNG.normal(0.0, 1.0, size=3)
                re_norm = np.linalg.norm(re_dir)
                if re_norm < FINITE_EPS:
                    re_dir = np.array([1.0, 0.0, 0.0], dtype=float)
                else:
                    re_dir = re_dir / re_norm
                x_p = x + LYAP_EPS * re_dir

    if not bounded:
        return ICResult(
            bounded=False,
            nonfinite=nonfinite,
            blowup=blowup,
            mle=None,
            tail_var=None,
            tail_speed=None,
            final_state=None,
            n_steps_completed=n_steps_completed,
        )

    if len(tail_states) < 5:
        return ICResult(
            bounded=False,
            nonfinite=False,
            blowup=True,
            mle=None,
            tail_var=None,
            tail_speed=None,
            final_state=x.tolist(),
            n_steps_completed=n_steps_completed,
        )

    tail = np.asarray(tail_states, dtype=float)
    diffs = np.diff(tail, axis=0)

    tail_var = float(np.mean(np.var(tail, axis=0)))
    tail_speed = float(np.mean(np.linalg.norm(diffs, axis=1)))

    mle = None
    if lyap_count > 0:
        mle = float(lyap_sum / (lyap_count * dt))

    return ICResult(
        bounded=True,
        nonfinite=False,
        blowup=False,
        mle=mle,
        tail_var=tail_var,
        tail_speed=tail_speed,
        final_state=x.tolist(),
        n_steps_completed=n_steps_completed,
    )


# =============================================================================
# CLASSIFICATION
# =============================================================================

def classify_case(ic_results: Sequence[ICResult]) -> Tuple[str, Dict[str, float]]:
    n_total = len(ic_results)
    bounded_runs = [r for r in ic_results if r.bounded]
    n_bounded = len(bounded_runs)
    bounded_frac = n_bounded / n_total

    if bounded_frac < MIN_BOUNDED_FRAC_FOR_NONUNSTABLE:
        metrics = {
            "bounded_frac": bounded_frac,
            "moving_frac": 0.0,
            "pos_lyap_frac": 0.0,
            "mle_mean_bounded": float("nan"),
            "mle_median_bounded": float("nan"),
            "n_bounded": n_bounded,
            "n_moving": 0,
            "n_pos_lyap": 0,
        }
        return "Unstable", metrics

    moving_flags = []
    mles = []

    for r in bounded_runs:
        moving = False
        if r.tail_speed is not None and r.tail_var is not None:
            moving = (r.tail_speed > SPEED_THRESH) and (r.tail_var > VAR_THRESH)
        moving_flags.append(moving)
        if r.mle is not None and np.isfinite(r.mle):
            mles.append(r.mle)

    n_moving = int(sum(moving_flags))
    moving_frac = n_moving / max(1, n_bounded)

    positive_mles = [m for m in mles if m > LYAP_POS_THRESH]
    n_pos_lyap = len(positive_mles)
    pos_lyap_frac = n_pos_lyap / max(1, n_bounded)

    mle_mean_bounded = float(np.mean(mles)) if mles else float("nan")
    mle_median_bounded = float(np.median(mles)) if mles else float("nan")

    metrics = {
        "bounded_frac": bounded_frac,
        "moving_frac": moving_frac,
        "pos_lyap_frac": pos_lyap_frac,
        "mle_mean_bounded": mle_mean_bounded,
        "mle_median_bounded": mle_median_bounded,
        "n_bounded": n_bounded,
        "n_moving": n_moving,
        "n_pos_lyap": n_pos_lyap,
    }

    if (moving_frac >= MIN_OSC_FRAC_FOR_COMPLEX) and (pos_lyap_frac >= MIN_POS_LYAP_FRAC_FOR_COMPLEX):
        return "Complex", metrics
    if moving_frac >= MIN_OSC_FRAC_FOR_OSC:
        return "Oscillating", metrics
    return "Fixed", metrics


# =============================================================================
# SCAN
# =============================================================================

def run_scan() -> Tuple[List[CaseResult], Dict[str, Dict[str, int]]]:
    topologies = gen_dense_topologies()

    all_case_results: List[CaseResult] = []
    eff_class_counter: Dict[str, Counter] = defaultdict(Counter)

    total_cases = len(topologies) * len(PERM_LIST) * len(PARAM_GRID)
    print("=" * 72)
    print("TRIDOM — Lorenz triadique affiné v2")
    print("Validation méthodologique")
    print("=" * 72)
    print(f"Topologies denses              : {len(topologies)}")
    print(f"Permutations par topologie     : {len(PERM_LIST)}")
    print(f"Paramétrisations               : {len(PARAM_GRID)}")
    print(f"Conditions initiales / cas     : {N_IC}")
    print(f"Total cas topo×perm×params     : {total_cases}")
    print(f"Total trajectoires             : {total_cases * N_IC}")
    print()

    print(
        f"{'topo':>4} {'perm':>12} {'sc':>3} {'sig':>7} {'rho':>6} {'beta':>7} "
        f"{'regime':>12} {'bnd%':>6} {'mov%':>6} {'lyap+%':>7} {'mle_med':>9}"
    )
    print("-" * 86)

    for topo_idx, W in enumerate(topologies):
        base_label = topo_label(W)

        for perm in PERM_LIST:
            Wp = permute_topology(W, perm)
            perm_lbl = topo_label(Wp)
            score = lorenz_score_descriptive(Wp)
            eff_sig = effective_signature(Wp)

            for sigma, rho, beta in PARAM_GRID:
                ic_results = [
                    integrate_one_ic(Wp, sigma, rho, beta)
                    for _ in range(N_IC)
                ]

                regime, metrics = classify_case(ic_results)

                row = CaseResult(
                    topo_idx=topo_idx,
                    topo_label=base_label,
                    perm=perm,
                    perm_label=perm_lbl,
                    score=score,
                    effective_signature=eff_sig,
                    sigma=float(sigma),
                    rho=float(rho),
                    beta=float(beta),
                    regime=regime,
                    bounded_frac=float(metrics["bounded_frac"]),
                    moving_frac=float(metrics["moving_frac"]),
                    pos_lyap_frac=float(metrics["pos_lyap_frac"]),
                    mle_mean_bounded=(
                        None if not np.isfinite(metrics["mle_mean_bounded"])
                        else float(metrics["mle_mean_bounded"])
                    ),
                    mle_median_bounded=(
                        None if not np.isfinite(metrics["mle_median_bounded"])
                        else float(metrics["mle_median_bounded"])
                    ),
                    n_bounded=int(metrics["n_bounded"]),
                    n_moving=int(metrics["n_moving"]),
                    n_pos_lyap=int(metrics["n_pos_lyap"]),
                )

                all_case_results.append(row)
                eff_class_counter[eff_sig][regime] += 1

                # N'afficher que les cas non-Fixed et non-Unstable, ou Complex
                if regime in ("Complex", "Oscillating") or (
                    regime == "Unstable" and row.mle_median_bounded is not None
                ):
                    mle_str = (
                        "       nan"
                        if row.mle_median_bounded is None
                        else f"{row.mle_median_bounded:9.4f}"
                    )
                    marker = "  ◄◄◄ COMPLEX" if regime == "Complex" else ""
                    print(
                        f"{topo_idx:4d} {str(perm):>12} {score:3d} {sigma:7.1f} {rho:6.1f} {beta:7.3f} "
                        f"{regime:>12} {100*row.bounded_frac:6.1f} {100*row.moving_frac:6.1f} "
                        f"{100*row.pos_lyap_frac:7.1f} {mle_str}{marker}"
                    )

    eff_summary = {
        sig: dict(counter)
        for sig, counter in sorted(eff_class_counter.items(), key=lambda kv: kv[0])
    }

    return all_case_results, eff_summary


# =============================================================================
# SUMMARY + SAVE
# =============================================================================

def summarize(case_results: Sequence[CaseResult], eff_summary: Dict[str, Dict[str, int]]) -> None:
    regime_counts = Counter(r.regime for r in case_results)
    total = len(case_results)

    print("\n" + "=" * 72)
    print("RÉSUMÉ GLOBAL")
    print("=" * 72)
    for regime in ["Complex", "Oscillating", "Fixed", "Unstable"]:
        n = regime_counts.get(regime, 0)
        print(f"  {regime:12s}: {n:6d}  ({100.0 * n / max(1, total):6.2f}%)")

    complex_hits = [r for r in case_results if r.regime == "Complex"]
    print(f"\nTotal cas 'Complex' : {len(complex_hits)}")

    if complex_hits:
        print("\nCas 'Complex' détaillés :")
        for r in complex_hits:
            mle_str = "None" if r.mle_median_bounded is None else f"{r.mle_median_bounded:.5f}"
            print(
                f"  topo_{r.topo_idx:02d} perm={r.perm} "
                f"sig={r.sigma:.1f} rho={r.rho:.1f} beta={r.beta:.3f} | "
                f"bnd={100*r.bounded_frac:.0f}% mov={100*r.moving_frac:.0f}% "
                f"lyap+={100*r.pos_lyap_frac:.0f}% mle_med={mle_str}"
            )
            print(f"    label    : {r.topo_label}")
            print(f"    perm_lbl : {r.perm_label}")
            print(f"    eff_sig  : {r.effective_signature}")
    else:
        print("\n→ Aucun cas Complex détecté avec ce seuil LYAP_POS_THRESH.")

    print("\n" + "=" * 72)
    print("RÉSUMÉ PAR CLASSE EFFECTIVE")
    print("=" * 72)
    for sig, counts in eff_summary.items():
        total_sig = sum(counts.values())
        n_complex = counts.get("Complex", 0)
        parts = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        marker = "  ◄ COMPLEX" if n_complex > 0 else ""
        print(f"  {sig:34s} | n={total_sig:5d} | {parts}{marker}")


def save_results(
    case_results: Sequence[CaseResult],
    eff_summary: Dict[str, Dict[str, int]],
    out_path: Path,
) -> None:
    payload = {
        "meta": {
            "seed": SEED,
            "n_ic": N_IC,
            "n_steps": N_STEPS,
            "dt": DT,
            "tail_steps": TAIL_STEPS,
            "lyap_transient_steps": LYAP_TRANSIENT_STEPS,
            "use_permutations": USE_PERMUTATIONS,
            "n_permutations": len(PERM_LIST),
            "blow_thresh": BLOW_THRESH,
            "lyap_eps": LYAP_EPS,
            "lyap_pos_thresh": LYAP_POS_THRESH,
            "speed_thresh": SPEED_THRESH,
            "var_thresh": VAR_THRESH,
            "param_grid": PARAM_GRID,
        },
        "effective_class_summary": eff_summary,
        "results": [asdict(r) for r in case_results],
    }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"\nRésultats JSON → {out_path}")


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    out_path = Path(__file__).parent / "scan_lorenz_refined_v2_results.json"
    case_results, eff_summary = run_scan()
    summarize(case_results, eff_summary)
    save_results(case_results, eff_summary, out_path)
    print("\nScan terminé.")


if __name__ == "__main__":
    main()
