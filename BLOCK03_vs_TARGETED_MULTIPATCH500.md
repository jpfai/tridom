# BLOCK03_vs_TARGETED_MULTIPATCH500

**Project:** Tridom  
**Comparison date:** 2026-04  
**Purpose:** final scientific comparison between the canonical reference block (`03_v3.3bis_vps_reference_7nuclei`) and the canonical targeted branch (`multi_patch_500pts`)

---

## 1. Scope

This document compares:

- the canonical reference block:
  - `TRIDOM_ARCHIVE/03_v3.3bis_vps_reference_7nuclei/`
- the canonical targeted refinement branch:
  - `TRIDOM_ARCHIVE/04_targeted_extraction/multi_patch_500pts/`
  - `TRIDOM_ARCHIVE/05_targeted_input_grid/multi_patch_500pts/`
  - `TRIDOM_ARCHIVE/06_targeted_run_results/multi_patch_500pts/`

Its goal is to answer a precise question:

> What does the targeted multi-patch refinement add, scientifically, relative to the current reference block?

This document does **not** compare the targeted branch with `pos_best_v2_441pts`, which is a separate local zoom.

---

## 2. Canonical status of the two compared objects

### 2.1 Reference block

The current scientific reference block is:

- `v3.3bis_vps_reference_7nuclei`

This block must be treated as the canonical baseline for current boundary interpretation.

### 2.2 Targeted branch

The current canonical targeted branch is:

- `multi_patch_500pts`

This branch is not a replacement for block 03.  
It is a refinement layer built from block 03 candidate extraction.

---

## 3. Data provenance

### 3.1 Reference block

The reference block corresponds to the dense `v3.3bis` run over 7 nuclei:

- total points: `1225`
- canonical status: reference
- reading level: boundary reference before targeted refinement

### 3.2 Targeted branch

The targeted multi-patch branch is built as follows:

1. extraction of:
   - `B_25points.csv`
   - `B_neg9points.csv`
2. targeted refinement planning:
   - `refine_centers.csv`
   - `refine_manifest.json`
   - `refine_points.csv`
3. targeted run on `500` explicit points
4. extraction of:
   - `B_25points_targeted_full.csv`
   - `B_neg10points_targeted_full.csv`

The canonical parent raw results file is:

- `1775924962009_tridom_v3_3bis_targeted_CSV_TARGETED_results.csv`

This file is the raw parent of the targeted multi-patch result interpretation.

---

## 4. Numerical comparison

## 4.1 Global counts

| Quantity | Block 03 (`v3.3bis_vps_reference_7nuclei`) | Targeted `multi_patch_500pts` |
|----------|--------------------------------------------|-------------------------------|
| Total points | 1225 | 500 |
| `B` | 25 | 25 |
| `B<0` | 9 | 10 |
| `UNSTABLE` | 0 | 0 |

### Immediate reading

- the targeted branch does **not** increase the total count of `B`;
- it **does** increase the count of `B<0` from `9` to `10`;
- it works on a **smaller and denser** region of parameter space.

---

## 4.2 Boundary density

### Block 03
- `B density = 25 / 1225 ≈ 2.0%`

### Targeted multi-patch
- `B density = 25 / 500 = 5.0%`

### Interpretation

The targeted branch more than doubles the density of boundary candidates.

This is a strong indication that the refinement is not random:
it concentrates computational effort on a region where boundary structure is more likely to appear.

---

## 4.3 Negative boundary density

### Block 03
- `B<0 density = 9 / 1225 ≈ 0.735%`

### Targeted multi-patch
- `B<0 density = 10 / 500 = 2.0%`

### Interpretation

The targeted branch significantly increases the concentration of negative-side candidates.

This does **not** prove a single crossing surface,
but it improves access to the negative side of the transition zone.

---

## 4.4 Best local robustness

### Block 03
Best reference-level local candidate:
- best `Δmle = 0.160`

### Targeted multi-patch
Best local candidate:
- `P0218`
- patch: `POS_BEST`
- coordinates: `(10.698, 105.25, 2.475)`
- best `Δmle = 0.069`

### Interpretation

This is the clearest local improvement yielded by the targeted branch.

The targeted refinement does not merely re-sample the same information:
it yields a numerically cleaner best boundary candidate.

---

## 5. Internal structure of the targeted branch

Patch distribution:

| Patch | `B` | `B<0` |
|-------|----:|------:|
| `POS_BEST` | 9 | 4 |
| `NEG_NEG3` | 8 | 2 |
| `NEG_NEG1` | 6 | 3 |
| `B_CENTER_EMPIRICAL` | 2 | 1 |

### Interpretation

The targeted branch is not uniformly informative.

Its strongest contribution is concentrated in:
- `POS_BEST`
- then `NEG_NEG3`
- then `NEG_NEG1`

The empirical-center patch contributes less than the patch-centered local refinements.

This suggests that the boundary structure is not simply centered on the empirical barycenter of `B`,
but is more effectively resolved near selected local candidate regions.

---

## 6. Scientific interpretation

## 6.1 What remains unchanged

The targeted branch does **not** overturn the reference reading.

The following remain true:

- the system exhibits a nontrivial boundary region;
- the phenomenon is not reducible to a numerical blow-up;
- the transition is not adequately described by a single isolated point.

## 6.2 What improves

The targeted branch adds three things:

1. **higher density of boundary candidates**
2. **more negative-side access**
3. **better best local robustness**

These are real gains, not only cosmetic reorganizations.

## 6.3 What this means conceptually

The targeted refinement supports the idea that the boundary behaves as a:

> **thick diagnostic transition zone**

rather than as a:
- single point,
- single exact threshold,
- or already fully resolved surface.

The refinement sharpens the local picture but does not yet close the geometric question.

---

## 7. What is proved, probable, and still open

### Established
- block 03 is the current reference block;
- targeted multi-patch preserves `B = 25`;
- targeted multi-patch increases `B<0` from `9` to `10`;
- targeted multi-patch increases boundary density from `2.0%` to `5.0%`;
- targeted multi-patch improves the best local `Δmle` from `0.160` to `0.069`.

### Strongly suggested
- the most promising local zone is now concentrated around `POS_BEST`;
- the boundary is better thought of as an extended local structure than as a single point.

### Still open
- fine connectivity between local patches;
- whether the boundary forms a sheet, ribbon, fragmented structure, or connected pockets;
- parameter continuation beyond the currently refined region.

---

## 8. Final comparison statement

The correct final comparison is:

> Relative to the canonical reference block `v3.3bis_vps_reference_7nuclei`, the targeted branch `multi_patch_500pts` does not change the global interpretation of the phenomenon. It confirms and densifies it. The total number of `B` candidates remains `25`, the number of negative candidates increases from `9` to `10`, the boundary density rises from `2.0%` to `5.0%`, and the best local robustness improves from `Δmle = 0.160` to `Δmle = 0.069`. The cumulative evidence therefore supports the interpretation of the Tridom frontier as a thick diagnostic transition zone rather than a single isolated critical point.

---

## 9. Operational consequence

For repository communication and GitHub status reporting:

- `03_v3.3bis_vps_reference_7nuclei` must remain the **reference block**
- `multi_patch_500pts` must be presented as the **canonical refinement branch**
- `pos_best_v2_441pts` must remain explicitly separate

This distinction is mandatory for scientific clarity and repository traceability.