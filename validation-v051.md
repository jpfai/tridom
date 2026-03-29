# Validation v0.5.1 — Rapport de relecture épistémique

**Date :** 2026-03-29
**Relecteur :** tridom-epistemic-reviewer
**Fichier validé :** `tridom/tridom_preprint_v0.5.1.md`
**Changelog vérifié :** `tridom/CHANGELOG-v0.5.1.md`

---

## 1. Cohérence interne (57/21/0) ✅

| Référence | Contenu | Verdict |
|-----------|---------|---------|
| L24 (Abstract) | "57 monostable, 21 oscillating, 0 chaotic" | ✅ |
| L218 (tableau §5) | Rangée monostable : 57 | ✅ |
| L227 (tableau §5) | Rangée oscillating : 21 | ✅ |
| L240 (note §5) | "reclassified as oscillating (6 cases) or monostable (1 case)" → 56+1=57, 15+6=21 | ✅ |
| Tableau dynamique §6.3 | N3D = "monostability, multistability, oscillation" (pas chaos) | ✅ |
| Conclusion §10 | "multi-stability and oscillatory regimes" | ✅ |

**Vérification arithmétique :** 56/15/7 (v0.1) → +1 monostable, +6 oscillating, −7 chaotic = 57/21/0 ✓

> Aucune incohérence détectée.

---

## 2. Épistémie (formulations et glissements) ✅

### Bloc D — 8 corrections vérifiées

| # | Localisation prévue | Présent dans v0.5.1 | Verdict |
|---|---------------------|----------------------|---------|
| 1 | Abstract | "proposes reframing… whose causal properties remain to be empirically validated" (L26-28) | ✅ |
| 2 | §1 L39-40 | "no formal definition as an autonomous dynamical unit — a gap this work aims to address" (L44) | ✅ |
| 3 | §1 L47-48 | "reframes… as a candidate dynamical unit, defined by a formal structural and dynamical characterisation" (L51) | ✅ |
| 4 | §1 L50 (manifeste) | Assertion reformulée comme hypothèse marquée (L54-55) | ✅ |
| 5 | §4 L200 (tableau) | "minimal candidate grain (hypothesis supported numerically, not yet formally proven)" (L205) | ✅ |
| 6 | §4 L201-203 (corollaire) | "distinguished numerical demonstration from conjectural impossibility" (L184, corollaire conjectural) | ✅ |
| 7 | Conclusion L644-645 | "formal candidate dynamical unit whose causal properties constitute an open research direction" (L655) | ✅ |
| 8 | Conclusion L651-653 | "proposes reframing… substrate-invariant L1 structural core — and invites future work to establish whether this structural invariance supports causal claims" (L666) | ✅ |

### Vérifications transversales

- **Verbes performatifs** : "shifts" et "elevates" absents du texte v0.5.1. Remplacés par "proposes reframing" / "reframes". ✅
- **Confusion structure/causalité** : distinction explicite partout (L655, L666). ✅
- **Assertions connectome** : aucune claim connectome non fondée. Le texte dit "invites future work to establish whether this structural invariance supports causal claims at the connectome scale" — formulation prudente. ✅
- **"The contribution of Tridom is not incremental" (L665)** : jugement de valeur, pas assertion factuelle. Tolérable dans une conclusion — mais c'est la formulation la plus assertive du texte.

> ⚠️ **Point mineur (non bloquant) :** L665 — "not incremental" est un jugement éditorial. Proposition : ajouter "in our assessment" ou reformuler en "goes beyond incremental extension by…". Impact : faible, mais un reviewer pourrait le relever.

---

## 3. Contextualisation du chaos ✅

| Référence | Formulation | Verdict |
|-----------|------------|---------|
| L24 (Abstract) | "No robust chaotic regime was observed under extended exploration" | ✅ — "was not observed", pas "does not exist" |
| L194 (§4, Note on chaos) | "suggests that the triadic scale may not generically support robust chaos" | ✅ — "suggests… may not" |
| L194 | "Chaotic dynamics may require higher-order structures (n ≥ 4)" | ✅ — "may require", hypothèse |
| L240 (§5) | "false positive artefact of insufficient sampling" | ✅ — qualification du protocole v0.1 |
| L335 (§6.3) | "Full palette: monostability, multistability, oscillation" — chaos absent | ✅ |
| L627-638 (§9.2 lim. 4) | "absence of chaos… does not constitute a formal impossibility proof" | ✅ — formulation idéale |
| L638 (§9.3) | "Investigation of chaotic dynamics at n = 3 under alternative nonlinearities" | ✅ — open question |
| L659-661 (Conclusion) | "did not reveal robust chaotic dynamics… suggesting that chaos may require higher-order structures — a hypothesis left open" | ✅ |

