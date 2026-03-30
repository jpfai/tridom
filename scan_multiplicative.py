from pathlib import Path
"""
TRIDOM — Scan couplage multiplicatif
Étape 3 — Modèle enrichi : dx_i/dt = -alpha*x_i + sum_j W_ij * x_j * phi(x_j)

Comparaison :
  - modèle additif (référence)  : dx = -alpha*x + W @ phi(x)
  - modèle multiplicatif        : dx_i = -alpha*x_i + sum_j W_ij * x_j * phi(x_j)

Sur les 64 topologies denses signées à 3 nœuds.
Classification : Fixed / Oscillating / Complex / Unstable
Indicateur Lyapunov approché par divergence de trajectoires proches.
"""

import numpy as np
import json
from itertools import product
from collections import Counter

np.random.seed(42)

# ── Paramètres ────────────────────────────────────────────────────────────────
ALPHA        = 1.0
N_IC         = 30
N_STEPS      = 1000
DT           = 0.02
VAR_THRESH   = 1e-4
BLOW_THRESH  = 1e3
LYAP_EPS     = 1e-7     # perturbation initiale pour Lyapunov
LYAP_THRESH  = 0.005    # seuil indicateur Lyapunov → Complex

# ── Génération des 64 topologies denses ───────────────────────────────────────
def gen_dense_topologies():
    arcs = [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)]
    topos = []
    for signs in product([-1,1], repeat=6):
        W = np.zeros((3,3))
        for (i,j), s in zip(arcs, signs):
            W[i,j] = s
        topos.append(W)
    return topos

# ── Modèle additif (référence) ────────────────────────────────────────────────
def step_additive(x, W, alpha=ALPHA, dt=DT):
    dx = -alpha * x + W @ np.tanh(x)
    return x + dt * dx

# ── Modèle multiplicatif ──────────────────────────────────────────────────────
def step_multiplicative(x, W, alpha=ALPHA, dt=DT):
    """
    dx_i/dt = -alpha*x_i + sum_j W_ij * x_j * tanh(x_j)
    = -alpha*x_i + W @ (x * tanh(x))   [produit terme à terme]
    """
    phi_x = x * np.tanh(x)   # x_j * phi(x_j) — non-linéarité quadratique signée
    dx = -alpha * x + W @ phi_x
    return x + dt * dx

# ── Intégration + calcul Lyapunov approché ───────────────────────────────────
def integrate_with_lyapunov(step_fn, W, n_ic=N_IC, n_steps=N_STEPS):
    """
    Retourne (trajs, lyap_indicators).
    trajs : (n_ic, n_steps+1, 3)
    lyap_indicators : (n_ic,) — indicateur de divergence exponentielle
    """
    trajs = []
    lyap_indicators = []

    for _ in range(n_ic):
        x0 = np.random.uniform(-1.0, 1.0, 3)
        x0_perturb = x0 + np.random.normal(0, LYAP_EPS, 3)

        x = x0.copy()
        x_p = x0_perturb.copy()
        traj = [x.copy()]
        divergences = []

        for t in range(n_steps):
            x   = step_fn(x, W)
            x_p = step_fn(x_p, W)
            traj.append(x.copy())

            # Renormalisation pour calcul Lyapunov
            diff = x_p - x
            norm = np.linalg.norm(diff)
            if norm > 0:
                lyap_local = np.log(norm / LYAP_EPS)
                divergences.append(lyap_local)
                x_p = x + (diff / norm) * LYAP_EPS  # renormaliser

        trajs.append(np.array(traj))
        lyap_mean = np.mean(divergences[-200:]) if divergences else 0.0
        lyap_indicators.append(lyap_mean)

    return np.array(trajs), np.array(lyap_indicators)

# ── Classification ────────────────────────────────────────────────────────────
def classify(trajs, lyap_indicators):
    window = trajs[:, -200:, :]
    max_vals = np.abs(window).max(axis=(1, 2))

    if max_vals.max() > BLOW_THRESH:
        return "Unstable"

    variances = window.var(axis=1).mean(axis=1)
    frac_osc = (variances > VAR_THRESH).mean()
    lyap_mean = lyap_indicators.mean()

    if frac_osc >= 0.5:
        if lyap_mean > LYAP_THRESH:
            return "Complex"
        return "Oscillating"
    else:
        if lyap_mean > LYAP_THRESH:
            return "Complex"
        return "Fixed"

# ── Scan principal ────────────────────────────────────────────────────────────
def run_scan():
    topologies = gen_dense_topologies()
    print(f"Topologies : {len(topologies)}")
    print(f"{'idx':>4}  {'Additif':>12}  {'Multiplicatif':>14}  {'Lyap_add':>10}  {'Lyap_mul':>10}")
    print("-" * 60)

    results = []
    complex_topos = []

    for idx, W in enumerate(topologies):
        # Modèle additif
        trajs_add, lyap_add = integrate_with_lyapunov(step_additive, W)
        regime_add = classify(trajs_add, lyap_add)

        # Modèle multiplicatif
        trajs_mul, lyap_mul = integrate_with_lyapunov(step_multiplicative, W)
        regime_mul = classify(trajs_mul, lyap_mul)

        row = {
            "topo_idx":     idx,
            "W":            W.tolist(),
            "additive":     regime_add,
            "multiplicative": regime_mul,
            "lyap_add_mean": float(lyap_add.mean()),
            "lyap_mul_mean": float(lyap_mul.mean()),
        }
        results.append(row)

        if regime_mul in ("Complex", "Unstable") or regime_add != regime_mul:
            marker = " ◄" if regime_mul == "Complex" else ""
            print(f"{idx:>4}  {regime_add:>12}  {regime_mul:>14}  "
                  f"{lyap_add.mean():>10.4f}  {lyap_mul.mean():>10.4f}{marker}")

        if regime_mul == "Complex":
            complex_topos.append(row)

    return results, complex_topos

# ── Résumé ────────────────────────────────────────────────────────────────────
def summarize(results, complex_topos):
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)

    for model in ["additive", "multiplicative"]:
        counts = Counter(r[model] for r in results)
        print(f"\nModèle '{model}':")
        for regime, n in sorted(counts.items()):
            print(f"  {regime:14s}: {n:3d}  ({100*n/len(results):.1f}%)")

    print(f"\nTopologies Complex (multiplicatif) : {len(complex_topos)}")
    if complex_topos:
        print("\nDétail des topologies complexes :")
        for t in complex_topos:
            W = np.array(t["W"])
            signs = []
            for i,j in [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)]:
                signs.append("E" if W[i,j] > 0 else "I")
            label = ".".join(f"{i}{j}{s}" for (i,j),s in
                             zip([(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)], signs))
            print(f"  topo_{t['topo_idx']:02d} | {label} | "
                  f"add={t['additive']:12s} | mul={t['multiplicative']:12s} | "
                  f"lyap_mul={t['lyap_mul_mean']:.4f}")

# ── Sauvegarde ────────────────────────────────────────────────────────────────
def save(results, path=str(Path(__file__).parent / "scan_multiplicative_results.json")):
    out = [{k: v for k, v in r.items() if k != "W"} for r in results]
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nRésultats → {path}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("TRIDOM — Scan couplage multiplicatif vs additif")
    print("=" * 60)
    results, complex_topos = run_scan()
    summarize(results, complex_topos)
    save(results)
    print("\nScan terminé.")
