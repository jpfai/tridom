from pathlib import Path
"""
TRIDOM — Scan famille Lorenz triadique
Modèle : couplage croisé x_i * x_j préservant l'antisymétrie

Trois variantes testées sur les 64 topologies denses :

  V1 — Lorenz canonique adapté (sigma/rho/beta imposés par W)
       dx_1 = W_12*(x_2 - x_1)
       dx_2 = W_20*x_1*(rho - x_3) - x_2
       dx_3 = W_01*x_1*x_2 - beta*x_3

  V2 — Couplage croisé général (produits x_j * tanh(x_k), j≠k)
       dx_i = -alpha*x_i + sum_{j≠k, j,k≠i} W_ij * x_j * tanh(x_k)
       + sum_j W_ij * tanh(x_j)   [terme additif résiduel]

  V3 — Couplage croisé pur signé
       dx_i = -alpha*x_i + sum_{j} W_ij * x_{(j+1)%3} * tanh(x_j)

Classification : Fixed / Oscillating / Complex / Unstable
Indicateur Lyapunov par divergence de trajectoires proches.
"""

import numpy as np
import json
from itertools import product
from collections import Counter

np.random.seed(42)

# ── Paramètres ────────────────────────────────────────────────────────────────
ALPHA        = 1.0
RHO          = 28.0      # paramètre Lorenz
SIGMA        = 10.0
BETA         = 8.0/3.0
N_IC         = 30
N_STEPS      = 2000
DT           = 0.005     # pas fin pour Lorenz
VAR_THRESH   = 1e-3
BLOW_THRESH  = 1e4
LYAP_EPS     = 1e-8
LYAP_THRESH  = 0.01      # exposant Lyapunov positif → chaos borné

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

# ── V1 — Lorenz triadique adapté ──────────────────────────────────────────────
def step_lorenz(x, W, dt=DT):
    """
    Lorenz adapté : les signes de W modulent les couplages croisés.
    dx0 = sigma * W[0,1] * (x[1] - x[0])
    dx1 = W[1,0] * x[0] * (rho - x[2]) - x[1]
    dx2 = W[0,1] * W[1,2] * x[0]*x[1] - beta*x[2]
    """
    dx = np.zeros(3)
    dx[0] = SIGMA * W[0,1] * (x[1] - x[0])
    dx[1] = W[1,0] * x[0] * (RHO - x[2]) - x[1]
    dx[2] = abs(W[0,1] * W[1,2]) * x[0]*x[1] - BETA * x[2]
    return x + dt * dx

# ── V2 — Couplage croisé général ─────────────────────────────────────────────
def step_cross_general(x, W, alpha=ALPHA, dt=DT):
    """
    dx_i = -alpha*x_i + sum_j W_ij * x_j * tanh(x_{(j+1)%3})
    Produit croisé entre variables successives.
    """
    n = len(x)
    phi = np.tanh(x)
    cross = np.zeros(n)
    for i in range(n):
        for j in range(n):
            k = (j + 1) % n
            cross[i] += W[i,j] * x[j] * phi[k]
    dx = -alpha * x + cross
    return x + dt * dx

# ── V3 — Couplage croisé pur signé ───────────────────────────────────────────
def step_cross_signed(x, W, alpha=ALPHA, dt=DT):
    """
    dx_i = -alpha*x_i + sum_j W_ij * sign(x_j) * x_{(j+1)%3}
    Préserve les signes de W et croise les variables.
    """
    n = len(x)
    cross = np.zeros(n)
    for i in range(n):
        for j in range(n):
            k = (j + 1) % n
            cross[i] += W[i,j] * np.sign(x[j] + 1e-12) * x[k]
    dx = -alpha * x + cross
    return x + dt * dx

# ── Intégration + Lyapunov ────────────────────────────────────────────────────
def integrate_lyapunov(step_fn, W, n_ic=N_IC, n_steps=N_STEPS):
    trajs, lyap_indicators = [], []

    for _ in range(n_ic):
        # CI selon le modèle
        if step_fn == step_lorenz:
            x0 = np.array([1.0, 0.0, 0.0]) + np.random.normal(0, 0.5, 3)
        else:
            x0 = np.random.uniform(-1.0, 1.0, 3)

        x0_p = x0 + np.random.normal(0, LYAP_EPS, 3)
        x, x_p = x0.copy(), x0_p.copy()
        traj, divergences = [x.copy()], []

        for _ in range(n_steps):
            x   = step_fn(x, W)
            x_p = step_fn(x_p, W)
            traj.append(x.copy())

            diff = x_p - x
            norm = np.linalg.norm(diff)
            if norm > 0 and norm < BLOW_THRESH:
                divergences.append(np.log(norm / LYAP_EPS))
                x_p = x + (diff / norm) * LYAP_EPS

        trajs.append(np.array(traj))
        lyap = np.mean(divergences[-400:]) if len(divergences) > 50 else -np.inf
        lyap_indicators.append(lyap)

    return np.array(trajs), np.array(lyap_indicators)