> Aucune formulation "chaos is absent" ou "chaos is impossible" trouvée. Toutes les mentions sont correctement contextualisées comme observations protocole-dépendantes ou hypothèses.

---

## 4. Benchmark — Honnêteté comparative ✅

### Données (§7.3)

| Modèle | Accuracy | Paramètres |
|--------|----------|------------|
| Tridom (EEI, 3 nodes) | 98.5% | 14 |
| GRU (3 units) | 100% | 62 |
| LSTM (3 units) | 100% | 80 |

### Évaluation

- **Précision de la comparaison** : Le texte dit "competitive performance with significantly fewer parameters" — pas "surpasses" ou "outperforms". ✅
- **Gap explicite** : "The gap in accuracy (1.5pp) relative to GRU/LSTM is expected given the order-of-magnitude difference in parameter count" — honnête. ✅
- **Ouverture** : "whether this gap closes with ensemble or stacked Tridom architectures is an open question" — non prétentieux. ✅
- **Auto-limitation (§9.2)** : "broader benchmarking against standard RNN architectures on established sequence tasks would strengthen the empirical claims" — lucidité. ✅

> ⚠️ **Point mineur (non bloquant) :** Le benchmark est décrit comme "on a classification task" sans spécifier le dataset. Pour la reproductibilité, il serait préférable de nommer le dataset (ex. : "on a binary classification of [dataset name]"). Impact : faible (le code est open-source), mais un reviewer pourrait demander la précision.

---

## 5. Changelog — Complétude et traçabilité ✅

### Couverture des modifications

| Section du changelog | Correspondance dans le preprint | Verdict |
|----------------------|--------------------------------|---------|
| Abstract (chaos, 57/21/0) | L24 | ✅ |
| §4 TTH (formulation) | L187, L205 | ✅ |
| §5 Atlas (distribution, protocole, faux positifs) | L210-240 | ✅ |
| §5.1 Interprétation chaos | L194, note explicite §4 | ✅ |
| §6.3 (retrait chaos N3D) | L335 | ✅ |
| §7.3 Benchmark | L474-487 | ✅ |
| §9.2 Limitations (item 4) | L636-638 | ✅ |
| §9.3 Open contributions | L641-648 | ✅ |
| §10 Conclusion | L655-666 | ✅ |
| 8 corrections Bloc D | Toutes vérifiées (§2 ci-dessus) | ✅ |

### Mineurs listés dans le changelog

- Version v0.5 → v0.5.1 ✅
- Unicode subscripts (n₁, n₂, n₃) ✅
- Zenodo archive v0.5.1 (DOI: 10.5281/zenodo.19130439) ✅ (L8-9)
- §9.1 "causal agents" → "dynamical units with guaranteed regime properties" ✅ (L596)

### Table de traçabilité

La table de traçabilité du changelog (6 lignes) relie chaque modification à sa source (fait expérimental / audit Bloc D). ✅

> Changelog complet et traçable. Aucune modification non documentée détectée.

---

## Résumé

| Critère | Statut |
|---------|--------|
| Cohérence interne (57/21/0) | ✅ Validé |
| Épistémie (8 corrections Bloc D) | ✅ Validé |
| Contextualisation chaos | ✅ Validé |
| Benchmark honnête | ✅ Validé |
| Changelog complet | ✅ Validé |

### Points mineurs (non bloquants)

| # | Ligne | Observation | Proposition |
|---|-------|-------------|-------------|
| 1 | L665 | "not incremental" — jugement éditorial assertif | Ajouter "in our assessment" ou reformuler |
| 2 | §7.3 | Dataset du benchmark non nommé | Préciser le dataset pour reproductibilité |

---

## Verdict : ✅ GO pour diffusion

Le preprint v0.5.1 est cohérent, épistémiquement rigoureux, et correctement nuancé sur le chaos. Les deux points mineurs identifiés ne compromettent pas la validité scientifique et peuvent être traités en patch mineur ultérieur (v0.5.2) ou laissés tels quels pour cette diffusion.
