from pathlib import Path
"""
TRIDOM — Scan poids réels non binaires
Modèle : dx/dt = -alpha*x + W_real @ tanh(x)

W_real conserve la structure topologique signée de chaque topologie dense,
mais les amplitudes sont tirées selon différentes distributions :

  D1 — Gaussienne signée  : W_ij = sign_ij * |N(0,1)|
  D2 — Uniforme signée    : W_ij = sign_ij * U(0.1, 3.0)
  D3 — Asymétrique        : W_ij = sign_ij * |N(0, sigma_ij)| avec sigma variable
  D4 — Forte asymétrie    : certains poids dominants (lognormale)

Pour chaque topologie × distribution × réalisation de poids :
  - N_WEIGHT_SAMPLES tirages de W_real
  - N_IC conditions initiales par tirage

Classification : Fixed / Oscillating / Complex / Unstable
Indicateur Lyapunov par divergence de trajectoires proches.
"""

import numpy as np
import json
from itertools import product
from collections import Counter

np.random.seed(42)

# ── Paramètres ────────────────────────────────────────────────────────────────
ALPHA           = 1.0
N_IC            = 10
N_WEIGHT_SAMPLES = 5      # tirages de poids par topologie
N_STEPS         = 800
DT              = 0.01
VAR_THRESH      = 1e-4
BLOW_THRESH     = 1e3
LYAP_EPS        = 1e-8
LYAP_THRESH     = 0.01

ARCS = [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)]

# ── Génération des 64 topologies denses ───────────────────────────────────────
def gen_dense_topologies():
    topos = []
    for signs in product([-1,1], repeat=6):
        W = np.zeros((3,3))
        for (i,j), s in zip(ARCS, signs):
            W[i,j] = s
        topos.append(W)
    return topos

# ── Distributions de poids réels ──────────────────────────────────────────────
def sample_weights(W_sign, dist, rng):
    """Remplace les ±1 par des amplitudes réelles selon la distribution."""
    W_real = np.zeros((3,3))
    for (i,j) in ARCS:
        s = W_sign[i,j]
        if dist == "D1_gaussian":
            amp = abs(rng.normal(0, 1))
        elif dist == "D2_uniform":
            amp = rng.uniform(0.1, 3.0)
        elif dist == "D3_asymmetric":
            # sigma variable selon la position dans la matrice
            sigma = 0.5 + 1.5 * ((i + j) % 3) / 2.0
            amp = abs(rng.normal(0, sigma))
        elif dist == "D4_lognormal":
            amp = rng.lognormal(mean=0.0, sigma=0.8)
        W_real[i,j] = s * amp
    return W_real

# ── Intégration + Lyapunov ────────────────────────────────────────────────────
def integrate_lyapunov(W, n_ic=N_IC, n_steps=N_STEPS, dt=DT):
    trajs, lyap_indicators = [], []

    for _ in range(n_ic):
        x0   = np.random.uniform(-1.0, 1.0, 3)
        x0_p = x0 + np.random.normal(0, LYAP_EPS, 3)
        x, x_p = x0.copy(), x0_p.copy()
        traj, divergences = [x.copy()], []

        for _ in range(n_steps):
            dx   = -ALPHA * x   + W @ np.tanh(x)
            dx_p = -ALPHA * x_p + W @ np.tanh(x_p)
            x   = x   + dt * dx
            x_p = x_p + dt * dx_p
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

    bounded  = max_vals <= BLOW_THRESH
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
    distributions = ["D1_gaussian", "D2_uniform", "D3_asymmetric", "D4_lognormal"]
    rng = np.random.RandomState(42)

    # Résultats agrégés : pour chaque (topo, dist) → liste de régimes sur N_WEIGHT_SAMPLES
    all_results = []
    complex_hits = []

    print(f"{'dist':>16} | {'Fixed':>6} {'Osc':>6} {'Complex':>8} {'Unstable':>8}")
    print("-" * 55)

    summary_by_dist = {d: Counter() for d in distributions}

    for dist in distributions:
        for topo_idx, W_sign in enumerate(topologies):
            for sample in range(N_WEIGHT_SAMPLES):
                W_real = sample_weights(W_sign, dist, rng)
                trajs, lyap = integrate_lyapunov(W_real)
                regime, lyap_mean = classify(trajs, lyap)

                summary_by_dist[dist][regime] += 1

                row = {
                    "topo_idx": topo_idx,
                    "dist": dist,
                    "sample": sample,
                    "regime": regime,
                    "lyap": lyap_mean,
                    "W_real": W_real.tolist(),
                }
                all_results.append(row)

                if regime == "Complex":
                    complex_hits.append(row)
                    signs = []
                    for i,j in ARCS:
                        signs.append("E" if W_sign[i,j] > 0 else "I")
                    label = ".".join(f"{i}{j}{s}" for (i,j),s in zip(ARCS, signs))
                    print(f"  ◄◄◄ COMPLEX | {dist} | topo_{topo_idx:02d} | "
                          f"{label} | sample={sample} | lyap={lyap_mean:.5f}")

        total = sum(summary_by_dist[dist].values())
        c = summary_by_dist[dist]
        print(f"{dist:>16} | {c['Fixed']:>6} {c['Oscillating']:>6} "
              f"{c['Complex']:>8} {c['Unstable']:>8}   "
              f"(total={total})")

    return all_results, complex_hits, summary_by_dist

# ── Résumé détaillé ───────────────────────────────────────────────────────────
def summarize(summary_by_dist, complex_hits):
    print("\n" + "=" * 60)
    print("RÉSUMÉ GLOBAL — Poids réels non binaires")
    print("=" * 60)
    print(f"{'Distribution':>18} | {'Fixed%':>7} {'Osc%':>7} {'Cplx%':>7} {'Unst%':>7}")
    print("-" * 55)
    for dist, counts in summary_by_dist.items():
        total = sum(counts.values())
        f = counts["Fixed"]
        o = counts["Oscillating"]
        c = counts["Complex"]
        u = counts["Unstable"]
        print(f"{dist:>18} | {100*f/total:>6.1f}% {100*o/total:>6.1f}% "
              f"{100*c/total:>6.1f}% {100*u/total:>6.1f}%")

    print(f"\nTotal cas Complex détectés : {len(complex_hits)}")

    if complex_hits:
        print("\nDétail :")
        for h in complex_hits:
            W = np.array(h["W_real"])
            amps = [f"{W[i,j]:+.3f}" for i,j in ARCS]
            print(f"  topo_{h['topo_idx']:02d} | {h['dist']} | "
                  f"sample={h['sample']} | lyap={h['lyap']:.5f}")
            print(f"    amplitudes : {' '.join(amps)}")
    else:
        print("\n→ Aucun attracteur chaotique borné détecté dans ce scan.")

# ── Sauvegarde ────────────────────────────────────────────────────────────────
def save(all_results, path=str(Path(__file__).parent / "scan_real_weights_results.json")):
    out = [{"topo_idx": r["topo_idx"], "dist": r["dist"],
            "sample": r["sample"], "regime": r["regime"],
            "lyap": r["lyap"]} for r in all_results]
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nRésultats → {path}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("TRIDOM — Poids réels non binaires (4 distributions × 64 topos × 10 samples)")
    print(f"Total runs : {4 * 64 * 10} × {N_IC} CI = {4*64*10*N_IC} trajectoires")
    print("=" * 60)
    all_results, complex_hits, summary_by_dist = run_scan()
    summarize(summary_by_dist, complex_hits)
    save(all_results)
    print("\nScan terminé.")
