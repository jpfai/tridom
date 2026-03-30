from pathlib import Path
"""
TRIDOM — Nona Dense (9 nœuds, 3 triades max-interconnectées)
Étape 3 — Test d'émergence de complexité bornée au niveau supra-triadique

Architecture :
  - 3 triades internes (nœuds 0-2, 3-5, 6-8), chacune dense signée
  - Couplage inter-triadique : arcs entre toutes les paires de triades
  - Phase 1 : sans retard (ODE)
  - Phase 2 : retard uniforme
  - Phase 3 : retard non uniforme (weak / strong) si nécessaire

Classification : Fixed / Oscillating / Complex (potentiellement chaotique borné)
"""

import numpy as np
import json

from itertools import product

np.random.seed(42)

# ── Paramètres ────────────────────────────────────────────────────────────────
N_NODES      = 9
N_TRIADS     = 3
TRIAD_SIZE   = 3
ALPHA        = 1.0
N_IC         = 30
N_STEPS      = 1000
DT           = 0.05
VAR_THRESH   = 1e-4
LYAP_THRESH  = 0.01      # seuil indicateur Lyapunov → complexité
BLOW_THRESH  = 1e2

# ── Construction de la matrice Nona dense ─────────────────────────────────────
def build_nona_matrix(intra_signs, inter_strength=0.3, inter_seed=0):
    """
    intra_signs : liste de 3 matrices 3×3 (une par triade)
    inter_strength : amplitude du couplage inter-triadique (aléatoire signé)
    Retourne W (9×9).
    """
    W = np.zeros((N_NODES, N_NODES))

    # Blocs intra-triadiques
    for t, W_t in enumerate(intra_signs):
        offset = t * TRIAD_SIZE
        W[offset:offset+TRIAD_SIZE, offset:offset+TRIAD_SIZE] = W_t

    # Couplage inter-triadique : arcs entre toutes les triades
    rng = np.random.RandomState(inter_seed)
    for t1 in range(N_TRIADS):
        for t2 in range(N_TRIADS):
            if t1 == t2:
                continue
            o1 = t1 * TRIAD_SIZE
            o2 = t2 * TRIAD_SIZE
            # Connexions denses inter-triadiques signées aléatoirement
            for i in range(TRIAD_SIZE):
                for j in range(TRIAD_SIZE):
                    s = rng.choice([-1, 1])
                    W[o1+i, o2+j] = inter_strength * s

    return W

# ── Intégration ODE (sans retard) ─────────────────────────────────────────────
def integrate_ode(W, n_ic=N_IC, n_steps=N_STEPS, dt=DT):
    results = []
    for _ in range(n_ic):
        x = np.random.uniform(-0.5, 0.5, N_NODES)
        traj = [x.copy()]
        for _ in range(n_steps):
            dx = -ALPHA * x + W @ np.tanh(x)
            x = x + dt * dx
            traj.append(x.copy())
        results.append(np.array(traj))
    return np.array(results)  # (n_ic, n_steps+1, 9)

# ── Intégration DDE (avec retard uniforme) ────────────────────────────────────
def integrate_dde(W, tau_steps, n_ic=N_IC, n_steps=N_STEPS, dt=DT):
    results = []
    hist_len = max(tau_steps, 1)
    for _ in range(n_ic):
        hist = [np.random.uniform(-0.5, 0.5, N_NODES)
                for _ in range(hist_len)]
        traj = list(hist)
        for t in range(n_steps):
            x_now = traj[-1]
            x_del = traj[-tau_steps] if len(traj) >= tau_steps else traj[0]
            dx = -ALPHA * x_now + W @ np.tanh(x_del)
            x_new = x_now + dt * dx
            traj.append(x_new.copy())
        results.append(np.array(traj))
    return np.array(results)

