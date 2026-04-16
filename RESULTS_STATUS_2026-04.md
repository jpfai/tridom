# RESULTS_STATUS_2026-04

**Project:** Tridom  
**Status date:** 2026-04  
**Purpose:** current scientific status reference for GitHub and repository communication

---

## 1. Scope

This document summarizes the current scientific reading of the Tridom boundary-refinement programme after archive clarification and targeted branch separation.

It is not a replacement for the README.  
Its role is to state, compactly and rigorously:

- what is the current canonical reference block,
- what the targeted refinement adds,
- what is established,
- what remains open.

---

## 2. Canonical hierarchy

The current scientific reading must distinguish three levels:

1. `v3.3_upstream`
2. `v3.3bis`
   - `v3.3bis_preliminary_light`
   - `v3.3bis_vps_reference_7nuclei`
3. targeted refinement
   - `multi_patch_500pts`
   - `pos_best_v2_441pts`

The current canonical reference is:

- **reference block:** `v3.3bis_vps_reference_7nuclei`
- **canonical targeted branch:** `multi_patch_500pts`

The branch `pos_best_v2_441pts` is a separate local zoom and must not be conflated with the parent run of `multi_patch_500pts`.

---

## 3. Reference block: `v3.3bis_vps_reference_7nuclei`

### Established facts

- Total points: `1225`
- `B = 25`
- `B<0 = 9`
- `UNSTABLE = 0`

This block confirms that:

- `B` is non-empty on all 7 nuclei,
- `B<0` appears on 6 nuclei out of 7,
- the boundary is not well described as a single compact critical point.

### Current reading

The most coherent interpretation is that the system exhibits a **thick diagnostic transition zone**, not a single isolated threshold point.

---

## 4. Targeted refinement: `multi_patch_500pts`

### Construction

The canonical targeted branch is built from:

- `B_25points.csv`
- `B_neg9points.csv`

through targeted refinement planning, yielding:

- `4` selected centers,
- `500` unique points,
- `4` patches × `125` points.

### Established facts

- Total points: `500`
- `B = 25`
- `B<0 = 10`

Compared with block 03:

- `B` count is preserved,
- `B<0` increases from `9` to `10`,
- boundary density increases from `25 / 1225 = 2.0%` to `25 / 500 = 5.0%`,
- the best local robustness improves from `Δmle = 0.160` to `Δmle = 0.069`.

### Patch distribution

- `POS_BEST`: `B = 9`, `B<0 = 4`
- `NEG_NEG3`: `B = 8`, `B<0 = 2`
- `NEG_NEG1`: `B = 6`, `B<0 = 3`
- `B_CENTER_EMPIRICAL`: `B = 2`, `B<0 = 1`

### Best targeted point

- `P0218`
- patch: `POS_BEST`
- coordinates: `(10.698, 105.25, 2.475)`
- `Δmle = 0.069`

---

## 5. Scientific comparison: block 03 vs targeted multi-patch

### What remains invariant

The targeted refinement does not destroy the boundary picture:

- `B` remains present,
- the transition remains nontrivial,
- the phenomenon is not reduced to numerical blow-up.

### What improves

The targeted branch adds real information:

- higher density of candidate boundary points,
- additional negative candidate (`B<0 = 10`),
- improved best local robustness,
- clearer concentration around `POS_BEST`.

### What this means

The targeted branch should be read as a **local densification and clarification** of the boundary, not as a contradiction of the reference block.

---

## 6. Current consolidated interpretation

The cumulative evidence does **not** support the idea of a single isolated critical point.

It supports instead the existence of a **thick diagnostic transition zone**:

- numerically bounded,
- dynamically nontrivial,
- sensitive to the Lyapunov / renormalization protocol,
- locally sharpened by targeted refinement.

---

## 7. What is established vs open

### Established
- existence of a nontrivial transition zone,
- persistence of `B` candidates across refinement,
- local improvement under targeted multi-patch refinement,
- current canonical reference hierarchy.

### Still open
- fine geometric connectivity of the frontier,
- whether the boundary forms a sheet, ribbon, fragmented set, or connected pockets,
- broader continuation beyond the currently refined region.

---

## 8. Repository reading rule

For the current scientific status, the canonical reading order is:

1. `TRIDOM_ARCHIVE/03_v3.3bis_vps_reference_7nuclei/`
2. `TRIDOM_ARCHIVE/04_targeted_extraction/multi_patch_500pts/`
3. `TRIDOM_ARCHIVE/05_targeted_input_grid/multi_patch_500pts/`
4. `TRIDOM_ARCHIVE/06_targeted_run_results/multi_patch_500pts/`

The branch `pos_best_v2_441pts` must be treated separately.

---

## 9. Communication rule for GitHub

When communicating the current status publicly, the correct formulation is:

> The current reference block is `v3.3bis_vps_reference_7nuclei`.  
> Targeted multi-patch refinement preserves `B = 25`, increases `B<0` from `9` to `10`, raises boundary density from `2.0%` to `5.0%`, and improves the best local robustness from `Δmle = 0.160` to `Δmle = 0.069`.  
> The boundary is therefore best read as a thick diagnostic transition zone rather than a single critical point.

---

## 10. Status conclusion

At this stage, Tridom has:

- a clarified archive structure,
- a stable reference block,
- a targeted multi-patch branch with identified canonical parent results,
- and a coherent current interpretation.

The main open problem is no longer detection, but fine geometric characterization.