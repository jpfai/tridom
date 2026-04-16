# BLOCK03_vs_TARGETED_MULTIPATCH500

**Projet :** Tridom  
**Date de comparaison :** 2026-04  
**Objet :** comparaison scientifique finale entre le bloc de référence canonique (`03_v3.3bis_vps_reference_7nuclei`) et la branche targeted canonique (`multi_patch_500pts`)

---

## 1. Portée

Ce document compare :

- le bloc de référence canonique :
  - `TRIDOM_ARCHIVE/03_v3.3bis_vps_reference_7nuclei/`
- la branche canonique de raffinement ciblé :
  - `TRIDOM_ARCHIVE/04_targeted_extraction/multi_patch_500pts/`
  - `TRIDOM_ARCHIVE/05_targeted_input_grid/multi_patch_500pts/`
  - `TRIDOM_ARCHIVE/06_targeted_run_results/multi_patch_500pts/`

Son objectif est de répondre à une question précise :

> Qu'apporte scientifiquement le raffinement targeted multi-patches par rapport au bloc de référence actuel ?

Ce document **ne compare pas** la branche targeted avec `pos_best_v2_441pts`, qui constitue un zoom local distinct.

---

## 2. Statut canonique des deux objets comparés

### 2.1 Bloc de référence

Le bloc de référence scientifique actuel est :

- `v3.3bis_vps_reference_7nuclei`

Ce bloc doit être traité comme la base canonique pour l'interprétation actuelle de la frontière.

### 2.2 Branche targeted

La branche targeted canonique actuelle est :

- `multi_patch_500pts`

Cette branche n'est pas un remplacement du bloc 03.  
C'est une couche de raffinement construite à partir de l'extraction des candidats du bloc 03.

---

## 3. Provenance des données

### 3.1 Bloc de référence

Le bloc de référence correspond au run dense `v3.3bis` sur 7 noyaux :

- total de points : `1225`
- statut canonique : référence
- niveau de lecture : référence frontière avant raffinement targeted

### 3.2 Branche targeted

La branche targeted multi-patches est construite comme suit :

1. extraction de :
   - `B_25points.csv`
   - `B_neg9points.csv`
2. planification du raffinement targeted :
   - `refine_centers.csv`
   - `refine_manifest.json`
   - `refine_points.csv`
3. exécution targeted sur `500` points explicites
4. extraction de :
   - `B_25points_targeted_full.csv`
   - `B_neg10points_targeted_full.csv`

Le fichier brut parent canonique des résultats est :

- `1775924962009_tridom_v3_3bis_targeted_CSV_TARGETED_results.csv`

Ce fichier constitue le parent brut de l'interprétation des résultats targeted multi-patches.

---

## 4. Comparaison numérique

### 4.1 Comptages globaux

| Quantité | Bloc 03 (`v3.3bis_vps_reference_7nuclei`) | Targeted `multi_patch_500pts` |
|----------|--------------------------------------------|-------------------------------|
| Total de points | 1225 | 500 |
| `B` | 25 | 25 |
| `B<0` | 9 | 10 |
| `UNSTABLE` | 0 | 0 |

#### Lecture immédiate

- la branche targeted **n'augmente pas** le nombre total de `B` ;
- elle **augmente** le nombre de `B<0` de `9` à `10` ;
- elle travaille sur une région de l'espace des paramètres **plus petite et plus dense**.

---

### 4.2 Densité de frontière

#### Bloc 03
- `densité B = 25 / 1225 ≈ 2.0%`

#### Targeted multi-patches
- `densité B = 25 / 500 = 5.0%`

#### Interprétation

La branche targeted fait plus que doubler la densité des candidats frontière.

C'est une indication forte que le raffinement n'est pas aléatoire :
il concentre l'effort computationnel sur une région où la structure frontière apparaît plus fréquemment.

---

### 4.3 Densité négative de frontière

#### Bloc 03
- `densité B<0 = 9 / 1225 ≈ 0.735%`

#### Targeted multi-patches
- `densité B<0 = 10 / 500 = 2.0%`

#### Interprétation

La branche targeted augmente significativement la concentration de candidats du côté négatif.

Cela **ne prouve pas** l'existence d'une surface de franchissement unique,
mais améliore l'accès numérique au côté négatif de la zone de transition.

---

### 4.4 Meilleure robustesse locale

#### Bloc 03
Meilleur candidat de niveau référence :
- meilleur `Δmle = 0.160`

