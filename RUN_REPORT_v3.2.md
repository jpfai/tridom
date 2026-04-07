# v3.2 — Robust local validation of C1 / C2

**Status:** numerical validation only. Not an analytical proof.

---

## What v3.2 does

v3.2 replaces the previous chaos indicator with a more robust estimate of the maximal Lyapunov exponent (MLE) using the Benettin / variational equation method, and tests local persistence around four previously identified anchors.

## Anchors

| Label | Topology | Perm | (σ, ρ, β) |
|-------|----------|------|-----------|
| C1a | topo_47 | (0,1,2) | (10, 28, 8/3) |
| C1b | topo_57 | (0,1,2) | (16, 45, 4) |
| C2a | topo_41 | (0,1,2) | (10, 99.6, 8/3) |
| C2b | topo_44 | (0,1,2) | (16, 45, 4) |

## Protocol

For each anchor:
- local 3×3×3 grid
- 12 initial conditions per grid point
- RK4 integration
- long burn-in + long measurement window
- MLE via variational equation + periodic renormalization

## Global result

Out of 108 tested cases:
- **105 / 108** are `robust_complex=True`
- **3 / 108** are non-robust
- all 3 non-robust cases occur on C2a

## Interpretation by class

| Class | Status |
|-------|--------|
| C1a | Robustly complex in the tested local neighborhood |
| C1b | Strongest confirmation; robust across the full tested grid |
| C2a | Mostly robust, with a small local oscillatory boundary |
| C2b | Robust across the full tested grid |

## Main conclusion

v3.2 provides strong numerical evidence that the effective classes C1 and C2 are not isolated artifacts, but locally persistent complex regimes under a stronger MLE estimation protocol.

In particular:
- the complex behavior is **not punctual**
- it persists over small local parameter regions
- the signal detected in v2 survives a more demanding quantitative test

## Important limitation

This is robust numerical evidence, **not an analytical proof of chaos**.

## Next step

A natural continuation is a targeted boundary study around C2a, to characterize more precisely the transition between robustly complex and oscillatory behavior.
