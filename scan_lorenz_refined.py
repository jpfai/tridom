"""
TRIDOM — Lorenz triadique affiné (Priorité 2)
Système autonome — pas de forçage externe.

Objectif : identifier parmi les 64 topologies denses celles qui sont
structurellement compatibles avec le mécanisme de Lorenz, puis affiner
les paramètres (sigma, rho, beta) pour chacune.

Rappel Lorenz canonique :
    dx0 = sigma * (x1 - x0)              [couplage linéaire différentiel]
    dx1 = x0 * (rho - x2) - x1           [couplage croisé x0*x2 + linéaire]
    dx2 = x0 * x1 - beta * x2            [couplage croisé x0*x1 + linéaire]

Structure Lorenz requise :
  - Un arc (i→j) avec couplage (xj - xi)  → boucle différentielle
  - Un arc (j→k) avec couplage xi*(rho - xk)  → couplage croisé inhibiteur
  - Un arc (i→k) avec couplage xi*xj  → couplage croisé excitateur

Étapes :
  1. Filtrer les topologies Lorenz-compatibles (score de compatibilité)
  2. Pour chaque topologie compatible, balayer (sigma, rho, beta)
  3. Classifier : Fixed / Oscillating / Complex / Unstable
  4. Calculer exposant Lyapunov par renormalisation

Le chaos de Lorenz canonique existe pour : sigma=10, rho=28, beta=8/3.
On balaie autour de ces valeurs et vers des régimes plus modestes.
"""

import numpy as np
import json
from pathlib import Path
from itertools import product
from collections import Counter

np.random.seed(42)

# ── Paramètres ────────────────────────────────────────────────────────────────
N_IC         = 20
N_STEPS      = 3000        # plus long pour détecter attracteurs
DT           = 0.005       # pas fin — Lorenz est sensible
BLOW_THRESH  = 1e4
LYAP_EPS     = 1e-8
LYAP_THRESH  = 0.005       # exposant Lyapunov positif → Complex
VAR_THRESH   = 1e-3

ARCS = [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)]

# Grille de paramètres (sigma, rho, beta)
# Lorenz canonique : (10, 28, 2.67)
# On balaye plusieurs régimes connus pour être chaotiques
PARAM_GRID = [
    ( 10.0, 28.0,  8/3),   # canonique
    ( 10.0, 28.0,  1.0),
    ( 10.0, 28.0,  4.0),
    ( 16.0, 45.0,  4.0),   # hyperchaotique
    (  5.0, 15.0,  8/3),   # sous-critique
    ( 10.0, 99.6,  8/3),   # période-3 → chaos
    ( 14.0, 28.0,  8/3),
    (  8.0, 28.0,  8/3),
]

# ── Génération des 64 topologies denses ───────────────────────────────────────
def gen_dense_topologies():
    topos = []
    for signs in product([-1, 1], repeat=6):
        W = np.zeros((3, 3))
        for (i, j), s in zip(ARCS, signs):
            W[i, j] = s
        topos.append(W)
    return topos

# ── Score de compatibilité Lorenz ─────────────────────────────────────────────
def lorenz_compatibility_score(W):
    """
    Heuristique : une topologie est Lorenz-compatible si elle possède
    des arcs permettant les deux couplages croisés nécessaires :
      - au moins 2 arcs excitatoires (pour x0*x1 et x0*x2 > 0)
      - au moins 1 arc inhibitoire (pour -(rho - xk) quand xk > rho)
    Score : 0 à 3 (3 = maximalement compatible).
    On retient toutes les topologies (score >= 1) pour ne pas
    sur-filtrer — le mécanisme de Lorenz n'exige pas une structure
    exactement binaire.
    """
    n_exc = sum(1 for (i,j) in ARCS if W[i,j] > 0)
    n_inh = sum(1 for (i,j) in ARCS if W[i,j] < 0)
    score = 0
    if n_exc >= 2: score += 1
    if n_inh >= 1: score += 1
    if n_exc >= 3 and n_inh >= 1: score += 1
    return score

# ── Modèle Lorenz triadique signé ─────────────────────────────────────────────
def step_lorenz_signed(x, W, sigma, rho, beta, dt=DT):
    """
    Lorenz triadique : les signes de W modulent les couplages croisés.

    dx[0] = sigma * W[0,1] * (x[1] - x[0])
    dx[1] = W[1,0] * x[0] * (rho - x[2]) * W[1,2] - x[1]
    dx[2] = W[2,0] * W[2,1] * x[0] * x[1] - beta * x[2]

    Interprétation : les signes de W orientent les couplages croisés
    (excitateur / inhibiteur) mais conservent la structure Lorenz.
    """
    dx = np.zeros(3)
    dx[0] = sigma * W[0,1] * (x[1] - x[0])
    dx[1] = W[1,0] * x[0] * (rho - W[1,2] * x[2]) - x[1]
    dx[2] = W[2,0] * W[2,1] * x[0] * x[1] - beta * x[2]
    return x + dt * dx

# ── Intégration + Lyapunov ────────────────────────────────────────────────────
def integrate_lyapunov(W, sigma, rho, beta,
                       n_ic=N_IC, n_steps=N_STEPS, dt=DT):
    trajs, lyap_indicators = [], []

    for _ in range(n_ic):
        # CI dans le bassin de Lorenz
        x0   = np.array([1.0, 1.0, rho * 0.5]) + np.random.normal(0, 1.0, 3)
        x0_p = x0 + np.random.normal(0, LYAP_EPS, 3)
        x, x_p = x0.copy(), x0_p.copy()
        traj, divergences = [x.copy()], []

        for _ in range(n_steps):
            x   = step_lorenz_signed(x,   W, sigma, rho, beta, dt)
            x_p = step_lorenz_signed(x_p, W, sigma, rho, beta, dt)
            traj.append(x.copy())

            diff = x_p - x
            norm = np.linalg.norm(diff)
            if 0 < norm < BLOW_THRESH:
                divergences.append(np.log(norm / LYAP_EPS))
                x_p = x + (diff / norm) * LYAP_EPS

        trajs.append(np.array(traj))
        lyap = np.mean(divergences[-800:]) if len(divergences) > 200 else -np.inf
        lyap_indicators.append(lyap)

    return np.array(trajs), np.array(lyap_indicators)

