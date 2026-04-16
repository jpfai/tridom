# Tridom — A Minimal Signed Triadic Unit for Substrate-Aware Network Dynamics

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19130439.svg)](https://doi.org/10.5281/zenodo.19130439)

**Version:** 0.5.1 — 2026-04  
**Author:** Jean-Paul Faihy  
**Location:** Saujon, Nouvelle-Aquitaine, FR  
**License:** MIT  
**DOI:** `10.5281/zenodo.19130439`

---

## Current status

**Canonical reference block:** `v3.3bis_vps_reference_7nuclei` (1225 points, B = 25, B<0 = 9).

**Canonical targeted branch:** `multi_patch_500pts` — targeted multi-patch refinement built from `B_25points.csv` and `B_neg9points.csv`, with 4 centers and 500 unique points.

**Key results (targeted multi-patch vs reference block):**

| Quantity | Reference block | Targeted multi-patch |
|----------|----------------|---------------------|
| Total points | 1225 | 500 |
| B | 25 | 25 |
| B<0 | 9 | 10 |
| Boundary density | 2.0% | 5.0% |
| Best Δmle | 0.160 | 0.069 |

**Best targeted point:** P0218 (patch `POS_BEST`, coordinates `(10.698, 105.25, 2.475)`).

**Current interpretation:** The boundary behaves as a **thick diagnostic transition zone** rather than a single isolated critical point. Targeted refinement densifies and sharpens this zone locally without overturning the reference reading.

**Branch distinction:** `multi_patch_500pts` (canonical targeted branch) and `pos_best_v2_441pts` (separate local zoom) must not be conflated.

See [RESULTS_STATUS_2026-04.md](RESULTS_STATUS_2026-04.md) for the full scientific status and [BLOCK03_vs_TARGETED_MULTIPATCH500.md](BLOCK03_vs_TARGETED_MULTIPATCH500.md) for the detailed comparison.

---

## Abstract

We introduce **Tridom**, a conceptual and formal unit defined as a strongly connected directed graph on three nodes, endowed with a signed coupling structure (excitatory/inhibitory) and a qualitative dynamical class. Drawing on the network motif literature and on the theory of feedback circuits, we formulate and support the hypothesis that the triadic level constitutes a **minimal grain** at which non-trivial causal organization — multi-stability, oscillation, minimal chaos — becomes generically possible. We further show that this grain is **substrate-invariant at L1** (topology + sign pattern only): the binary sign pattern of couplings is preserved across biological, digital, and logical implementations. This repository provides the formal specification, an enumerated atlas of 78 canonical signed triad topologies classified by dynamical regime, a PyTorch reference implementation with local Hebbian plasticity, and a self-organizing multi-agent system (TridomGroupSystem / Nona²) with endogenous birth and death within an explicit rule scaffold.

---

## Table of Contents

1. [Concept](#1-concept)
2. [Formal Definition](#2-formal-definition)
3. [The Triadic Threshold Hypothesis](#3-the-triadic-threshold-hypothesis)
4. [Atlas of 78 Canonical Topologies](#4-atlas-of-78-canonical-topologies)
5. [Reference Implementation (PyTorch)](#5-reference-implementation-pytorch)
6. [Experimental Results](#6-experimental-results)
7. [TridomGroupSystem — Nona²](#7-tridomgroupsystem--nona)
8. [Positioning relative to the literature](#8-positioning-relative-to-the-literature)
9. [Repository Structure](#9-repository-structure)
10. [Citation](#10-citation)
11. [Contributing](#11-contributing)

---

## 1. Concept

Most research on network motifs treats triadic patterns as *descriptive* building blocks — statistical overrepresentation in biological networks, identified post-hoc. **Tridom elevates the three-node signed motif to an *ontological* unit**: a causal minimal domain whose dynamical identity survives substrate changes.

The key claim:

> *The elementary grain of a connectome is not the isolated neuron, but the causal triad — defined by its dynamics, not its matter.*

---

## 2. Formal Definition

A **Tridom** is a triple **(G, σ, [f])** where:

- **G = (V, E)** with `V = {n₁, n₂, n₃}`, a strongly connected directed graph with at least one feedback cycle.
- **σ : E → {+1, −1}** — binary edge labelling (excitatory `E` / inhibitory `I`).
- **[f]** — equivalence class of local dynamics under topological conjugacy of the phase-space flow.

### Equivalence levels

| Level | Criterion | Verifiability |
|-------|-----------|---------------|
| **L1** — Structural | Same signed graph (topology + σ) | Combinatorial, easy |
| **L2** — Regime | Same attractor family (mono-stable, bi-stable, oscillating, chaotic) | Numerical |
| **L3** — Conjugacy | Homeomorphism of phase spaces | Analytic, case-by-case |

**Invariant core** (substrate-invariant): topology + sign pattern (L1).  
**Realization**: substrate choice (ODE, neural network, logic circuit) + continuous parameters.

---

## 3. The Triadic Threshold Hypothesis

*Based on Thomas–Kaufman structural conditions (Thomas & Kaufman, 2001) and Soulé's proof of the positive circuit condition (Soulé, 2003), with constructive ODE examples.*

For any strongly connected signed directed graph G on n nodes:

| n | Accessible dynamics | Remark |
|---|---------------------|--------|
| **1** | Mono-stability only | No relational structure |
| **2** | Mono- or bi-stability | No generic periodic oscillation or chaos |
| **3** | All families: mono-, multi-stability, oscillation, minimal chaos | **Under suitable realizations** (stable under parameter perturbation) |

**Corollary (supported hypothesis):** n = 3 is the smallest integer at which substrate-invariant non-trivial causal organization becomes possible in the strong sense.<!-- TODO: verify strength of "supported" vs "conjecture" once formal proof is complete -->

---

## 4. Atlas of 78 Canonical Topologies

File: `tridom_atlas.json`

Exhaustive enumeration of strongly connected signed directed graphs on 3 nodes (no self-loops), up to node permutation. Dynamical regime classified via ODE integration (tanh nonlinearity, 8 random initial conditions).

| Regime | Count | % |
|--------|-------|---|
| Mono-stable | 56 | 71.8% |
| Oscillating | 15 | 19.2% |
| Chaotic candidates | 7 | 9.0% |
| **Total** | **78** | 100% |

> **Note:** The dynamical classification is protocol-relative: ODE integration with tanh nonlinearity, 8 random initial conditions, 500 time steps. Different protocols may yield different regime assignments.<!-- TODO: confirm step count matches actual simulation parameters -->

### Key examples

| Topology ID | Arcs | E | I | Regime | Typical use |
|-------------|------|---|---|--------|-------------|
| `01I.12I.20I` | 3 | 0 | 3 | Oscillating | Internal clock, CPG |
| `01E.12E.20I` | 3 | 2 | 1 | Chaotic candidates | Exploration, variability |
| `01E.02E.10E.21I` | 4 | 3 | 1 | Oscillating | Regulated rhythm |
| `01E.02E.10E.12E.20I` | 5 | 4 | 1 | Chaotic candidates | Sensitivity to initial conditions |

### JSON schema

```json
{
  "id": "01I.12I.20I",
  "n_edges": 3,
  "n_excit": 0,
  "n_inhib": 3,
  "edges": [[0,1],[1,2],[2,0]],
  "signs": {"0,1": -1, "1,2": -1, "2,0": -1},
  "regime_l2": "oscillating",
  "description": "Converges to a stable limit cycle. Ideal for internal rhythms.",
  "example_use": "Internal clock, CPG, rhythms."
}
```

---

## 5. Reference Implementation (PyTorch)

### N3D — Minimal triadic cell

```python
class N3D(nn.Module):
    """
    3 internal states x ∈ R³
    Recurrent matrix W ∈ R^{3×3} (strongly connected, signed)
    Dynamics: x_{t+1} = tanh(W · x_t + b + u_t)
    Local Hebbian plasticity: ΔW_ij = η · x_i · x_j − λ · W_ij
    """
```

**Calibrated parameters (TEST_009):** `eta=1e-3`, `w_decay=1e-5`

### Vitality metric

```python
vitality = 0.5 * (activity + regularity)
# activity   = fraction of steps where max|x_t| > x_min  (≠ rest)
# regularity = 1 - std(max|x_t|) / (mean(max|x_t|) + ε)  (≠ divergence)
```

A Tridom is **alive** if `vitality > threshold`; it **dies** (self-extinguishes) otherwise — no external oracle.

---

## 6. Experimental Results

### TEST_008 — Comparative dynamics N1D / N2D / N3D with Hebbian plasticity

| Scenario | Winner | Key insight |
|----------|--------|-------------|
| Simple regulation | N1D | Direct response, no memory needed |
| High noise | N2D | Bidirectional feedback filters noise |
| Delay k=2,3 | N3D | Triadic loop encodes short/mid memory |
| **Strong hysteresis** | **N3D** | **Factor ×1.64 over N1D** — suggests directional encoding capability |

### TEST_009 — Calibration grid (eta × w_decay)

30 configurations tested on delays k=4 and k=5.  
**Recommended (local optimum in grid tested):** `eta=1e-3`, `w_decay=1e-5` — N3D wins on both delays simultaneously.<!-- TODO: broader grid search or Bayesian optimization may yield better parameters -->

```
eta=1e-03, w_decay=1e-05:
  k=4 → N1D=-66.88  N2D=-55.51  N3D=-52.44  ★
  k=5 → N1D=-55.48  N2D=-62.45  N3D=-53.79  ★
```

Full results: `test009_calibration.csv`

---

## 7. TridomGroupSystem — Nona²

File: `tridom_tgs_v2.py`

A self-organizing population of Tridom groups with **endogenous lifecycle within an explicitly specified rule scaffold**.

### Architecture

```
Level 1 : N1D  (1 neuron)          → simple regulation
Level 2 : N2D  (2 neurons)         → noise filtering, short memory
Level 3 : N3D  (3 neurons)         → hysteresis, delays, oscillation
Level 4 : Nona (3 groups × N3D)    → collective robustness
Level 5 : Nona² (up to 9 groups)   → auto-replication, death, evolution
```

### Lifecycle rules (no external oracle)

| Rule | Condition | Action |
|------|-----------|--------|
| **Birth** | `vitality > 0.80` for `BIRTH_WINDOW` steps | Spawn child group (copy + Gaussian mutation σ=0.1) |
| **Death** | `vitality < 0.25` for `2×DEATH_WINDOW` steps | Remove group |
| **Resilience** | `n_active_groups ≥ MIN_GROUPS` | Last group is immune to death |
| **Cap** | `n_active_groups ≤ MAX_GROUPS = 9` | 27 Tridoms maximum |

### Demo results (3 phases: hysteresis → extreme noise → recovery)

| Phase | Groups | Tridoms | Vitality | Events |
|-------|--------|---------|----------|--------|
| Hysteresis (t=0..200) | 12 (peak, before cap) | 36 | 0.957 | 9 births |
| Extreme noise (t=200..400) | 1 (survivor) | 3 | 0.195 | 11 deaths |
| Recovery (t=400..600) | 8 | 24 | 0.797 | 7 births |

> Note: the peak of 12 groups was reached transiently during the first phase before the `MAX_GROUPS=9` cap was enforced in steady state. The cap limits concurrent active groups, not the cumulative birth count.

The sole survivor (`713dc102`) replicates 3 generations during recovery, rebuilding a population of 8 groups with vitality 0.797.

---

## 8. Positioning relative to the literature

| Concept | Tridom | Classical approach |
|---------|--------|--------------------|
| Grain | Triad (3 nodes) as explicit formal unit | Neuron or full network |
| Substrate | Structurally invariant at L1 (signed topology) | Substrate-specific |
| Dynamics | Equivalence class, not parameter set | Fixed architecture |
| Taxonomy | 78 canonical classes, open atlas | Descriptive motif statistics |
| Agency | Endogenous birth/death within rule scaffold (vitality) | External training loop |

**Key references:**
- Milo et al. (2002) — *Network motifs: simple building blocks of complex networks*, Science
- Alon (2007) — *Network motifs: theory and experimental approaches*, Nature Reviews Genetics
- Thomas & Kaufman (2001) — *Multistationarity, the basis of cell differentiation and memory*, Chaos (AIP)
- Soulé (2003) — *Graphic requirements for multistationarity*, ComplexUs
- Tononi et al. — Integrated Information Theory (IIT) — causal irreducibility
- Krauss et al. — Exhaustive analysis of 3-neuron binary motifs

**Tridom's contribution:** naming + formal substrate-invariant definition + open atlas + reference implementation with endogenous lifecycle.

---

## 9. Repository Structure

```
Tridom/
├── README.md                      ← this file
├── tridom_atlas.json              ← atlas of 78 canonical topologies (open data)
├── tridom_atlas.py                ← enumeration + ODE classification script
├── tridom_tgs_v2.py               ← TGS Nona² (birth/death/replication)
├── tridom_promotion.py            ← AdaptiveTridomAgent + Nona (v1)
├── test_tridom_calibration.py     ← TEST_009 calibration grid
├── test009_calibration.csv        ← calibration results
├── TRIDOM_DYNAMIQUE_N123.md       ← full dynamic reference documentation
├── TRIDOM_SESSION_LOG.md          ← session journal (TEST_001 to TEST_009)
└── spec/
    └── tridom_spec.md             ← formal specification (L1, L2, L3)
```

---

## 10. Citation

If you use Tridom in your work, please cite:

```bibtex
@software{faihy2026tridom,
  author    = {Faihy, Jean-Paul},
  title     = {Tridom: A Minimal Signed Triadic Unit for Substrate-Aware Network Dynamics},
  year      = {2026},
  version   = {0.4},
  url       = {https://github.com/jpfai/tridom},
  doi       = {10.5281/zenodo.19130439}
}
```

---

## 11. Contributing

Tridom is an open research project. Issues, pull requests, and forks are welcome.

Suggested contributions:
- Extend the atlas to n=4 (four-node motifs)
- Implement Φ (IIT phi) computation for binary Tridoms
- Benchmark Tridom-RNN against standard GRU/LSTM on memory tasks
- Formal proof of the Triadic Threshold Hypothesis (Thomas–Kaufman / Soulé framework)

---

*"The elementary grain of a connectome is not the isolated neuron, but the causal triad — defined by its dynamics, not its matter."*