#### Targeted multi-patches
Meilleur candidat local :
- `P0218`
- patch : `POS_BEST`
- coordonnées : `(10.698, 105.25, 2.475)`
- meilleur `Δmle = 0.069`

#### Interprétation

C'est l'amélioration locale la plus nette produite par la branche targeted.

Le raffinement targeted ne se contente pas de rééchantillonner la même information :
il fournit un meilleur candidat frontière du point de vue de la robustesse numérique.

---

## 5. Structure interne de la branche targeted

Répartition par patch :

| Patch | `B` | `B<0` |
|-------|----:|------:|
| `POS_BEST` | 9 | 4 |
| `NEG_NEG3` | 8 | 2 |
| `NEG_NEG1` | 6 | 3 |
| `B_CENTER_EMPIRICAL` | 2 | 1 |

### Interprétation

La branche targeted n'est pas uniformément informative.

Sa contribution principale se concentre sur :
- `POS_BEST`
- puis `NEG_NEG3`
- puis `NEG_NEG1`

Le patch centré sur le centre empirique apporte moins que les raffinements locaux centrés sur des candidats sélectionnés.

Cela suggère que la structure frontière n'est pas simplement centrée sur le barycentre empirique de `B`,
mais qu'elle se résout mieux près de régions locales choisies.

---

## 6. Interprétation scientifique

### 6.1 Ce qui reste inchangé

La branche targeted **ne renverse pas** la lecture de référence.

Les points suivants restent vrais :

- le système présente une zone frontière non triviale ;
- le phénomène ne se réduit pas à un blow-up numérique ;
- la transition n'est pas correctement décrite comme un point isolé unique.

### 6.2 Ce qui s'améliore

La branche targeted apporte trois gains réels :

1. **une densité plus élevée de candidats frontière**
2. **un meilleur accès au côté négatif**
3. **une meilleure robustesse locale maximale**

Il s'agit d'améliorations effectives, et non d'un simple reclassement cosmétique.

### 6.3 Ce que cela signifie conceptuellement

Le raffinement targeted renforce l'idée que la frontière se comporte comme une :

> **zone de transition diagnostique épaisse**

et non comme :
- un point unique,
- un seuil exact unique,
- ou une surface déjà complètement résolue.

Le raffinement affine l'image locale, mais ne ferme pas encore la question géométrique.

---

## 7. Ce qui est établi, probable et encore ouvert

### Établi
- le bloc 03 est le bloc de référence actuel ;
- le targeted multi-patches conserve `B = 25` ;
- le targeted multi-patches augmente `B<0` de `9` à `10` ;
- le targeted multi-patches augmente la densité frontière de `2.0%` à `5.0%` ;
- le targeted multi-patches améliore le meilleur `Δmle` local de `0.160` à `0.069`.

### Fortement suggéré
- la zone locale la plus prometteuse se concentre désormais autour de `POS_BEST` ;
- la frontière doit être pensée comme une structure locale étendue plutôt que comme un point unique.

### Encore ouvert
- la connectivité géométrique fine entre les patches ;
- la question de savoir si la frontière forme une nappe, un ruban, une structure fragmentée ou des poches connectées ;
- la continuation paramétrique au-delà de la région actuellement raffinée.

---

## 8. Énoncé final de comparaison

La comparaison finale correcte est la suivante :

> Par rapport au bloc de référence canonique `v3.3bis_vps_reference_7nuclei`, la branche targeted `multi_patch_500pts` ne change pas l'interprétation globale du phénomène. Elle la confirme et la densifie. Le nombre total de candidats `B` reste `25`, le nombre de candidats négatifs passe de `9` à `10`, la densité frontière augmente de `2.0%` à `5.0%`, et la meilleure robustesse locale s'améliore de `Δmle = 0.160` à `Δmle = 0.069`. L'ensemble des éléments soutient donc l'interprétation de la frontière Tridom comme une zone de transition diagnostique épaisse plutôt que comme un point critique isolé unique.

---

## 9. Conséquence opérationnelle

Pour la communication du dépôt et du statut GitHub :

- `03_v3.3bis_vps_reference_7nuclei` doit rester le **bloc de référence**
- `multi_patch_500pts` doit être présenté comme la **branche canonique de raffinement**
- `pos_best_v2_441pts` doit rester explicitement séparé

Cette distinction est obligatoire pour la clarté scientifique et la traçabilité du dépôt.

---

*Tridom — Comparaison bloc de référence vs targeted multi-patches — 2026-04*
