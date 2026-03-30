# TRIDOM — Synthèse interne v0.4
*Mars 2026 — Programme Tridom v0.5.1*
*Mise à jour après détection de chaos borné dans le cadre Lorenz triadique signé*

---

## *** RÉSULTAT MAJEUR ***

> **Chaos borné détecté dans 7 configurations triadiques denses autonomes**
> dans le cadre Lorenz triadique signé, pour des paramétrisations (σ, ρ, β) connues.

---

## 1. Tableau cumulatif complet

| Expérience | Modèle | Complex | Résultat |
|---|---|---|---|
| Atlas tanh ODE | additif, tanh | 0 | 57 fixed / 21 osc |
| Multi-NL (piecewise, rational, relu) | additif | 0 | idem / rational contracte |
| m6_extension (6 nœuds) | additif, tanh | 0 | 100% osc |
| Retard uniforme | DDE tanh | 0 | 63/64 osc |
| Retards non uniformes weak/strong | DDE tanh | 0 | strong→osc (78%) |
| Nona dense (9 nœuds) | additif + DDE tanh | 0 | 0% complex |
| Couplage multiplicatif | additif enrichi | 0 | 8 unstable, 0 complex |
| Famille Lorenz V1/V2/V3 | croisé | 0 | V1 50% unstable |
| Poids réels D1–D4 | additif, tanh | 0 | osc renforcée |
| NL non monotone NM1–NM5 | additif enrichi | 0 | 0 complex |
| **Lorenz triadique affiné** | **Lorenz signé autonome** | **✅ 21 cas** | **8 topologies chaotiques** |

---

## 2. Topologies chaotiques identifiées

| Topo idx | Score | Label | Paramétrisations chaotiques | Lyap max |
|---|---|---|---|---|
| 41 | 3 | `01E.02I.10E.12I.20I.21E` | (10,28,4) · (16,45,4) · (10,99.6,8/3) | 0.01123 |
| 42 | 3 | `01E.02I.10E.12I.20E.21I` | (16,45,4) | 0.00821 |
| 44 | 3 | `01E.02I.10E.12E.20I.21I` | (16,45,4) · (10,99.6,8/3) | 0.00947 |
| 47 | 3 | `01E.02I.10E.12E.20E.21E` | (10,28,8/3) · (16,45,4) · (10,99.6,8/3) · (14,28,8/3) | 0.00833 |
| 57 | 3 | `01E.02E.10E.12I.20I.21E` | (10,28,8/3) · (10,28,4) · (16,45,4) · (10,99.6,8/3) | 0.00804 |
| 58 | 3 | `01E.02E.10E.12I.20E.21I` | (10,28,8/3) · (16,45,4) | 0.00821 |
| 60 | 3 | `01E.02E.10E.12E.20I.21I` | (10,28,4) · (16,45,4) · (10,99.6,8/3) | 0.00922 |
| 63 | 1 | `01E.02E.10E.12E.20E.21E` | (16,45,4) · (10,99.6,8/3) | 0.00925 |

### Signature structurelle commune

**Toutes les topologies chaotiques partagent : `01E` ET `10E`**

→ La boucle positive excitative 0↔1 (arcs 0→1 et 1→0 tous deux excitatoires) semble **nécessaire** au mécanisme chaotique dans ce cadre.

