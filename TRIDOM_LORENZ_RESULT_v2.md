# NOTE CANONIQUE — RÉSULTAT TRIDOM LORENZ v2
## Chaos triadique autonome : condition structurelle au niveau des classes effectives
*30 mars 2026*

---

# 1. Objet

Cette note fige le résultat validé par le scan **TRIDOM — Lorenz triadique affiné v2**.
Elle sert de formulation canonique interne pour la suite du programme.

Statut :
- **résultat numérique fort**
- **validation méthodologique propre au niveau du protocole testé**
- **non encore théorème analytique général**

---

# 2. Cadre exact du résultat

Modèle **autonome**, **sans forçage externe**, de type Lorenz-like triadique signé.

Protocole v2 :
- Intégration **RK4**, DT = 0.0025
- **64 topologies denses**
- **6 permutations** par topologie
- **8 paramétrisations** (σ, ρ, β)
- **20 conditions initiales** par cas
- **3072 cas**, **61 440 trajectoires** au total
- MLE normalisé par le temps, LYAP_POS_THRESH = 0.05

La dynamique effectivement testée ne dépend pas des 6 arcs comme degrés de liberté indépendants, mais d'une **signature effective** :

$$\big(W_{01},\; W_{10},\; W_{12},\; \mathrm{sgn}(W_{20}W_{21})\big)$$

Le scan se réduit naturellement à **16 classes effectives**.

Note : $W_{02}$ (arc 0→2) n'intervient pas dans la dynamique — il est absent des équations :
$$\dot{x}_0 = \sigma W_{01}(x_1 - x_0), \quad \dot{x}_1 = W_{10}\,x_0(\rho - W_{12}\,x_2) - x_1, \quad \dot{x}_2 = W_{20}W_{21}\,x_0 x_1 - \beta x_2$$

---

# 3. Faits établis

## 3.1 Réduction des dégénérescences

Le résultat v1 en "8 topologies chaotiques" se réduit après factorisation à **2 mécanismes effectifs**.

## 3.2 Résumé par classes effectives

| Classe effective | Complex | Oscillating | Fixed | Unstable |
|---|---|---|---|---|
| `W01=+\|W10=+\|W12=+\|W20W21=+` | **168** | 24 | 0 | 0 |
| `W01=+\|W10=+\|W12=-\|W20W21=-` | **154** | 38 | 0 | 0 |
| `W01=+\|W10=-\|...` (toutes) | 0 | 0 | **192** | 0 |
| `W01=-\|...` (toutes) | 0 | 0 | 0 | **192** |

## 3.3 Robustesse des classes chaotiques

Dans les deux classes chaotiques :
- cas Complex : **100% bornés**, **100% mouvants**
- fraction MLE positif : très élevée
- médianes MLE : nettement positives
- paramétrisation (5, 15, 8/3) → Oscillating plutôt que Complex — frontière interne cohérente, pas un artefact

---

# 4. Condition structurelle canonique

## 4.1 Formulation correcte

$$\boxed{W_{01}=+,\qquad W_{10}=+,\qquad \mathrm{sgn}(W_{12})=\mathrm{sgn}(W_{20}W_{21})}$$

## 4.2 Statut exact

Dans le **cadre exact du modèle testé**, cette condition est :
- **nécessaire**
- **suffisante au niveau des classes effectives**

pour l'apparition numérique d'un régime chaotique borné.

## 4.3 Correction d'interprétation (v1 → v2)

**Incorrect (v1) :**
> "La boucle excitatrice bidirectionnelle 0↔1 est à elle seule nécessaire et suffisante."

**Correct (v2) :**
> $W_{01}=+$ et $W_{10}=+$ sont **nécessaires** mais **non suffisants seuls**.
> Il faut en plus l'alignement : $\mathrm{sgn}(W_{12}) = \mathrm{sgn}(W_{20}W_{21})$.

## 4.4 Interprétation dynamique