# ── Classification avec indicateur Lyapunov approché ─────────────────────────
def classify_with_lyapunov(trajs):
    """
    trajs : (n_ic, n_steps+1, 9)
    Retourne 'Fixed', 'Oscillating', 'Complex', ou 'Unstable'.
    """
    window = trajs[:, -200:, :]
    max_vals = np.abs(window).max(axis=(1, 2))

    if max_vals.max() > BLOW_THRESH:
        return "Unstable"

    variances = window.var(axis=1).mean(axis=1)
    frac_osc = (variances > VAR_THRESH).mean()

    # Indicateur Lyapunov approché : divergence de 2 CI proches
    lyap_indicators = []
    for ic in range(min(10, len(trajs))):
        traj1 = trajs[ic]
        # Perturber légèrement la CI
        x0_perturb = trajs[ic, 0] + np.random.normal(0, 1e-6, N_NODES)
        # Intégrer W identique
        W_approx = None  # non disponible ici, on utilise la variance différentielle
        diff = np.diff(traj1, axis=0)
        lyap_approx = np.log(np.abs(diff[-50:]).mean() + 1e-12)
        lyap_indicators.append(lyap_approx)

    lyap_mean = np.mean(lyap_indicators)

    if frac_osc >= 0.5:
        if lyap_mean > LYAP_THRESH:
            return "Complex"
        return "Oscillating"
    else:
        return "Fixed"

# ── Scan Nona ─────────────────────────────────────────────────────────────────
def run_nona_scan():
    print("=" * 60)
    print("TRIDOM — Nona Dense (9 nœuds, 3 triades)")
    print("=" * 60)

    # Générer quelques configurations intra-triadiques représentatives
    # On prend les 4 topologies représentatives de l'atlas
    arcs = [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)]

    # Topologies de référence : all-inhibitory (osc), mixed (osc), all-excitatory (fixed)
    def make_W(signs):
        W = np.zeros((3,3))
        for (i,j), s in zip(arcs, signs):
            W[i,j] = s
        return W

    ref_topologies = {
        "all_inhibitory":  make_W([-1,-1,-1,-1,-1,-1]),  # 01I.12I.20I + arcs
        "mixed_osc":       make_W([ 1, 1,-1, 1,-1,-1]),  # oscillatoire
        "all_excitatory":  make_W([ 1, 1, 1, 1, 1, 1]),  # monostable
    }

    results = {}

    for topo_name, W_triad in ref_topologies.items():
        print(f"\nTopologie intra-triadique : {topo_name}")
        results[topo_name] = {}

        for inter_seed in range(5):  # 5 configurations de couplage inter-triadique
            W_nona = build_nona_matrix(
                [W_triad, W_triad, W_triad],
                inter_strength=0.3,
                inter_seed=inter_seed
            )

            # Phase 1 : sans retard
            trajs_ode = integrate_ode(W_nona)
            regime_ode = classify_with_lyapunov(trajs_ode)

            # Phase 2 : retard uniforme τ=1.0
            tau_steps = max(1, int(1.0 / DT))
            trajs_dde = integrate_dde(W_nona, tau_steps)
            regime_dde = classify_with_lyapunov(trajs_dde)

            key = f"seed_{inter_seed}"
            results[topo_name][key] = {
                "no_delay": regime_ode,
                "uniform_delay_tau1": regime_dde,
            }
            print(f"  seed={inter_seed} | no_delay={regime_ode:12s} | "
                  f"uniform_delay={regime_dde}")

    return results

# ── Résumé ────────────────────────────────────────────────────────────────────
def summarize_nona(results):
    from collections import Counter
    print("\n" + "=" * 60)
    print("RÉSUMÉ — Nona Dense")
    print("=" * 60)

    all_ode, all_dde = [], []
    for topo, seeds in results.items():
        for seed, regimes in seeds.items():
            all_ode.append(regimes["no_delay"])
            all_dde.append(regimes["uniform_delay_tau1"])

    print("\nSans retard :")
    for regime, n in sorted(Counter(all_ode).items()):
        print(f"  {regime:14s}: {n:3d}  ({100*n/len(all_ode):.1f}%)")

    print("\nRetard uniforme τ=1.0 :")
    for regime, n in sorted(Counter(all_dde).items()):
        print(f"  {regime:14s}: {n:3d}  ({100*n/len(all_dde):.1f}%)")

    complex_found = any(
        v["no_delay"] == "Complex" or v["uniform_delay_tau1"] == "Complex"
        for seeds in results.values()
        for v in seeds.values()
    )
    print(f"\nComplexité bornée détectée : {'OUI' if complex_found else 'NON'}")

# ── Sauvegarde ────────────────────────────────────────────────────────────────
def save_nona_results(results, path=str(Path(__file__).parent / "nona_dense_results.json")):
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nRésultats sauvegardés → {path}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = run_nona_scan()
    summarize_nona(results)
    save_nona_results(results)
    print("\nNona dense : scan terminé.")
