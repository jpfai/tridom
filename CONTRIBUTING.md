# Contributing to Tridom

Thank you for your interest in Tridom. This document describes the open research directions and how to contribute.

Tridom is an open research project. Contributions are welcome from researchers, mathematicians, computational neuroscientists, and engineers — regardless of institutional affiliation.

---

## Open Research Directions

The following five directions are explicitly identified as open contributions in the preprint ([arXiv preprint](https://github.com/jpfai/tridom), [Zenodo v0.4](https://doi.org/10.5281/zenodo.19130439)):

### 1. Formal Proof of the Triadic Threshold Theorem
**Status:** Proof sketch (constructive ODE examples).  
**Goal:** A complete formal proof within the Thomas–Kaufman / Soulé framework establishing that n = 3 is the minimal size for substrate-invariant non-trivial causal organisation.  
**Skills needed:** Dynamical systems theory, algebraic graph theory, feedback circuit analysis.  
**Reference:** Thomas & Kaufman (2001), Soulé (2003).  
→ See [Issue #1](https://github.com/jpfai/tridom/issues/1)

---

### 2. Extension of the Atlas to n = 4
**Status:** Atlas complete for n = 3 (78 canonical topologies).  
**Goal:** Enumerate and classify all strongly connected signed directed graphs on 4 nodes by ODE dynamical regime. The combinatorial space is substantially larger.  
**Skills needed:** Graph enumeration, ODE numerical integration, Python.  
**Starting point:** [`tridom_atlas.py`](tridom_atlas.py) — the n=3 enumeration and classification pipeline.  
→ See [Issue #2](https://github.com/jpfai/tridom/issues/2)

---

### 3. Benchmark Tridom-RNN against GRU / LSTM
**Status:** Evaluated on delay prediction and hysteresis tasks only (TEST_008, TEST_009).  
**Goal:** Systematic benchmarking of N3D (Tridom PyTorch cell) against GRU and LSTM on standard sequence tasks (e.g., copying, adding, sequential MNIST).  
**Skills needed:** PyTorch, recurrent neural networks, benchmark design.  
**Starting point:** [`tridom_promotion.py`](tridom_promotion.py) — AdaptiveTridomAgent (N1D→N2D→N3D).  
→ See [Issue #3](https://github.com/jpfai/tridom/issues/3)

---

### 4. Integrated Information (IIT phi) for Binary Tridoms
**Status:** Not yet computed.  
**Goal:** Compute phi (Tononi's integrated information) for all 78 canonical binary Tridoms and examine whether phi correlates with dynamical regime (monostable / oscillating / chaotic).  
**Skills needed:** Information theory, IIT framework (PyPhi or equivalent), Python.  
**Reference:** Tononi et al. (2016), PyPhi library.  
→ See [Issue #4](https://github.com/jpfai/tridom/issues/4)

---

### 5. Biological Validation — Tridom Classes in Published Connectomes
**Status:** Theoretical substrate-invariance claim; no biological validation yet.  
**Goal:** Identify which of the 78 canonical Tridom topologies are over-represented in published connectomes (C. elegans, Drosophila, mouse cortex) and compare their dynamical class with known circuit functions.  
**Skills needed:** Connectomics, network analysis, Python/NetworkX.  
**Data:** [`tridom_atlas.json`](tridom_atlas.json) — 78 topologies with regime labels (open data).  
→ See [Issue #5](https://github.com/jpfai/tridom/issues/5)

---

## How to Contribute

1. **Read the preprint** — all theoretical foundations are described there.
2. **Pick an open direction** — browse the [Issues](https://github.com/jpfai/tridom/issues) to find one that matches your expertise.
3. **Open a discussion** — comment on the relevant Issue before starting work to avoid duplication.
4. **Fork the repository** and work on a dedicated branch.
5. **Submit a Pull Request** with a clear description of what was done and how results were validated.

There is no formal requirement for institutional affiliation. Independent researchers are welcome.

---

## Code Standards

- Python 3.10+, PyTorch 2.x
- Follow the existing code style (see [`tridom_promotion.py`](tridom_promotion.py) as reference)
- All new experiments should include a reproducibility note (random seed, hardware, runtime)
- Results should be saved as CSV and committed alongside the code

---

## Contact

**Jean-Paul Faihy**  
Independent Researcher, Saujon, Nouvelle-Aquitaine, France  
faihy.jeanpaul@gmail.com  
GitHub: [jpfai](https://github.com/jpfai)

---

## Citation

If you use Tridom in your work, please cite:

```
Faihy, J.-P. (2026). Tridom: A Minimal Causal Unit for Substrate-Invariant
Network Dynamics. Zenodo. https://doi.org/10.5281/zenodo.19130439
```

---

*This project is open source under the MIT licence.*
