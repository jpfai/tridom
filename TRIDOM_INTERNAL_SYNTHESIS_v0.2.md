# TRIDOM — Synthèse interne v0.2
*Mars 2026 — Programme Tridom v0.5.1*
*Mise à jour après scan global retards + Nona dense*

---

## 1. Faits établis

### 1.1 Manuscrit

- Version actuelle : **v0.5.1** (tag GitHub, branche main).
- Épistémiquement propre, reproductibilité minimale validée (V1–V5 PASS).
- Diffusable comme preprint sérieux ; non définitif scientifiquement.

### 1.2 Atlas corrigé (tanh ODE, sans retard, protocole fixé)

| Régime | Count |
|---|---|
| Monostable | 57 |
| Oscillatoire | 21 |
| Chaos borné observé | **0** |

### 1.3 Scan multi-non-linéarités (64 topologies denses)

| NL | Fixed | Osc | Complex | Remarque |
|---|---|---|---|---|
| tanh | 21 | 43 | 0 | référence |
| piecewise | 21 | 43 | 0 | identique |
| rational | 61 | 3 | 0 | très contractant |
| relu | — | — | 1 | blow-up non borné |

### 1.4 m6_extension (6 nœuds, 2 triades couplées)

- 50 CI — 100% oscillatoire — 0% complexité bornée.

### 1.5 Retard uniforme (triade dense)

- 63/64 topologies → oscillatoires.
- 0 complexité bornée.

### 1.6 Scan global retards non uniformes (64 topologies, tanh)

| Profil | Fixed | Osc | Unstable |
|---|---|---|---|
| weak (τ=0.5) | 44 (68.8%) | 20 (31.2%) | 0 |
| strong (τ=3.0) | 14 (21.9%) | 50 (78.1%) | 0 |

Matrice de transition weak → strong :

| | strong: Fixed | strong: Osc |
|---|---|---|
| weak: Fixed | 14 | 30 |
| weak: Osc | 0 | 20 |

- Transition unidirectionnelle : Fixed→Osc possible, Osc→Fixed non observé.
- 0 instabilité. 0 complexité bornée.

### 1.7 Nona dense (9 nœuds, 3 triades, tanh)

| Phase | Fixed | Osc | Complex |
|---|---|---|---|
| Sans retard | 86.7% | 13.3% | 0% |
| Retard uniforme τ=1 | 40.0% | 60.0% | 0% |

- 0 complexité bornée dans toutes les configurations testées.

---

## 2. Déductions

### 2.1 Déduction centrale

> Dans la famille de modèles testée — $\dot{x} = -\alpha x + W\phi(x)$ avec $\phi$ monotone composante par composante — aucune complexité bornée n'émerge, ni au niveau triadique, ni au niveau m6, ni au niveau Nona dense, avec ou sans retard.

### 2.2 Sur le verrou structurel

L'absence de chaos ne s'explique pas par la seule dimension (le chaos est théoriquement possible en n=3 ODE autonome). Elle s'explique probablement par la structure restrictive du modèle :
- φ monotone ;
- application composante par composante ;
- absence de couplage multiplicatif direct entre variables.

### 2.3 Sur l'effet du retard

Le retard (uniforme ou fort) favorise globalement l'oscillation mais ne fait pas émerger de complexité bornée dans les scans effectués. Même pour les DDE (espace fonctionnel infinidimensionnel), aucune complexité bornée n'a été détectée.

### 2.4 Sur la taille du réseau

La simple augmentation de taille (n=3 → n=6 → n=9), dans cette famille de modèles, ne suffit pas à faire émerger de la complexité bornée.

---

## 3. Reclassification des hypothèses

### H1 — Pattern global des retards non uniformes

| | |
|---|---|
| Formulation initiale | `weak → oscillation / strong → fixation` |
| Statut | **Réfutée à l'échelle globale** |
| Remplacement | Dans le scan global (64 topologies), le retard fort favorise davantage l'oscillation que le retard faible. |

### H2 — Émergence de la complexité au niveau supra-triadique

| | |
|---|---|
| Formulation | La complexité manquante pourrait émerger au niveau supra-triadique. |
| Statut | **Non confirmée. Fortement affaiblie. Réfutée dans le sous-cadre Nona dense tanh ODE/DDE testé.** |

### H3 — Verrou structurel du modèle

| | |
|---|---|
| Formulation | L'émergence éventuelle d'une complexité bornée requiert un enrichissement structurel du modèle, non une simple augmentation de taille. |
| Statut | **Hypothèse de travail principale.** |

---

## 4. Limites explicites

### 4.1 Ce qui est prouvé (dans le protocole)

- Classification numérique reproductible (seeds fixés).
- Effet robuste du retard fort sur la proportion d'oscillation.
- Absence numérique de chaos borné dans toutes les architectures explorées.

### 4.2 Ce qui est probable

- Robustesse de l'absence de complexité bornée dans la famille $\dot{x} = -\alpha x + W\phi(x)$.
- Caractère structurel (plutôt que dimensionnel) de cette absence.

### 4.3 Ce qui est hypothétique

- Nécessité d'un enrichissement structurel pour faire émerger de la complexité bornée.
- Rôle décisif possible de couplages multiplicatifs, poids réels, ou non-linéarités non monotones.

### 4.4 Inconnus

| Inconnu | Priorité |
|---|---|
| Chaos avec couplage multiplicatif | Haute — Étape 3 |
| Chaos avec poids réels non binaires | Haute — Étape 3 |
| Chaos avec non-linéarité non monotone | Haute — Étape 3 |
| Chaos avec forçage externe | Moyenne |
| Comportement d'architectures modulaires asymétriques | Moyenne |
| Preuve formelle du seuil triadique | Ouverte |
| Exposants de Lyapunov formels | Ouverte |

---

## 5. Orientation du programme

### Avant

> Chercher à quelle taille apparaît le chaos.

### Maintenant

> Identifier quelle **modification structurelle minimale** du modèle rend possible l'émergence d'une complexité bornée.

### Candidats à tester (Étape 3)

Par ordre de priorité :

1. **Couplage multiplicatif** : $\dot{x}_i = -\alpha x_i + \sum_j W_{ij} x_j \phi(x_j)$
2. **Poids réels non binaires** : $W_{ij} \in \mathbb{R}$, tirés selon une distribution continue
3. **Non-linéarité non monotone** : $\phi(x) = x\sin(x)$ ou $\phi(x) = x^2/(1+x^2)$ signé
4. **Forçage externe** : $\dot{x} = -\alpha x + W\phi(x) + \epsilon \cos(\omega t)$

---

## 6. Question d'orientation (Étape 3)

> Quelle est la modification minimale du modèle $\dot{x} = -\alpha x + W\phi(x)$ la plus cohérente à tester en premier pour rendre possible l'émergence d'une complexité bornée : couplage multiplicatif, poids réels non binaires, non-linéarité non monotone, ou forçage externe ?

---

*Toutes les conclusions dynamiques sont indexées aux classes de modèles, topologies, non-linéarités et protocoles numériques effectivement testés à ce stade.*
