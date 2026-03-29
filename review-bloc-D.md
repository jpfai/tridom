# Review Bloc D — Formulations spéculatives / assertives (tridom_preprint_v0.5.md)

**Reviewer :** tridom-epistemic-reviewer (sous-agent)
**Date :** 2026-03-29
**Manuscrit :** v0.5 / v0.4 (fichier `tridom_preprint_v0.5.md`)
**Posture épistémique attendue :** hypothèse soutenue par preuves constructives numériques, pas théorème démontré.

---

## Tableau des phrases problématiques

| Ligne(s) | Original | Problème | Proposition de reformulation |
|----------|----------|----------|------------------------------|
| **L27–29** (Abstract) | *"it shifts the ontological grain from the motif as a network statistic to the motif as a formal, persistent, substrate-aware candidate causal unit"* | Verbe performatif ("shifts") qui présente la contribution comme un fait accompli ontologique. "Candidate causal unit" n'est relié à aucune donnée causale — il s'agit d'une proposition théorique, non d'un résultat empirique démontré. | *"it proposes reframing the motif from a network statistic toward a formal, persistent, substrate-aware unit whose causal properties remain to be empirically validated"* |
| **L39–40** (Section 1) | *"with no formal claim to ontological status as an independent causal unit"* | Présuppose que le motif *devrait* avoir un statut ontologique, et que l'absence en est un défaut. C'est un argument rhétorique orientant vers la solution proposée, pas un constat neutre. | *"with no formal definition as an autonomous dynamical unit — a gap this work aims to address"* |
| **L47–48** (Section 1) | *"This paper elevates the three-node signed motif from statistical building block to ontological unit"* | Assertion ontologique forte : "elevates ... to ontological unit" postule un saut de statut qui n'est pas encore démontré. L'atlas et l'implémentation montrent une *classification dynamique*, pas un statut ontologique. | *"This paper reframes the three-node signed motif as a candidate dynamical unit, defined by a formal structural and dynamical characterisation rather than by statistical over-representation alone"* |
| **L50** (Section 1) | *"The elementary grain of a connectome is not the isolated neuron, but the causal triad — defined by its dynamics, not its matter."* | Formulation assertive de type manifeste. "Elementary grain of a connectome" est spéculatif : aucune connectome n'a été analysée dans ce papier. "Causal triad" présuppose la causalité, qui n'est pas démontrée. La distinction dynamique/matière est intéressante mais formulée comme vérité, pas hypothèse. | *"We hypothesise that the relevant unit of analysis for connectome-scale organisation may be the causal triad, defined by its dynamical regime rather than by substrate identity — a proposition to be tested against empirical connectome data"* |
| **L200** (Section 4, tableau) | *"Stable under parameter perturbation — minimal complete grain"* | "Minimal complete grain" est présenté comme fait dans un tableau, alors que le statut de l'hypothèse est "supported" (pas prouvé). Le tableau mélange résultats numériques et interprétation ontologique. | *"Stable under parameter perturbation — minimal candidate grain (hypothesis supported numerically, not yet formally proven)"* |
| **L201–203** (Section 4, corollaire) | *"n = 3 is the smallest integer at which substrate-invariant non-trivial causal organisation becomes possible in the strong sense"* | Le corollaire est étiqueté "conjectural" (bon), mais la formulation "becomes possible in the strong sense" est assertive. Le résultat constructif montre *existence de réalisations* sous ODE, pas une impossibilité générale pour n < 3 hors conditions Thomas–Kaufman. | *"n = 3 is the smallest integer at which substrate-invariant non-trivial organisation is demonstrated under the present numerical protocol, consistent with the Thomas–Kaufman structural conditions; the strong impossibility claim for general substrates remains conjectural"* |
| **L644–645** (Conclusion) | *"We have introduced Tridom as a formal candidate causal unit"* | Même problème que L27–29 : "candidate causal unit" est utilisé comme label sans qualification du statut hypothétique. Répété en position de conclusion, il acquiert un poids rhétorique supérieur au reste du texte. | *"We have introduced Tridom as a formal candidate dynamical unit whose causal properties constitute an open research direction"* |
| **L651–653** (Conclusion) | *"it shifts the ontological grain from the motif as a network statistic to the motif as a formal, persistent, substrate-invariant causal unit"* | Répétition quasi exacte de L27–29, avec ajout de "substrate-invariant" devant "causal unit" (intensification). Confond L1 (sign pattern, effectivement invariant) avec le statut causal (non démontré). | *"it proposes reframing the motif from a network statistic toward a formal, persistent unit with a substrate-invariant L1 structural core — and invites future work to establish whether this structural invariance supports causal claims at the connectome scale"* |

---

## Synthèse

### Catégories de problèmes

1. **Confusion structure / causalité** (L27–29, L50, L651–653) : l'invariance structurelle L1 (topologie + signe) est démontrée par construction. Le statut *causal* ne l'est pas. Le manuscrit glisse de l'un à l'autre sans marquer la frontière épistémique.

2. **Verbes performatifs** (L27–29, L47–48, L651–653) : "shifts", "elevates" présentent la contribution comme un accomplissement, alors qu'il s'agit d'une *proposition de reframing*.

3. **Assertions non connectées aux données** (L50, L39–40) : "elementary grain of a connectome" — aucune connectome n'est analysée. "Ontological status" — aucun critère ontologique n'est proposé ou discuté.

4. **Répétition rhétorique** (L27–29 ≈ L651–653) : la même phrase assertive apparaît en Abstract et en Conclusion, créant un effet d'écho qui amplifie au-delà de ce que les résultats supportent.

### Recommandation globale

Le manuscrit dispose de résultats concrets (atlas de 78 topologies, classification ODE, implémentation PyTorch, TGS v2). Ces résultats sont solides. Le problème n'est pas dans la contribution, mais dans le *packaging rhétorique* qui sur-vend le statut ontologique et causal. Les reformulations proposées conservent l'ambition théorique tout en distinguant clairement :
- ce qui est **démontré** (classification, invariance L1, implémentation)
- ce qui est **soutenu numériquement** (TTH, performances comparatives)
- ce qui reste **hypothétique** (statut causal, application aux connectomes)

### Posture épistémique cible

> "Nous proposons un cadre formel pour traiter le motif triadique comme unité dynamique autonome. L'invariance structurelle est garantie par construction. Le statut causal est une hypothèse de travail soutenue par des preuves constructives, pas un théorème."

---

*Fin du rapport Bloc D.*
