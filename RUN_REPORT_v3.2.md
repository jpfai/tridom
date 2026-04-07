# v3.2 / v3.2bis — Robust local validation of effective complex classes C1 / C2

**Status:** numerical validation only.
These results provide strong evidence but are not an analytical proof of chaos.

---

## What was done

Version v3.2 was designed to reassess the effective complex/chaotic classes previously identified in v2 using a stronger estimator of the maximal Lyapunov exponent (MLE):

- Benettin / variational equation method
- RK4 integration
- long burn-in + long measurement window
- local 3×3×3 grids around four retained anchors
- 12 initial conditions per grid point

The four anchors were:

| Label | Topology | Perm | (σ, ρ, β) |
|-------|----------|------|-----------|
| C1a | topo_47 | (0,1,2) | (10, 28, 8/3) |
| C1b | topo_57 | (0,1,2) | (16, 45, 4) |
| C2a | topo_41 | (0,1,2) | (10, 99.6, 8/3) |
| C2b | topo_44 | (0,1,2) | (16, 45, 4) |

Each case was classified using `bounded_frac`, `moving_frac`, `pos_lyap_frac`, `mle_mean`, and `mle_median`.

A case was classified as Complex only when trajectories were:
- bounded,
- dynamically active,
- and associated with a robustly positive MLE.

A stricter flag `robust_complex=True` was also used.

---

## Global outcome (v3.2)

Out of 108 tested cases:

- **105 / 108** were classified as `robust_complex=True`
- **3 / 108** were non-robust
- all 3 non-robust cases occurred on C2a

This already shows that the complex behavior is not punctual: it persists over small local parameter neighborhoods around the retained anchors.

---

## Anchor-wise interpretation

### C1a

C1a is confirmed as a locally robust complex regime.
Median MLE values remain clearly positive across the tested neighborhood, typically around 0.8–1.0.

### C1b

C1b is the strongest confirmation in the study.
The full local grid remains robustly complex, with median MLE values typically around 1.4–1.6.

### C2a

C2a is mostly confirmed but contains an interesting localized fragility.
Three cases fall out of the robustly complex class and become oscillatory/non-robust:

1. σ=10.00, ρ=99.60, β=2.667 (mle_median ≈ −0.07)
2. σ=11.00, ρ=99.60, β=2.933 (mle_median ≈ +0.02)
3. σ=11.00, ρ=104.58, β=2.667 (mle_median ≈ −0.01)

This is not a failure of the method.
It is the most scientifically interesting feature of the study: C2a appears to lie near a genuine dynamic boundary.

### C2b

C2b is also strongly confirmed as a robust complex class, with median MLE values comparable to C1b.

---

## v3.2bis — MLE robustness check

Version v3.2bis added a targeted sensitivity test on the renormalization interval used in the Benettin estimator:

- RENORM_EVERY ∈ {5, 10, 20}

This test was not run as a new global scan, but on representative robust and critical cases.

### Main outcome

- For the robust zones (especially C1b and C2b), the MLE remains stable under renormalization changes:
  - typical variation: ΔMLE ≈ 0.01–0.05
- For the critical C2a cases:
  - one case remains negative regardless of RENORM_EVERY
  - one case fluctuates around zero
  - one case remains positive but with high sensitivity (ΔMLE ≈ 0.26)

This is exactly the expected pattern for a genuine transition zone:
- the robust zones remain robust,
- the critical zone remains critical.

---

## Main conclusion

The combined v3.2 / v3.2bis result is the following:

> The effective classes C1 and C2 are not isolated numerical artifacts.
> They correspond to numerically robust and locally persistent complex regimes under a stronger variational MLE estimator.

More precisely:

- C1a, C1b, C2b are confirmed as robust local complex regions
- C2a defines a genuine transition boundary between robustly complex and oscillatory behavior
- the original v2 signal survives a significantly stronger validation protocol
- the remaining fragility is structured, not random

---

## Epistemic status

These results justify the claim of:

- robust numerical evidence for locally persistent complex dynamics
- compatibility with chaos in a strong numerical sense
- structured transition behavior at C2a

They do not yet justify the stronger claim of:

- analytical proof of chaos
- complete theoretical characterization of the attractors
- global classification beyond the tested local neighborhoods

---

## Why C2a matters

The most important result of this study is not simply that 105 cases are robust.

The central scientific result is:

> Under a stronger estimator and a sensitivity test, C2a does not collapse into noise.
> Instead, it reveals a structured transition region where the sign and stability of the MLE become sensitive.

This makes C2a the main target for the next stage.

---

## Next step

The most coherent continuation is not another broad scan.

The natural next step is:

> v3.3 — boundary study around C2a

with a finer local refinement around the three critical points, in order to characterize more precisely the transition between:
- robustly complex behavior,
- weak/intermittent chaos,
- and oscillatory dynamics.
