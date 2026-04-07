# v3.2 — Quantitative validation of effective chaotic classes C1 / C2

## Status

Numerical validation only.
This is not an analytical proof of chaos.

## Objective

Version v3.2 was designed to quantitatively validate the two effective chaotic classes previously identified in v2 by replacing the former indicator with a more robust estimate of the maximal Lyapunov exponent (MLE) using the Benettin / variational equation method, and by testing local persistence around four retained anchor points.

## Scope

This is not a new global scan.
The protocol is restricted to four local anchors:

- **C1a**: topo_47, perm=(0,1,2), (σ,ρ,β)=(10,28,8/3)
- **C1b**: topo_57, perm=(0,1,2), (σ,ρ,β)=(16,45,4)
- **C2a**: topo_41, perm=(0,1,2), (σ,ρ,β)=(10,99.6,8/3)
- **C2b**: topo_44, perm=(0,1,2), (σ,ρ,β)=(16,45,4)

For each anchor, a local 3×3×3 grid was explored:

- σ ∈ {0.9, 1.0, 1.1} σ₀
- ρ ∈ {0.95, 1.0, 1.05} ρ₀
- β ∈ {0.9, 1.0, 1.1} β₀

Each grid point was tested with:

- 12 initial conditions
- RK4 integration
- long burn-in
- long measurement window
- MLE estimation via variational equation + periodic renormalization

## Classification rule

Each case was classified using:

- `bounded_frac`
- `moving_frac`
- `pos_lyap_frac`
- `mle_mean`
- `mle_median`

Regimes:

- **Unstable**: too few bounded trajectories
- **Fixed**: bounded but weak motion
- **Oscillating**: bounded + moving, but no robust positive MLE
- **Complex**: bounded + moving + robust positive MLE

A case is marked `robust_complex=True` only under a stricter combined criterion.

## Main results

### Global outcome

Out of 108 tested cases:

- 105 / 108 were classified as `robust_complex=True`
- only 3 / 108 were non-robust, all on C2a
- no anchor collapsed globally into fixed or unstable behavior

### Anchor-wise interpretation

**C1a** — Confirmed as a locally robust complex regime. Across the tested neighborhood, trajectories remain bounded and moving, with clearly positive median MLE values.

**C1b** — Strongest confirmation in the study. The whole tested neighborhood is robustly complex, with high positive MLE values throughout.

**C2a** — Mostly confirmed, but shows a localized fragility. Three points in the local grid were classified as Oscillating instead of robustly complex:

1. σ=10.00, ρ=99.60, β=2.667
2. σ=11.00, ρ=99.60, β=2.933
3. σ=11.00, ρ=104.58, β=2.667

This suggests that C2a lies near a local transition boundary between oscillatory and robustly complex behavior.

**C2b** — Strongly confirmed as a robust complex class over the full tested local grid.

## Scientific conclusion

The v3.2 results strongly support the following statement:

> The classes C1 and C2, previously identified in v2 as effective chaos candidates, are confirmed in v3.2 as numerically robust and locally persistent complex regimes under a stronger MLE estimation protocol based on the Benettin / variational equation method.

More precisely:

- the observed complex behavior is not punctual
- it persists over small local parameter regions
- the former signal of chaos from v2 does not appear to be a weak artifact of the previous estimator
- C2a remains the only anchor showing a limited local loss of robustness

## Epistemic status

These results justify the claim of:

- robust numerical evidence for locally persistent complex dynamics
- compatibility with chaos in a strong numerical sense

They do not yet justify the stronger claim of:

- analytical proof of chaos
- complete theoretical characterization of the chaotic sets

## Next step

The most coherent continuation is not another broad scan, but a targeted boundary study around C2a, in order to characterize more precisely the transition between robustly complex and oscillatory behavior.
