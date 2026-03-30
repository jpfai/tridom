# TRIDOM — Note canonique de résultat
## Chaos triadique autonome — Scan Lorenz v2
*Mars 2026 — Programme Tridom v0.5.1*

---

## Statut

**Résultat numérique validé.**
Établi par `scan_lorenz_refined_v2.py` (RK4, MLE normalisé, 6 permutations, classes effectives).
Ce résultat est de nature numérique expérimentale — il n'est pas, à lui seul, une preuve mathématique formelle.

---

## Énoncé canonique

> Dans le modèle Lorenz-like triadique autonome testé, après réduction par classes effectives,
> le chaos borné n'apparaît que dans les deux classes caractérisées par :
>
> $$W_{01} = +, \quad W_{10} = +, \quad \mathrm{sgn}(W_{12}) = \mathrm{sgn}(W_{20} W_{21})$$
>
> avec deux variantes :
> - $(W_{12} = +)$ et $(W_{20} W_{21} = +)$
> - $(W_{12} = -)$ et $(W_{20} W_{21} = -)$
>
> Toutes les autres classes effectives sont soit entièrement fixes, soit entièrement instables
> dans la grille de paramètres testée.

---

## Données numériques

### Structure des classes effectives

- **16 classes effectives** au total (déterminées par W01, W10, W12, sgn(W20·W21)).
- Chaque classe contient **192 cas** (64 topologies × 6 permutations × 8 paramétrisations / 16 classes × facteur combinatoire).

### Classes chaotiques

| Classe effective | Complex | Oscillating | Fixed | Unstable |
|---|---|---|---|---|
| `W01=+\|W10=+\|W12=+\|W20W21=+` | **168** | 24 | 0 | 0 |
| `W01=+\|W10=+\|W12=-\|W20W21=-` | **154** | 38 | 0 | 0 |

### Classes non chaotiques

| Classe | Régime unique |
|---|---|
| `W01=+\|W10=-\|...` (toutes variantes) | Fixed = 192 |
| `W01=-\|...` (toutes variantes) | Unstable = 192 |

### Propriétés des cas Complex

- Fraction bornée : **100%**
- Fraction mouvante : **100%**
- Fraction MLE positif : très élevée
- MLE médian : nettement positif
- Exception : la paramétrisation (σ=5, ρ=15, β=8/3) bascule en Oscillating plutôt que Complex dans les deux classes chaotiques — compatible avec le fait que ce régime est sous-critique pour Lorenz canonique.

---

## Condition nécessaire et suffisante (au niveau des classes effectives)

### Ce qui était dit après v1 (incorrectement généralisé)
> "La boucle excitatrice bidirectionnelle 0↔1 est nécessaire et suffisante."

### Correction v2

$W_{01} = +$ et $W_{10} = +$ sont **nécessaires** mais **non suffisants**.

La condition nécessaire **et suffisante** au niveau des classes effectives dans la famille testée est :

$$W_{01} = +, \quad W_{10} = +, \quad \mathrm{sgn}(W_{12}) = \mathrm{sgn}(W_{20} W_{21})$$

Autrement dit : la boucle excitatrice bidirectionnelle 0↔1 doit être présente, **et** le couplage indirect $W_{12}$ doit être **aligné en signe** avec le produit $W_{20} W_{21}$.

---

## Interprétation dynamique

La condition $\mathrm{sgn}(W_{12}) = \mathrm{sgn}(W_{20} W_{21})$ garantit que le terme croisé effectif de la troisième équation :

$$\dot{x}_2 = (W_{20} \cdot W_{21}) \, x_0 x_1 - \beta x_2$$

et le terme inhibiteur de la deuxième équation :

$$\dot{x}_1 = W_{10} \cdot x_0 \cdot (\rho - W_{12} \cdot x_2) - x_1$$

sont **cohérents en signe** : le produit $W_{12} \cdot (W_{20} W_{21})$ est positif dans les deux cas chaotiques. Cela reproduit structurellement le mécanisme de Lorenz canonique où le terme $-xz$ dans $\dot{y}$ et le terme $+xy$ dans $\dot{z}$ ont des signes complémentaires assurant le confinement de l'attracteur.

---

## Déduction de fond

1. **Le cadre additif** $\dot{x} = -\alpha x + W\phi(x)$ avec $\phi$ monotone : **0 chaos borné** dans tous les scans (64 topologies, multi-NL, poids réels, retards, Nona dense).

2. **Le cadre à couplages croisés multiplicatifs** (Lorenz signé) : **chaos borné confirmé** dans deux classes effectives précisément caractérisées.

3. **Conclusion structurelle** : le verrou observé dans le programme est bien de nature structurelle — lié à la **forme du couplage**, pas à la taille du réseau ni aux amplitudes des poids.

---

## Note sur W02

L'arc $W_{02}$ (arc 0→2) **n'intervient pas** dans la dynamique Lorenz signée implémentée. Il est absent des équations :

$$\dot{x}_0 = \sigma \cdot W_{01} \cdot (x_1 - x_0)$$
$$\dot{x}_1 = W_{10} \cdot x_0 \cdot (\rho - W_{12} \cdot x_2) - x_1$$
$$\dot{x}_2 = (W_{20} \cdot W_{21}) \cdot x_0 x_1 - \beta \cdot x_2$$

Les 64 labels topologiques se réduisent donc à **16 classes effectives** par rapport à cette dynamique. Toute interprétation en termes de topologies "01E.02I.10E..." doit tenir compte de cette dégénérescence.

---

## Portée exacte de ce résultat

Ce résultat vaut :
- pour le **modèle Lorenz signé** spécifié ci-dessus
- pour les **8 paramétrisations** (σ, ρ, β) de la grille testée
- pour les **64 topologies denses** à 3 nœuds, sous leurs **6 permutations**
- avec **N_IC = 20**, **N_STEPS = 4000**, **DT = 0.0025** (RK4)
- avec le seuil **LYAP_POS_THRESH = 0.05** (normalisé en 1/temps)

Il ne constitue pas une preuve formelle de chaos au sens des exposants de Lyapunov calculés avec une méthode QR complète, ni une preuve de la généralité de ces conditions au-delà du modèle testé.

---

## Prochaines étapes cohérentes (v3 publication-grade)

1. **Portraits d'attracteurs** pour les cas Complex — vérification visuelle de la structure d'attracteur étrange.
2. **Calcul Lyapunov rigoureux** (méthode QR, long horizon) sur les cas Complex confirmés.
3. **Export CSV** + tableau final (topologie / permutation / paramètres / bassin borné / MLE médian).
4. **Mise à jour du manuscrit** — sections 4 (Triadic Threshold Hypothesis) et 9 (Discussion) à réviser.
5. **Analyse formelle** de la condition $\mathrm{sgn}(W_{12}) = \mathrm{sgn}(W_{20} W_{21})$ dans le cadre Thomas–Kaufman / Soulé.

---

*Document auto-suffisant. Indexé au protocole v2 exact.*
