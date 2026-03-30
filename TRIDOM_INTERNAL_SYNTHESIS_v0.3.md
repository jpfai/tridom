# TRIDOM — Synthèse interne v0.3
*Mars 2026 — Programme Tridom v0.5.1*
*Mise à jour après scan complet des enrichissements structurels (H3)*

---

## 1. Faits établis — tableau cumulatif complet

| Expérience | Modèle | Topologies | CI | Complex | Résultat |
|---|---|---|---|---|---|
| Atlas tanh ODE | additif, tanh | 64 denses | 8 | 0 | 57 fixed / 21 osc |
| Multi-NL (piecewise, rational, relu) | additif | 64 denses | 8 | 0 | idem tanh / rational contracte / relu blow-up |
| m6_extension | additif, tanh, 6 nœuds | — | 50 | 0 | 100% osc |
| Retard uniforme | DDE tanh | 64 denses | — | 0 | 63/64 osc |
| Retards non uniformes — weak/strong | DDE tanh | 64 denses | 20 | 0 | strong→osc (78%), Fixed→Osc unidirectionnel |
| Nona dense | additif + DDE tanh, 9 nœuds | 3 topos × 5 seeds | 30 | 0 | 0% complex |
| Couplage multiplicatif $x_j \phi(x_j)$ | additif enrichi | 64 denses | 30 | 0 | 8 unstable, 0 complex |
| Famille Lorenz (V1/V2/V3) | croisé | 64 denses | 30 | 0 | V1 : 50% unstable ; V2 : 100% fixed ; V3 : 25% osc |
| Poids réels non binaires (D1–D4) | additif, tanh | 64 × 5 tirages | 10 | 0 | osc renforcée (jusqu'à 91.6%), 0 complex |
| **Non-linéarité non monotone (NM1–NM5)** | **additif enrichi** | **64 denses** | **20** | **0** | **voir tableau ci-dessous** |

### Détail — Non-linéarités non monotones

| NL | Formule | Fixed% | Osc% | Complex% | Unstable% |
|---|---|---|---|---|---|
| NM1 sin | $\sin(x)$ | 56.2% | 43.8% | **0%** | 0% |
| NM2 sinc-gauss | $x\,e^{-x^2}$ | 100% | 0% | **0%** | 0% |
| NM3 sin-bounded | $\sin(x)/(1+|x|)$ | 100% | 0% | **0%** | 0% |
| NM4 double-well | $x - x^3/3$ | 65.6% | 34.4% | **0%** | 0% |
| NM5 sin-damped | $\sin(\pi x)\,e^{-0.1|x|}$ | 50% | 50% | **0%** | 0% |

**Observations :**
- NM2 et NM3 : 100% monostable — ces φ très contractantes suppriment même l'oscillation.
- NM1 et NM5 : jusqu'à 50% oscillatoire — le sinus pur et le sinus amorti préservent la richesse dynamique.
- NM4 (double-puits) : 34.4% oscillatoire — non-monotonicité modérée insuffisante pour le chaos.
- **0 complexité bornée dans toutes les variantes.**

---

## 2. Déduction centrale — version consolidée

> Dans l'ensemble des variantes testées à ce stade — additif, multiplicatif, croisé, retardé, multi-NL, poids réels, supra-triadique — **aucun attracteur chaotique borné n'a été détecté**. L'oscillation est robuste et constitue le régime non-trivial dominant. La résistance au chaos semble être une propriété structurelle du cadre $\dot{x} = -\alpha x + W\phi(x)$ plutôt qu'un artefact de la taille, des poids, ou de la non-linéarité spécifique.

---

## 3. Reclassification finale des hypothèses

### H1 — Pattern global des retards non uniformes
- **Réfutée** à l'échelle globale : weak ne favorise pas l'oscillation plus que strong. C'est le contraire.

### H2 — Émergence de la complexité au niveau supra-triadique
- **Réfutée** dans le sous-cadre Nona dense tanh ODE/DDE testé.

### H3 — Verrou structurel du modèle
- **Confirmée comme hypothèse de travail** après 4 enrichissements testés (multiplicatif, Lorenz, poids réels, NL non monotone), tous négatifs.
- Le verrou semble **plus profond que prévu** — il n'est pas levé par des non-linéarités non monotones, ni par des couplages croisés.

### H4 — Nouvelle hypothèse émergente
> **Le chaos borné dans un réseau triadique $\dot{x} = -\alpha x + g(W, x)$ requiert soit un couplage multiplicatif croisé entre variables distinctes (type Lorenz $x_i x_j$, $i \neq j$) avec une structure topologique précise, soit un forçage externe périodique.**

---

## 4. Bilan des enrichissements structurels (H3)

| Candidat | Résultat | Interprétation |
|---|---|---|
| Multiplicatif $x_j \phi(x_j)$ | 0 complex, 8 unstable | Terme $x_j^2$ non borné asymétriquement |
| Lorenz V1 (croisé canonique) | 0 complex, 50% unstable | Structure correcte mais paramétrage à affiner |
| Lorenz V2 (croisé général) | 0 complex, 100% fixed | Trop contractant |
| Lorenz V3 (croisé signé) | 0 complex, 25% osc | Borné mais pas assez riche |
| Poids réels D1–D4 | 0 complex, osc renforcée | Enrichit quantitativement, pas qualitativement |
| NL non monotone NM1–NM5 | 0 complex | Pas de rupture qualitative |

---

## 5. Limites explicites

### Ce qui est prouvé (dans le protocole)
- Absence numérique reproductible de chaos borné dans toutes les architectures explorées.
- Oscillation robuste comme régime non-trivial dominant.
- Retard fort favorise l'oscillation (effect global sur 64 topologies).

### Ce qui reste hypothétique
- Lorenz V1 avec paramétrage σ/ρ/β affiné par topologie pourrait produire du chaos borné pour des topologies spécifiques.
- Un forçage externe périodique ($\epsilon \cos \omega t$) pourrait déstabiliser les cycles limites en orbites chaotiques (bifurcation quasi-périodique → chaos).
- Des poids réels avec structure spécifique (non aléatoire) pourraient être nécessaires.

### Ce qui est inconnu
- Comportement exact avec couplage croisé $W_{ij} x_j x_k$ ($j \neq k$) sans terme additif résiduel.
- Existence de topologies Lorenz-compatibles parmi les 64 denses sous paramétrage σ/ρ/β adapté.
- Rôle du forçage externe périodique.
- Statut formel des exposants de Lyapunov (calcul rigoureux non encore effectué).

---

## 6. Orientation — prochains fronts expérimentaux

### Priorité 1 — Forçage externe (candidat le plus prometteur)
$$\dot{x} = -\alpha x + W\phi(x) + \epsilon \cos(\omega t)$$
- Même structure de base, ajout minimal.
- Connu pour produire du chaos par quasi-périodicité dans des systèmes oscillants.
- Testable immédiatement sur les 21 topologies oscillatoires de l'atlas.

### Priorité 2 — Lorenz triadique affiné (V1 revisité)
- Identifier parmi les 64 topologies celles compatibles avec la structure Lorenz.
- Affiner σ, ρ, β par topologie pour obtenir le chaos borné canonique.
- Vérifier si la contrainte de signe de W est compatible.

### Priorité 3 — Couplage croisé pur $W_{ij} x_j x_k$
$$\dot{x}_i = -\alpha x_i + \sum_{j \neq k} W_{ij} x_j x_k$$
- Couplage strictement bilinéaire sans terme additif.
- Plus proche du mécanisme de Lorenz que les variantes V1–V3 testées.

---

## 7. Question d'orientation (v0.3)

> Après l'échec des enrichissements non monotones, multiplicatifs et de poids réels, le forçage externe périodique est-il le candidat le plus parcimonieux à tester pour faire émerger une complexité bornée dans le cadre triadique, ou faut-il d'abord affiner le paramétrage Lorenz triadique sur les topologies compatibles ?

---

*Toutes les conclusions sont indexées aux classes de modèles, topologies et protocoles numériques effectivement testés à ce stade.*
