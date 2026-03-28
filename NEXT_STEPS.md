# NEXT_STEPS.md — Feuille de route post-gel v0.5

*Priorités ordonnées. Ne pas ouvrir avant que la précédente soit clôturée.*

---

## 1. Pipeline Lyapunov complet
- **Statut :** Ouvert
- **Objectif :** Remplacer l'approximation par perturbation par un vrai exposant de Lyapunov (ré-orthogonalisation QR)
- **Impact :** Crédibilité de la classification "chaotic candidates"
- **Agent :** coder → validator

## 2. Benchmarking externe
- **Statut :** Ouvert
- **Objectif :** Comparer N3D vs GRU/LSTM sur tâches standard (adding, copy, sequential MNIST)
- **Impact :** Positionnement scientifique
- **Agent :** coder → validator → epistemic_reviewer

## 3. Preuve formelle Triadic Threshold
- **Statut :** Ouvert
- **Objectif :** Formaliser le programme de preuve dans le cadre Thomas-Kaufman/Soulé
- **Impact :** Passage de "supported hypothesis" à "theorem"
- **Agent :** researcher → epistemic_reviewer
- **Prérequis :** Aucun (peut avancer en parallèle)

## 4. Note séparée m5_extension
- **Statut :** Ouvert (après items 1-2)
- **Objectif :** Documenter le résultat Variante B (96 runs, 88 convergences, γa³+λa=η)
- **Format :** Note courte, reproductible, centrée dynamique
- **Agent :** researcher → validator → epistemic_reviewer
- **Contrainte :** Ne pas intégrer au preprint principal

## 5. Récupération source LaTeX native
- **Statut :** Ouvert
- **Objectif :** Retrouver ou reconstruire le .tex d'origine du preprint
- **Impact :** Publication-ready (PDF actuel = extraction, pas source)
- **Action :** Vérifier historique local, Overleaf, ou reconstruire à partir de tridom_preprint_v0.5.md

## 6. Extension en échelle (n > 3)
- **Statut :** Futur
- **Objectif :** Explorer la composition de Tridoms à n=4 et au-delà
- **Question :** Nouvelles lois mésoscopiques ou simple croissance combinatoire ?

---

## Principes
- Un item à la fois (sauf parallélisme explicite)
- Validation avant ouverture (reviewer systématique)
- Pas de mélange des statuts (preuve ≠ support ≠ conjecture)