La condition garantit que le terme croisé de la troisième équation et le terme inhibiteur de la deuxième sont **cohérents en signe** : $W_{12} \cdot (W_{20}W_{21}) > 0$ dans les deux cas chaotiques. Cela reproduit structurellement le mécanisme de Lorenz canonique où $-xz$ dans $\dot{y}$ et $+xy$ dans $\dot{z}$ assurent le confinement de l'attracteur.

---

# 5. Déduction scientifique

## 5.1 Résultat central

> Le chaos triadique autonome devient numériquement accessible dès que l'on remplace le cadre additif séparé par un cadre de **couplages croisés multiplicatifs** de type Lorenz-like, sous la condition structurelle précise ci-dessus.

## 5.2 Contraste canonique

| Cadre | Chaos borné détecté |
|---|---|
| Additif $\dot{x} = -\alpha x + W\phi(x)$, $\phi$ monotone | **0** dans tous les scans rapportés |
| Lorenz-like croisé multiplicatif | **Oui**, dans 2 classes effectives précises |

## 5.3 Conséquence pour le programme

> Le verrou observé dans TRIDOM est **structurel**, lié à la nature du couplage, non à la taille du réseau.

---

# 6. Formulation canonique courte

> Le scan Lorenz v2 valide numériquement l'existence d'un chaos triadique autonome dans une famille de couplages croisés multiplicatifs. Après réduction des dégénérescences topologiques, deux seules classes effectives subsistent comme chaotiques. Dans le cadre exact testé, elles sont caractérisées par une boucle excitatrice bidirectionnelle $0 \leftrightarrow 1$ et par l'alignement de signe entre $W_{12}$ et $W_{20}W_{21}$.

---

# 7. Portée et limites

## Ce qui est établi
- Existence numérique de chaos triadique autonome dans le modèle testé
- Réduction de 8 labels apparents à **2 mécanismes effectifs**
- Condition structurelle exacte au niveau des classes effectives
- Robustesse numérique interne dans le protocole v2

## Ce qui n'est pas encore établi
- Théorème analytique général
- Universalité au-delà de la famille Lorenz-like testée
- Classification générale de tous les couplages multiplicatifs triadiques
- Preuve formelle indépendante du protocole numérique

## Statut épistémique
> **Résultat numérique fort, structurant, mais encore intra-modèle.**

---

# 8. Conséquence doctrinale pour TRIDOM

Ce résultat déplace le centre du programme :
- non plus : "à quelle taille apparaît la complexité ?"
- mais : **"quelle structure minimale de couplage autonome permet le passage de l'oscillation à une complexité bornée triadique ?"**

---

# 9. Énoncé final figé

> Dans le modèle Lorenz-like triadique autonome testé, le chaos borné n'apparaît numériquement que dans les classes effectives satisfaisant
> $$W_{01}=+,\quad W_{10}=+,\quad \mathrm{sgn}(W_{12})=\mathrm{sgn}(W_{20}W_{21}).$$
> Ce résultat montre que, dans TRIDOM, l'accès à la complexité bornée dépend de la structure du couplage croisé multiplicatif, et non d'une simple augmentation de taille.

---

# 10. Prochaines étapes cohérentes (v3 publication-grade)

1. **Portraits d'attracteurs** pour les cas Complex — vérification visuelle de la structure d'attracteur étrange
2. **Calcul Lyapunov rigoureux** (méthode QR, long horizon) sur les cas Complex confirmés
3. **Export CSV** + tableau final (topologie / permutation / paramètres / bassin borné / MLE médian)
4. **Mise à jour du manuscrit** — sections 4 (Triadic Threshold Hypothesis) et 9 (Discussion)
5. **Analyse formelle** de la condition $\mathrm{sgn}(W_{12}) = \mathrm{sgn}(W_{20}W_{21})$ dans le cadre Thomas–Kaufman / Soulé

---

*Document auto-suffisant. Indexé au protocole v2 exact. Version figée le 30 mars 2026.*