# ── Classification ────────────────────────────────────────────────────────────
def classify(trajs, lyap_indicators):
    window = trajs[:, -400:, :]
    max_vals = np.abs(window).max(axis=(1, 2))

    n_unstable = (max_vals > BLOW_THRESH).sum()
    if n_unstable > N_IC // 2:
        return "Unstable", float(np.nanmean(lyap_indicators))

    # Filtrer les trajectoires bornées
    bounded = max_vals <= BLOW_THRESH
    if bounded.sum() == 0:
        return "Unstable", float(np.nanmean(lyap_indicators))

    window_b = window[bounded]
    variances = window_b.var(axis=1).mean(axis=1)
    frac_osc  = (variances > VAR_THRESH).mean()
    lyap_mean = float(np.nanmean(lyap_indicators[bounded]))

    if lyap_mean > LYAP_THRESH and frac_osc > 0.3:
        return "Complex", lyap_mean
    elif frac_osc >= 0.4:
        return "Oscillating", lyap_mean
    else:
        return "Fixed", lyap_mean

# ── Scan ──────────────────────────────────────────────────────────────────────
def run_scan():
    topologies = gen_dense_topologies()
    variants = {
        "V1_Lorenz":       step_lorenz,
        "V2_CrossGeneral": step_cross_general,
        "V3_CrossSigned":  step_cross_signed,
    }

    results = {v: [] for v in variants}
    complex_found = {v: [] for v in variants}

    for v_name, step_fn in variants.items():
        print(f"\n{'='*60}")
        print(f"Variante : {v_name}")
        print(f"{'='*60}")
        print(f"{'idx':>4}  {'Régime':>14}  {'Lyap':>10}")
        print("-" * 35)

        for idx, W in enumerate(topologies):
            trajs, lyap = integrate_lyapunov(step_fn, W)
            regime, lyap_mean = classify(trajs, lyap)

            row = {
                "topo_idx": idx,
                "regime":   regime,
                "lyap":     lyap_mean,
                "W":        W.tolist(),
            }
            results[v_name].append(row)

            # Afficher uniquement les cas non-Fixed ou Complex
            if regime in ("Complex", "Unstable", "Oscillating"):
                marker = " ◄◄◄ CHAOS BORNÉ" if regime == "Complex" else ""
                print(f"{idx:>4}  {regime:>14}  {lyap_mean:>10.5f}{marker}")

            if regime == "Complex":
                complex_found[v_name].append(row)

    return results, complex_found

# ── Résumé ────────────────────────────────────────────────────────────────────
def summarize(results, complex_found):
    print("\n" + "=" * 60)
    print("RÉSUMÉ GLOBAL")
    print("=" * 60)

    for v_name, rows in results.items():
        counts = Counter(r["regime"] for r in rows)
        print(f"\n{v_name}:")
        for regime, n in sorted(counts.items()):
            print(f"  {regime:16s}: {n:3d}  ({100*n/len(rows):.1f}%)")

        if complex_found[v_name]:
            print(f"  *** {len(complex_found[v_name])} topologie(s) complexe(s) détectée(s) ***")
            for t in complex_found[v_name]:
                W = np.array(t["W"])
                signs = []
                for i,j in [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)]:
                    signs.append("E" if W[i,j] > 0 else "I")
                label = ".".join(f"{i}{j}{s}" for (i,j),s in
                                 zip([(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)], signs))
                print(f"    topo_{t['topo_idx']:02d} | {label} | lyap={t['lyap']:.5f}")

# ── Sauvegarde ────────────────────────────────────────────────────────────────
def save(results, path=str(Path(__file__).parent / "scan_lorenz_results.json")):
    out = {}
    for v_name, rows in results.items():
        out[v_name] = [{"topo_idx": r["topo_idx"],
                        "regime": r["regime"],
                        "lyap": r["lyap"]} for r in rows]
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nRésultats → {path}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("TRIDOM — Famille Lorenz triadique (3 variantes × 64 topologies)")
    print("=" * 60)
    results, complex_found = run_scan()
    summarize(results, complex_found)
    save(results)
    print("\nScan terminé.")
