# CHANGELOG — v0.5.1

**Date :** 2026-03-29
**Motif :** Résultat expérimental majeur (atlas v0.2) + audit épistémique Bloc D

---

## 1. Corrections expérimentales (atlas v0.2)

### Abstract
- Supprimé "chaotic candidates" de la distribution et de la description
- Remplacé par : *"The atlas exhibits monostable and oscillatory regimes under the tested protocol. No robust chaotic regime was observed under extended exploration (50 initial conditions, 2000 integration steps)."*
- Distribution mise à jour : 57 monostable / 21 oscillating / 0 chaotic

### Section 4 (Triadic Threshold Hypothesis)
- Tableau TTH : n=3 reformulé en *"Multi-stability and oscillatory regimes become accessible at the triadic scale; the presence of chaos under the considered realizations remains an open question"*
- Supprimé "minimal complete grain" → remplacé par "minimal candidate grain (hypothesis supported numerically, not yet formally proven)"
- Corollaire conjectural : reformulé pour distinguer démonstration numérique (protocol-specific) et impossibilité générale (conjecturale)

### Section 5 (Atlas)
- Distribution : 56/15/7 → 57/21/0
- Protocole mis à jour : 8 CI / 500 steps → 50 CI / 2000 steps
- Supprimé la colonne "Chaotic candidates" du tableau de régime
- Ajouté note explicite sur les 7 faux positifs de v0.1
- Tableau représentatif : les topologies anciennement "chaotic candidates" reclassées comme "Oscillating"

### Nouvelle sous-section 5.1 (Interprétation)
- Ajouté l'hypothèse que chaos → n≥4
- Positionnement : hypothèse, pas théorème

### Section 6.3 (Comparative Architecture)
- Retiré "chaotic candidates" de la capacité dynamique de N3D

### Section 7.3 (Benchmark — nouvelle sous-section)
- Ajouté comparaison paramétrique : Tridom 98.5% / 14 params vs GRU 100% / 62 params vs LSTM 100% / 80 params
- Reformulation : *"competitive performance with significantly fewer parameters"*

### Section 9.2 (Limitations)
- Ajouté limitation 4 : absence de chaos ≠ preuve d'impossibilité formelle

### Section 9.3 (Open Contributions)
- Ajouté extension atlas n=4 motivée par hypothèse chaos
- Ajouté investigation chaos sous non-linéarités alternatives

### Section 10 (Conclusion)
- Remplacé "all non-trivial dynamical families" par "multi-stability and oscillatory regimes"
- Ajouté mention de l'exploration étendue (50 CI, 2000 steps)
- Ajouté hypothèse chaos → n≥4

---

## 2. Corrections épistémiques (Bloc D — 8 items)

| # | Localisation | Correction |
|---|-------------|------------|
| 1 | Abstract (L27-29) | "shifts the ontological grain... candidate causal unit" → "proposes reframing... whose causal properties remain to be empirically validated" |
| 2 | §1 (L39-40) | "no formal claim to ontological status" → "no formal definition as an autonomous dynamical unit — a gap this work aims to address" |
| 3 | §1 (L47-48) | "elevates... to ontological unit" → "reframes... as a candidate dynamical unit, defined by a formal structural and dynamical characterisation" |
| 4 | §1 (L50, manifeste) | Citation assertive → reformulée comme hypothèse clairement marquée |
| 5 | §4 (L200, tableau) | "minimal complete grain" → "minimal candidate grain (hypothesis supported numerically, not yet formally proven)" |
| 6 | §4 (L201-203, corollaire) | "becomes possible in the strong sense" → distingué démonstration numérique de conjecture d'impossibilité |
| 7 | Conclusion (L644-645) | "formal candidate causal unit" → "formal candidate dynamical unit whose causal properties constitute an open research direction" |
| 8 | Conclusion (L651-653) | "shifts... substrate-invariant causal unit" → "proposes reframing... with a substrate-invariant L1 structural core — and invites future work to establish whether this structural invariance supports causal claims" |

### Corrections transversales
- Verbes performatifs ("shifts", "elevates") remplacés par descriptifs ("proposes reframing", "reframes")
- Confusion structure/causalité levée : distinction explicite entre invariance L1 (démontrée) et statut causal (hypothétique)
- Suppression des assertions non connectées aux données (aucune connectome analysée → pas de claim connectome)
- Répétition rhétorique Abstract/Conclusion harmonisée avec formulation nuancée

---

## 3. Changements mineurs

- Version : v0.5 → v0.5.1 dans en-tête
- L2 de la table des nœuds : unicode subscripts (n₁, n₂, n₃) au lieu de n1, n2, n3
- Zenodo archive : référence v0.5.1
- Section 9.1 : "causal agents" → "dynamical units with guaranteed regime properties" (cohérence épistémique)

---

## Traçabilité

| Modification | Source |
|-------------|--------|
| Atlas v0.2 (57/21/0) | Fait expérimental : 50 CI, 2000 steps |
| Suppression chaos | Fait expérimental : 7 faux positifs confirmés |
| Interprétation chaos → n≥4 | Inférence du résultat expérimental |
| Benchmark paramétrique | Données expérimentales Tridom/GRU/LSTM |
| 8 corrections épistémiques | Audit Bloc D (review-bloc-D.md) |
| Reformulations TTH | Audit Bloc D + fait expérimental |
