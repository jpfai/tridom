#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRIDOM v3.1 — Portraits d'attracteurs canonisés
================================================
Produit 6 figures (4 projections chacune) pour les deux classes
chaotiques effectives et deux contrôles (oscillatoire, fixe).

Standard publication :
  - même burn-in (BURN_STEPS = 500)
  - même fenêtre (TRAJ_STEPS = 8000)
  - RK4, DT = 0.0025
  - projections (x0,x1), (x0,x2), (x1,x2), 3D
  - légende : classe effective, permutation, (sigma,rho,beta), MLE médian, statut

Sorties : tridom_v3_1_portrait_<id>.png dans le même dossier.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np

# ── Paramètres ────────────────────────────────────────────────────────────────
SEED        = 42
RNG         = np.random.default_rng(SEED)
DT          = 0.0025
BURN_STEPS  = 500
TRAJ_STEPS  = 8000
LYAP_EPS    = 1e-8
LYAP_TRANSIENT = 300
BLOW_THRESH = 1e4
FINITE_EPS  = 1e-15

ARCS: List[Tuple[int,int]] = [(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)]

# Couleurs par statut
COLOR_COMPLEX   = "#C0392B"   # rouge foncé
COLOR_OSC       = "#2471A3"   # bleu
COLOR_FIXED     = "#1E8449"   # vert
COLOR_ALPHA     = 0.55

# ── Topologies de référence ───────────────────────────────────────────────────
def make_W(sign_list: List[int]) -> np.ndarray:
    """sign_list : [s01, s02, s10, s12, s20, s21] dans l'ordre ARCS."""
    W = np.zeros((3, 3))
    for (i, j), s in zip(ARCS, sign_list):
        W[i, j] = float(s)
    return W

# Cas de référence issus de scan_lorenz_refined_v2
# Classe 1 : W01=+|W10=+|W12=+|W20W21=+
W_topo47 = make_W([+1, -1, +1, +1, -1, -1])  # topo_47 : 01E.02I.10E.12E.20I.21I => W20*W21=+
W_topo57 = make_W([+1, +1, +1, -1, -1, +1])  # topo_57 : 01E.02E.10E.12I.20I.21E => W20*W21=- → ajusté ci-dessous

# On définit les W directement par leur signature effective confirmée
# Classe 1 chaotique : W01=+ W10=+ W12=+ W20W21=+ (sgn aligné)
W_class1_a = make_W([+1, +1, +1, +1, +1, +1])   # tous excitateurs — topo_63
W_class1_b = make_W([+1, -1, +1, +1, -1, -1])   # topo_47 : W12=+, W20*W21=(-1)*(-1)=+

# Classe 2 chaotique : W01=+ W10=+ W12=- W20W21=- (sgn aligné)
W_class2_a = make_W([+1, +1, +1, -1, +1, -1])   # W12=-, W20*W21=(+1)*(-1)=-
W_class2_b = make_W([+1, -1, +1, -1, +1, +1])   # W12=-, W20*W21=(+1)*(+1)=+ → non aligné
# Correction : classe 2 requiert sgn(W12) = sgn(W20*W21) = -
# Donc W12=- et W20*W21 < 0
W_class2_b = make_W([+1, +1, +1, -1, -1, +1])   # W12=-, W20=-, W21=+, W20*W21=-

# Contrôle oscillatoire : W01=+ W10=+ W12=+ W20W21=+ mais (5,15,8/3) → Oscillating
W_ctrl_osc  = W_class1_a.copy()

# Contrôle fixe : W01=+ W10=- → 100% Fixed
W_ctrl_fixed = make_W([+1, +1, -1, +1, +1, +1])   # W10=-


@dataclass
class Portrait:
    label: str           # identifiant court
    W: np.ndarray
    sigma: float
    rho: float
    beta: float
    status: str          # "Complex" / "Oscillating" / "Fixed"
    eff_class: str       # classe effective
    perm: str            # "(0,1,2)"
    color: str