# ── Classification ────────────────────────────────────────────────────────────
def classify(trajs, lyap_indicators):
    window   = trajs[:, -600:, :]
    max_vals = np.abs(window).max(axis=(1, 2))

    n_unstable = (max_vals > BLOW_THRESH).sum()
    if n_unstable > N_IC // 2:
        return "Unstable", float(np.nanmean(lyap_indicators))

    bounded   = max_vals <= BLOW_THRESH
    if bounded.sum() == 0:
        return "Unstable", float(np.nanmean(lyap_indicators))

    window_b  = window[bounded]
    variances = window_b.var(axis=1).mean(axis=1)
    frac_osc  = (variances > VAR_THRESH).mean()
    lyap_mean = float(np.nanmean(lyap_indicators[bounded]))

    if lyap_mean > LYAP_THRESH and frac_osc > 0.3:
        return "Complex", lyap_mean
    elif frac_osc >= 0.4:
        return "Oscillating", lyap_mean
    else:
        return "Fixed", lyap_mean

# ── Scan principal ────────────────────────────────────────────────────────────
def run_scan():
    topologies = gen_dense_topologies()

    # Filtrer par score de compatibilité Lorenz
    compatible = [(idx, W, lorenz_compatibility_score(W))
                  for idx, W in enumerate(topologies)]
    compatible.sort(key=lambda x: -x[2])  # score décroissant

    print(f"Topologies Lorenz-compatibles (score ≥ 1) : "
          f"{sum(1 for _,_,s in compatible if s >= 1)} / 64")
    print(f"Score 3 (maximalement compatibles) : "
          f"{sum(1 for _,_,s in compatible if s == 3)}")
    print(f"Paramétrisations testées : {len(PARAM_GRID)}")
    print(f"Total runs : "
          f"{sum(1 for _,_,s in compatible if s>=1) * len(PARAM_GRID)} × {N_IC} CI\n")

    all_results = []
    complex_hits = []
    counts = Counter()

    print(f"{'idx':>4} {'score':>5} {'sigma':>6} {'rho':>6} {'beta':>6} "
          f"{'Régime':>14} {'Lyap':>10}")
    print("-" * 58)

    for topo_idx, W, score in compatible:
        if score < 1:
            continue

        for sigma, rho, beta in PARAM_GRID:
            trajs, lyap = integrate_lyapunov(W, sigma, rho, beta)
            regime, lyap_mean = classify(trajs, lyap)
            counts[regime] += 1

            row = {
                "topo_idx": topo_idx,
                "score":    score,
                "sigma":    sigma,
                "rho":      rho,
                "beta":     round(beta, 4),
                "regime":   regime,
                "lyap":     lyap_mean,
            }
            all_results.append(row)

            if regime == "Complex":
                complex_hits.append(row)
                signs = []
                for i, j in ARCS:
                    signs.append("E" if W[i,j] > 0 else "I")
                label = ".".join(f"{i}{j}{s}" for (i,j),s in zip(ARCS, signs))
                print(f"{topo_idx:>4} {score:>5} {sigma:>6.1f} {rho:>6.1f} "
                      f"{beta:>6.3f} {'Complex':>14} {lyap_mean:>10.5f}  "
                      f"◄◄◄ CHAOS BORNÉ | {label}")
            elif regime == "Unstable":
                # Afficher instabilités seulement pour score max
                if score == 3:
                    print(f"{topo_idx:>4} {score:>5} {sigma:>6.1f} {rho:>6.1f} "
                          f"{beta:>6.3f} {'Unstable':>14} {lyap_mean:>10.5f}")

    return all_results, complex_hits, counts

# ── Résumé ────────────────────────────────────────────────────────────────────
def summarize(counts, complex_hits):
    print("\n" + "=" * 60)
    print("RÉSUMÉ — Lorenz triadique affiné")
    print("=" * 60)
    total = sum(counts.values())
    for regime, n in sorted(counts.items()):
        print(f"  {regime:16s}: {n:4d}  ({100*n/total:.1f}%)")

    print(f"\nTotal cas Complex (chaos borné) : {len(complex_hits)}")

    if complex_hits:
        print("\nDétail :")
        for h in complex_hits:
            print(f"  topo_{h['topo_idx']:02d} (score={h['score']}) | "
                  f"sigma={h['sigma']} rho={h['rho']} beta={h['beta']:.3f} | "
                  f"lyap={h['lyap']:.5f}")
    else:
        print("\n→ Aucun attracteur chaotique borné détecté dans ce scan.")
        print("  Piste suivante : couplage croisé pur W_ij * x_j * x_k (j≠k).")

# ── Sauvegarde ────────────────────────────────────────────────────────────────
def save(all_results,
         path=str(Path(__file__).parent / "scan_lorenz_refined_results.json")):
    with open(path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nRésultats → {path}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("TRIDOM — Lorenz triadique affiné (Priorité 2)")
    print("Système autonome — aucun forçage externe")
    print("=" * 60)
    all_results, complex_hits, counts = run_scan()
    summarize(counts, complex_hits)
    save(all_results)
    print("\nScan terminé.")
