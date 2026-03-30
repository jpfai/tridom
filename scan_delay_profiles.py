from pathlib import Path
"""
TRIDOM — Scan global retards non uniformes
Étape 2 — 64 topologies denses, profils weak / strong, tanh

Pour chaque topologie dense signée à 3 nœuds :
  - profil weak  : tau = [0.5, 0.5, 0.5, ...] (retards faibles uniformes)
  - profil strong: tau = [3.0, 3.0, 3.0, ...] (retards forts uniformes)
Intégration DDE par Euler–Maruyama discret (approximation à pas fixe).
Classification : Fixed / Oscillating / Unstable.
"""

import numpy as np
import json

from itertools import product

np.random.seed(42)

# ── Paramètres ────────────────────────────────────────────────────────────────
ALPHA       = 1.0          # taux de décroissance
N_IC        = 20           # conditions initiales par topologie
N_STEPS     = 600          # pas d'intégration
DT          = 0.05         # pas de temps
HIST_LEN    = 60           # longueur historique (steps)
VAR_THRESH  = 1e-4         # seuil variance → oscillation
BLOW_THRESH = 1e2          # seuil explosion → unstable

DELAY_PROFILES = {
    "weak":   0.5,   # τ faible → tau_steps ≈ 10
    "strong": 3.0,   # τ fort   → tau_steps ≈ 60
}

# ── Génération des 64 topologies denses signées ───────────────────────────────
def gen_dense_topologies():
    """
    Topologies 3 nœuds fortement connexes, signées ±1, denses (tous les arcs ij i≠j présents).
    6 arcs possibles (0→1, 0→2, 1→0, 1→2, 2→0, 2→1) → 2^6 = 64 combinaisons de signes.
    Chaque topologie est représentée comme matrice W 3×3 avec 0 sur la diagonale.
    """
    arcs = [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)]
    topos = []
    for signs in product([-1,1], repeat=6):
        W = np.zeros((3,3))
        for (i,j), s in zip(arcs, signs):
            W[i,j] = s
        topos.append(W)
    return topos

# ── Intégration DDE (Euler discret avec historique) ───────────────────────────
def integrate_dde(W, tau_steps, n_ic=N_IC, n_steps=N_STEPS, dt=DT):
    """
    x_{t+1} = x_t + dt * (-alpha*x_t + W @ tanh(x_{t - tau_steps}))
    tau_steps : entier, retard en nombre de steps
    Retourne la trajectoire finale (n_ic, 3, n_steps).
    """
    results = []
    for _ in range(n_ic):
        x_hist = np.random.uniform(-0.5, 0.5, size=(HIST_LEN + n_steps + 1, 3))
        x = x_hist[:HIST_LEN].copy()  # initialisation historique aléatoire

        traj = []
        for t in range(n_steps):
            t_delayed = max(0, len(x) - 1 - tau_steps)
            x_delayed = x[t_delayed]
            dx = -ALPHA * x[-1] + W @ np.tanh(x_delayed)
            x_new = x[-1] + dt * dx
            x = np.vstack([x, x_new])
            traj.append(x_new.copy())

        results.append(np.array(traj))  # (n_steps, 3)
    return np.array(results)  # (n_ic, n_steps, 3)

# ── Classification ────────────────────────────────────────────────────────────
def classify(trajs):
    """
    trajs : (n_ic, n_steps, 3)
    Retourne 'Fixed', 'Oscillating', ou 'Unstable'.
    """
    window = trajs[:, -100:, :]  # dernières 100 steps
    max_vals = np.abs(window).max(axis=(1,2))

    if max_vals.max() > BLOW_THRESH:
        return "Unstable"

    variances = window.var(axis=1).mean(axis=1)  # (n_ic,)
    frac_osc = (variances > VAR_THRESH).mean()

    if frac_osc >= 0.5:
        return "Oscillating"
    else:
        return "Fixed"

# ── Scan principal ────────────────────────────────────────────────────────────
def run_scan():
    topologies = gen_dense_topologies()
    print(f"Topologies générées : {len(topologies)}")

    results = []

    for topo_idx, W in enumerate(topologies):
        row = {"topo_idx": topo_idx, "W": W.tolist()}

        for profile_name, tau_val in DELAY_PROFILES.items():
            tau_steps = max(1, int(tau_val / DT))
            trajs = integrate_dde(W, tau_steps)
            regime = classify(trajs)
            row[profile_name] = regime

        results.append(row)

        if (topo_idx + 1) % 16 == 0:
            print(f"  [{topo_idx+1}/64] "
                  f"weak={row['weak']} strong={row['strong']}")

    return results

# ── Résumé ────────────────────────────────────────────────────────────────────
def summarize(results):
    from collections import Counter
    for profile in ["weak", "strong"]:
        counts = Counter(r[profile] for r in results)
        print(f"\nProfil '{profile}':")
        for regime, n in sorted(counts.items()):
            print(f"  {regime:12s} : {n:3d}  ({100*n/len(results):.1f}%)")

    # Matrice de transition weak → strong
    print("\nMatrice de transition (weak → strong) :")
    regimes = ["Fixed", "Oscillating", "Unstable"]
    header = f"{'weak \\ strong':<14}" + "".join(f"{r:>12}" for r in regimes)
    print(header)
    for r_weak in regimes:
        row_str = f"{r_weak:<14}"
        for r_strong in regimes:
            n = sum(1 for x in results
                    if x["weak"] == r_weak and x["strong"] == r_strong)
            row_str += f"{n:>12}"
        print(row_str)

# ── Sauvegarde ────────────────────────────────────────────────────────────────
def save_results(results, path=str(Path(__file__).parent / "scan_delay_results.json")):
    # Sauvegarder sans les matrices W (trop volumineuses) pour le JSON résumé
    summary = [{"topo_idx": r["topo_idx"],
                "weak": r["weak"],
                "strong": r["strong"]} for r in results]
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nRésultats sauvegardés → {path}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("TRIDOM — Scan retards non uniformes (weak / strong)")
    print("=" * 60)
    results = run_scan()
    summarize(results)
    save_results(results)
    print("\nScan terminé.")