def eff_sig(W: np.ndarray) -> str:
    s01 = "+" if W[0,1] > 0 else "-"
    s10 = "+" if W[1,0] > 0 else "-"
    s12 = "+" if W[1,2] > 0 else "-"
    s2021 = "+" if (W[2,0]*W[2,1]) > 0 else "-"
    return f"W01={s01}|W10={s10}|W12={s12}|W20W21={s2021}"


PORTRAITS: List[Portrait] = [
    Portrait(
        label="C1a",
        W=W_class1_a,
        sigma=10., rho=28., beta=8./3.,
        status="Complex",
        eff_class="W01=+|W10=+|W12=+|W20W21=+",
        perm="(0,1,2)",
        color=COLOR_COMPLEX,
    ),
    Portrait(
        label="C1b",
        W=W_class1_b,
        sigma=16., rho=45., beta=4.,
        status="Complex",
        eff_class="W01=+|W10=+|W12=+|W20W21=+",
        perm="(0,1,2)",
        color=COLOR_COMPLEX,
    ),
    Portrait(
        label="C2a",
        W=W_class2_a,
        sigma=10., rho=99.6, beta=8./3.,
        status="Complex",
        eff_class="W01=+|W10=+|W12=-|W20W21=-",
        perm="(0,1,2)",
        color=COLOR_COMPLEX,
    ),
    Portrait(
        label="C2b",
        W=W_class2_b,
        sigma=16., rho=45., beta=4.,
        status="Complex",
        eff_class="W01=+|W10=+|W12=-|W20W21=-",
        perm="(0,1,2)",
        color=COLOR_COMPLEX,
    ),
    Portrait(
        label="OSC",
        W=W_ctrl_osc,
        sigma=5., rho=15., beta=8./3.,
        status="Oscillating",
        eff_class="W01=+|W10=+|W12=+|W20W21=+",
        perm="(0,1,2)",
        color=COLOR_OSC,
    ),
    Portrait(
        label="FIX",
        W=W_ctrl_fixed,
        sigma=10., rho=28., beta=8./3.,
        status="Fixed",
        eff_class="W01=+|W10=-|W12=+|W20W21=+",
        perm="(0,1,2)",
        color=COLOR_FIXED,
    ),
]

# ── Dynamique ─────────────────────────────────────────────────────────────────
def lorenz_rhs(x, W, sigma, rho, beta):
    dx = np.zeros(3)
    dx[0] = sigma * W[0,1] * (x[1] - x[0])
    dx[1] = W[1,0] * x[0] * (rho - W[1,2]*x[2]) - x[1]
    dx[2] = (W[2,0]*W[2,1]) * x[0]*x[1] - beta*x[2]
    return dx

def rk4(x, W, sigma, rho, beta, dt=DT):
    k1 = lorenz_rhs(x, W, sigma, rho, beta)
    k2 = lorenz_rhs(x + .5*dt*k1, W, sigma, rho, beta)
    k3 = lorenz_rhs(x + .5*dt*k2, W, sigma, rho, beta)
    k4 = lorenz_rhs(x + dt*k3, W, sigma, rho, beta)
    return x + (dt/6.)*(k1 + 2*k2 + 2*k3 + k4)

def is_valid(x):
    return np.all(np.isfinite(x)) and np.max(np.abs(x)) <= BLOW_THRESH

def integrate(W, sigma, rho, beta,
              burn=BURN_STEPS, steps=TRAJ_STEPS, dt=DT):
    """
    Retourne (traj, mle_median) où traj est (steps, 3).
    Essaie plusieurs CI si la première diverge.
    """
    center = np.array([1., 1., max(1., .5*rho)])
    for attempt in range(20):
        x = center + RNG.normal(0, 1.0, 3)
        # Burn-in
        ok = True
        for _ in range(burn):
            x = rk4(x, W, sigma, rho, beta, dt)
            if not is_valid(x):
                ok = False
                break
        if not ok:
            continue

        # Trajectoire + Lyapunov
        x_p = x + LYAP_EPS * (RNG.normal(0, 1, 3))
        x_p = x + (x_p - x) / np.linalg.norm(x_p - x) * LYAP_EPS

        traj = []
        lyap_vals = []
        diverged = False

        for step in range(steps):
            x   = rk4(x, W, sigma, rho, beta, dt)
            x_p = rk4(x_p, W, sigma, rho, beta, dt)

            if not is_valid(x) or not is_valid(x_p):
                diverged = True
                break

            traj.append(x.copy())

            if step >= LYAP_TRANSIENT:
                diff = x_p - x
                norm = np.linalg.norm(diff)
                if np.isfinite(norm) and norm > FINITE_EPS:
                    lyap_vals.append(math.log(norm / LYAP_EPS))
                    x_p = x + (diff / norm) * LYAP_EPS

        if diverged or len(traj) < steps // 2:
            continue

        traj = np.array(traj)
        mle = None
        if lyap_vals:
            mle = float(np.median(lyap_vals)) / dt

        return traj, mle

    return None, None   # toutes les tentatives ont divergé