**Note sur topo_63 (score=1)** : `01E.02E.10E.12E.20E.21E` — entièrement excitatrice, score de compatibilité Lorenz = 1 (pas d'arc inhibitoire). Elle produit quand même du chaos sous (16,45,4) et (10,99.6,8/3), ce qui suggère que l'inhibition n'est **pas** une condition nécessaire dans ce cadre. Le mécanisme chaotique repose sur la structure croisée, pas sur le signe global.

### Paramétrisations les plus robustes

| (σ, ρ, β) | Topologies chaotiques | Robustesse |
|---|---|---|
| (16, 45, 4.0) | 41, 42, 44, 47, 57, 58, 60, 63 | **8/8 — la plus robuste** |
| (10, 99.6, 8/3) | 41, 44, 47, 57, 60, 63 | 6/8 |
| (10, 28, 8/3) | 47, 57, 58 | 3/8 — canonique |
| (10, 28, 4.0) | 41, 47, 57, 60 | 4/8 |
| (14, 28, 8/3) | 47 | 1/8 |

---

## 3. Déduction centrale — version révisée

### Avant ce scan
> Le chaos borné semble absent du cadre triadique dans toutes les variantes testées.

### Après ce scan
> **Le chaos borné existe dans le cadre triadique autonome** — mais il requiert :
> 1. Un **couplage croisé de type Lorenz** ($x_i x_j$, $i \neq j$) — pas un couplage additif monotone.
> 2. Une **topologie spécifique** avec boucle positive excitative 0↔1 (arcs 01E et 10E présents).
> 3. Un **paramétrage** (σ, ρ, β) dans le régime chaotique — le canonique (10, 28, 8/3) suffit pour les topologies les plus robustes.

---

## 4. Reclassification finale des hypothèses

### H1 — Pattern global des retards : **Réfutée**
### H2 — Complexité supra-triadique : **Réfutée dans la Nona dense tanh**
### H3 — Verrou structurel du modèle : **Confirmée et précisée**
> Le verrou n'est pas la taille du réseau mais la forme du couplage. Le modèle additif $\dot{x} = -\alpha x + W\phi(x)$ exclut structurellement le chaos. Le couplage croisé de type Lorenz le rend possible.

### H4 — Couplage croisé nécessaire : **Confirmée**
> Le chaos borné dans un réseau triadique autonome requiert un couplage multiplicatif croisé entre variables distinctes ($x_i x_j$, $i \neq j$), avec une topologie excitative 0↔1.

---

## 5. Questions ouvertes immédiates

### Q1 — Vérification Lyapunov rigoureuse
Les exposants Lyapunov détectés (0.005–0.011) sont positifs mais modestes.
Une vérification avec calcul Lyapunov rigoureux (méthode QR, long horizon) est nécessaire pour confirmer formellement le chaos.

### Q2 — Signature topologique complète
`01E` et `10E` sont-ils **nécessaires et suffisants**, ou seulement nécessaires ?
Tester les 64 topologies avec (16, 45, 4) pour cartographier exhaustivement.

### Q3 — Relation avec l'atlas Tridom
Les topologies 41, 42, 44, 47, 57, 58, 60 — quel était leur régime dans l'atlas tanh ODE ?
Sont-elles parmi les 21 oscillatoires ou les 57 monostables ?

### Q4 — Interprétation dans le cadre Tridom
Le couplage Lorenz est-il compatible avec la définition formelle du Tridom ?
La structure (G, σ, [f]) peut-elle accueillir ce type de couplage ?
Ou faut-il étendre la définition ?

---

## 6. Prochaines étapes recommandées

### Étape A — Vérification immédiate (priorité haute)
Vérifier que les 7 topologies produisent bien des attracteurs bornés visuellement :
- Tracer les trajectoires (x0, x1, x2) dans l'espace de phase.
- Confirmer la structure d'attracteur (pas simplement du bruit numérique).

### Étape B — Cartographie exhaustive (σ=16, ρ=45, β=4)
Scanner les 64 topologies avec la paramétrisation la plus robuste (16, 45, 4).
Identifier toutes les topologies chaotiques et cartographier la signature structurelle.

### Étape C — Mise à jour du manuscrit
Ce résultat modifie la section 4 (Triadic Threshold Hypothesis) et la section 9 (Discussion).
Le chaos triadique existe — sous des conditions structurelles précises.

---

*Toutes les conclusions sont indexées aux classes de modèles, topologies et protocoles numériques effectivement testés à ce stade.*
