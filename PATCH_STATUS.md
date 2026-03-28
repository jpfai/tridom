# PATCH_STATUS.md — Tridom v0.5 Working

*Manuscrit de travail reconstitué à partir d'une extraction PDF ; stabilisé éditorialement ; non destiné à la publication directe (source LaTeX native non disponible).*

## Sections patchées

| Section | Patch appliqué | Commit |
|---|---|---|
| Titre | Substrate-Invariant → Substrate-Aware | `4d98715` |
| Abstract | prove → formulate and support; substrate-invariant → L1; fully endogenous → rule scaffold; generically → accessible; minimal chaos → chaotic candidates | `4d98715` + `d6d2a32` |
| §3.2 (L2) | Yes (generic) → Conditionally/generically under realization constraints | `4d98715` |
| §4 (Threshold) | Theorem → Hypothesis; Corollary → conjectural; Proof sketch → Evidence sketch; establishes → constructive support; Generically stable → Stable | `4d98715` + `d6d2a32` |
| §5 (Atlas) | Chaos → Chaotic candidates; ajout note protocol-relative | `4d98715` |
| §7 (TGS) | fully endogenous → within rule scaffold | `4d98715` |
| §8 (Positioning) | Invariant by construction → Structurally invariant at L1 | `4d98715` |
| §9 (Discussion) | Theorem → Hypothesis; separates faits/conjectures/limites | `4d98715` + `d6d2a32` |
| §10 (Conclusion) | Ton démonstratif → programme minimal cohérent | `4d98715` |

## Critères épistémiques validés

| Critère | Statut |
|---|---|
| theorem/prove/establishes → 0 (hors citations historiques) | ✅ |
| substrate-invariant → L1 uniquement | ✅ |
| chaos → chaotic candidates (atlas) | ✅ |
| fully endogenous → absent | ✅ |
| generically → absent du Threshold | ✅ |
| Inférences fortes non démontrées → absentes | ✅ |

## Points ouverts (non bloquants pour le gel)

- [ ] Pipeline Lyapunov complet (QR ré-orthogonalisation)
- [ ] Benchmarking externe (GRU/LSTM)
- [ ] Preuve formelle Triadic Threshold
- [ ] Note séparée m5_extension
- [ ] Source LaTeX native (recherche/Reconstruction)

## Chaîne C — Reproductibilité

| Patch | Contenu | Commit |
|---|---|---|
| C1 | Seed fixée (SEED=42) + config JSON | `57f606c` |
| C2 | requirements.txt + RUN_NOTES.md | `57f606c` |
| C3 | TGS persistance (à faire) | — |