# ── Tracé ─────────────────────────────────────────────────────────────────────
def plot_portrait(p: Portrait, out_dir: Path) -> None:
    traj, mle = integrate(p.W, p.sigma, p.rho, p.beta)

    if traj is None:
        print(f"  [SKIP] {p.label} — toutes les trajectoires ont divergé")
        return

    x0, x1, x2 = traj[:,0], traj[:,1], traj[:,2]

    # MLE string
    if mle is not None and np.isfinite(mle):
        mle_str = f"{mle:+.4f} s⁻¹"
    else:
        mle_str = "n/a"

    # Titre principal
    title = (
        f"[{p.status}]  {p.eff_class}\n"
        f"σ={p.sigma:.1f}  ρ={p.rho:.1f}  β={p.beta:.3f}  "
        f"MLE≈{mle_str}  perm={p.perm}"
    )

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(title, fontsize=10, y=0.98)
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)

    kw = dict(s=0.4, alpha=COLOR_ALPHA, c=p.color, rasterized=True)

    # (x0, x1)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.scatter(x0, x1, **kw)
    ax1.set_xlabel("$x_0$"); ax1.set_ylabel("$x_1$")
    ax1.set_title("$(x_0,\\,x_1)$")
    ax1.tick_params(labelsize=7)

    # (x0, x2)
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.scatter(x0, x2, **kw)
    ax2.set_xlabel("$x_0$"); ax2.set_ylabel("$x_2$")
    ax2.set_title("$(x_0,\\,x_2)$")
    ax2.tick_params(labelsize=7)

    # (x1, x2)
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.scatter(x1, x2, **kw)
    ax3.set_xlabel("$x_1$"); ax3.set_ylabel("$x_2$")
    ax3.set_title("$(x_1,\\,x_2)$")
    ax3.tick_params(labelsize=7)

    # 3D
    ax4 = fig.add_subplot(gs[1, 1], projection="3d")
    ax4.scatter(x0, x1, x2, s=0.3, alpha=0.3, c=p.color, rasterized=True)
    ax4.set_xlabel("$x_0$", fontsize=7); ax4.set_ylabel("$x_1$", fontsize=7)
    ax4.set_zlabel("$x_2$", fontsize=7)
    ax4.set_title("3D", fontsize=9)
    ax4.tick_params(labelsize=6)

    fname = out_dir / f"tridom_v3_1_portrait_{p.label}.png"
    fig.savefig(fname, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [{p.status:12s}] {p.label} → {fname.name}  (MLE≈{mle_str})")

# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    out_dir = Path(__file__).parent
    print("=" * 60)
    print("TRIDOM v3.1 — Portraits d'attracteurs canonisés")
    print(f"6 portraits × 4 projections chacun")
    print(f"Burn-in : {BURN_STEPS} steps | Trajectoire : {TRAJ_STEPS} steps | DT = {DT}")
    print("=" * 60)

    for p in PORTRAITS:
        eff = eff_sig(p.W)
        print(f"\n[{p.label}] {p.status} — {eff}")
        print(f"  σ={p.sigma} ρ={p.rho} β={p.beta:.3f}")
        plot_portrait(p, out_dir)

    print("\nv3.1 terminé.")

if __name__ == "__main__":
    main()
