"""
TRIDOM — Scan non-linéarité non monotone
Modèle : dx/dt = -alpha*x + W @ phi(x)

phi non monotone testée sur les 64 topologies denses (poids binaires ±1) :

  NM1 — Sinus           : phi(x) = sin(x)
  NM2 — Sinc signé      : phi(x) = x * exp(-x^2)        [Gaussienne dérivée]
  NM3 — Oscillante bornée: phi(x) = sin(x) / (1 + |x|)
  NM4 — Double-puits    : phi(x) = x - x^3/3             [Taylor tanh tronqué, non monotone pour |x|>1]
  NM5 — Sinus amorti    : phi(x) = sin(pi*x) * exp(-0.1*|x|)

Pour chaque topologie × phi : N_IC conditions initiales.
Classification : Fixed / Oscillating / Complex / Unstable
Indicateur Lyapunov par divergence de trajectoires proches (renormalisation).

Résultats sauvegardés dans le même dossier que ce script.
"""

import numpy as np
import json
from pathlib import Path
from itertools import product
from collections import Counter

np.random.seed(42)

# ── Paramètres ────────────────────────────────────────────────────────────────
ALPHA        = 1.0
N_IC         = 20
N_STEPS      = 1500
DT           = 0.01
VAR_THRESH   = 1e-4
BLOW_THRESH  = 1e3
LYAP_EPS     = 1e-8
LYAP_THRESH  = 0.01      # exposant Lyapunov positif → Complex

ARCS = [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)]

# ── Non-linéarités non monotones ──────────────────────────────────────────────
def phi_sin(x):
    return np.sin(x)

def phi_sinc_gauss(x):
    return x * np.exp(-x**2)

def phi_sin_bounded(x):
    return np.sin(x) / (1.0 + np.abs(x))

def phi_double_well(x):
    # Taylor tronqué de tanh : x - x^3/3
    # Non monotone pour |x| > 1
    return x - (x**3) / 3.0

def phi_sin_damped(x):
    return np.sin(np.pi * x) * np.exp(-0.1 * np.abs(x))

NONLINEARITIES = {
    "NM1_sin":         phi_sin,
    "NM2_sinc_gauss":  phi_sinc_gauss,
    "NM3_sin_bounded": phi_sin_bounded,
    "NM4_double_well": phi_double_well,
    "NM5_sin_damped":  phi_sin_damped,
}

# ── Génération des 64 topologies denses ───────────────────────────────────────
def gen_dense_topologies():
    topos = []
    for signs in product([-1, 1], repeat=6):
        W = np.zeros((3, 3))
        for (i, j), s in zip(ARCS, signs):
            W[i, j] = s
        topos.append(W)
    return topos

# ── Intégration + Lyapunov ────────────────────────────────────────────────────
def integrate_lyapunov(W, phi, n_ic=N_IC, n_steps=N_STEPS, dt=DT):
    trajs, lyap_indicators = [], []

    for _ in range(n_ic):
        x0   = np.random.uniform(-1.5, 1.5, 3)
        x0_p = x0 + np.random.normal(0, LYAP_EPS, 3)
        x, x_p = x0.copy(), x0_p.copy()
        traj, divergences = [x.copy()], []

        for _ in range(n_steps):
            dx   = -ALPHA * x   + W @ phi(x)
            dx_p = -ALPHA * x_p + W @ phi(x_p)
            x    = x   + dt * dx
            x_p  = x_p + dt * dx_p
            traj.append(x.copy())

            diff = x_p - x
            norm = np.linalg.norm(diff)
            if 0 < norm < BLOW_THRESH:
                divergences.append(np.log(norm / LYAP_EPS))
                x_p = x + (diff / norm) * LYAP_EPS

        trajs.append(np.array(traj))
        lyap = np.mean(divergences[-500:]) if len(divergences) > 100 else -np.inf
        lyap_indicators.append(lyap)

    return np.array(trajs), np.array(lyap_indicators)

# ── Classification ────────────────────────────────────────────────────────────
def classify(trajs, lyap_indicators):
    window   = trajs[:, -400:, :]
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
    all_results = []
    complex_hits = []
    summary = {nm: Counter() for nm in NONLINEARITIES}

    print(f"{'NL':>18} | {'Fixed':>6} {'Osc':>6} {'Complex':>8} {'Unstable':>8}")
    print("-" * 58)

    for nm_name, phi in NONLINEARITIES.items():
        for topo_idx, W in enumerate(topologies):
            trajs, lyap = integrate_lyapunov(W, phi)
            regime, lyap_mean = classify(trajs, lyap)
            summary[nm_name][regime] += 1

            row = {
                "topo_idx": topo_idx,
                "nl":       nm_name,
                "regime":   regime,
                "lyap":     lyap_mean,
            }
            all_results.append(row)

            if regime == "Complex":
                complex_hits.append(row)
                signs = []
                for i, j in ARCS:
                    signs.append("E" if W[i, j] > 0 else "I")
                label = ".".join(f"{i}{j}{s}"
                                 for (i, j), s in zip(ARCS, signs))
                print(f"  ◄◄◄ COMPLEX | {nm_name} | topo_{topo_idx:02d} | "
                      f"{label} | lyap={lyap_mean:.5f}")

        c = summary[nm_name]
        tot = sum(c.values())
        print(f"{nm_name:>18} | {c['Fixed']:>6} {c['Oscillating']:>6} "
              f"{c['Complex']:>8} {c['Unstable']:>8}   (total={tot})")

    return all_results, complex_hits, summary

# ── Résumé ────────────────────────────────────────────────────────────────────
def summarize(summary, complex_hits):
    print("\n" + "=" * 60)
    print("RÉSUMÉ GLOBAL — Non-linéarité non monotone")
    print("=" * 60)
    print(f"{'NL':>20} | {'Fixed%':>7} {'Osc%':>7} {'Cplx%':>7} {'Unst%':>7}")
    print("-" * 58)
    for nm, counts in summary.items():
        total = sum(counts.values())
        f = counts["Fixed"]
        o = counts["Oscillating"]
        c = counts["Complex"]
        u = counts["Unstable"]
        print(f"{nm:>20} | {100*f/total:>6.1f}% {100*o/total:>6.1f}% "
              f"{100*c/total:>6.1f}% {100*u/total:>6.1f}%")

    print(f"\nTotal cas Complex détectés : {len(complex_hits)}")
    if complex_hits:
        print("\nDétail des topologies complexes :")
        for h in complex_hits:
            print(f"  topo_{h['topo_idx']:02d} | {h['nl']} | lyap={h['lyap']:.5f}")
    else:
        print("\n→ Aucun attracteur chaotique borné détecté dans ce scan.")

# ── Sauvegarde ────────────────────────────────────────────────────────────────
def save(all_results,
         path=str(Path(__file__).parent / "scan_nonmonotone_results.json")):
    with open(path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nRésultats → {path}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("TRIDOM — Non-linéarité non monotone")
    print(f"5 NL × 64 topologies × {N_IC} CI = {5*64*N_IC} trajectoires")
    print("=" * 60)
    all_results, complex_hits, summary = run_scan()
    summarize(summary, complex_hits)
    save(all_results)
    print("\nScan terminé.")
