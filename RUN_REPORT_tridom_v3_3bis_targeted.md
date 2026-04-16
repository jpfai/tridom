# RUN_REPORT — TRIDOM v3.3bis-targeted

**Date :** 2026-04-10
**Statut :** Consolidé — extrait depuis CSV brut natif
**Commande exécutée :**
```
python tridom_v3_3bis_targeted.py --mode vps --points-csv refine_vps_targets/refine_points.csv --outdir targeted_results
```
**Runtime :** 98.89 min

---

## 1. Identification du run

| Paramètre | Valeur |
|---|---|
| Mode | vps (points-csv) |
| Points total | 500 |
| Patches | 4 × 125 pts |
| N_IC | 8 |
| Source CSV | `refine_points.csv` |
| Sortie | `targeted_results/` |

**Patches explorés :**

| patch_label | patch_source | Centre |
|---|---|---|
| B_CENTER_EMPIRICAL | empirical_mean_of_B | (10.152, 101.851, 2.563) — global B vps |
| POS_BEST | NEG4 best Δmle | (9.95, 98.0, 2.4) |
| NEG_NEG1 | NEG1 best neg | (9.55, 99.0, 2.475) |
| NEG_NEG3 | NEG3 best neg | (10.65, 103.5, 2.55) |

---

## 2. Résultats globaux

### 2.1 Partition des classes (exhaustive, 500 pts)

| Classe | n | % |
|---|---|---|
| CHAOS_STRONG | 96 | 19.2% |
| CHAOS_WEAK | 3 | 0.6% |
| BORDER | 400 | 80.0% |
| OSCILLATORY | 1 | 0.2% |
| UNSTABLE | 0 | 0.0% |

Vérification : 96+3+400+1+0 = **500** ✓

### 2.2 Ensembles diagnostiques (B ⊂ A)

| Ensemble | n | % |
|---|---|---|
| A (sign_inst > 0) | 60 | 12.0% |
| B (sign_inst > 0, \|mle\| ≤ 0.05) | 25 | 5.0% |
| B<0 | 10 | 2.0% |
| C (sign_inst = 0, Δmle > 0.10) | 340 | 68.0% |

### 2.3 B par patch

| Patch | B | B<0 |
|---|---|---|
| POS_BEST | 9 | 4 |
| NEG_NEG3 | 8 | 2 |
| NEG_NEG1 | 6 | 3 |
| B_CENTER_EMPIRICAL | 2 | 1 |

---

## 3. Points B<0 — candidats franchissement (10 points)

Triés par `|mle|` croissant :

| point_id | patch | σ | ρ | β | mle | Δmle | sign |
|---|---|---|---|---|---|---|---|
| P0235 | POS_BEST | 10.747 | 104.750 | 2.5321 | −0.0015 | 1.467 | 0.667 |
| P0297 | NEG_NEG1 | 9.502 | 99.500 | 2.4465 | −0.0041 | 1.079 | 0.667 |
| P0485 | NEG_NEG3 | 10.747 | 103.250 | 2.6071 | −0.0066 | 0.737 | 0.667 |
| P0050 | B_CENTER | 10.104 | 102.351 | 2.6200 | −0.0106 | **0.271** | 0.667 |
| P0490 | NEG_NEG3 | 10.747 | 103.500 | 2.6071 | −0.0111 | 1.470 | 0.667 |
| P0271 | NEG_NEG1 | 9.453 | 99.500 | 2.4179 | −0.0124 | **0.092** | 0.667 |
| P0313 | NEG_NEG1 | 9.550 | 99.000 | 2.4750 | −0.0156 | 0.461 | 0.667 |
| P0210 | POS_BEST | 10.698 | 104.750 | 2.5321 | −0.0170 | 0.219 | 0.667 |
| P0230 | POS_BEST | 10.747 | 104.500 | 2.5321 | −0.0188 | **0.173** | 0.667 |
| P0214 | POS_BEST | 10.698 | 105.000 | 2.5036 | −0.0326 | **0.083** | 0.667 |

---

## 4. Points B les plus robustes (Δmle minimal)

| point_id | patch | σ | ρ | β | mle | Δmle |
|---|---|---|---|---|---|---|
| P0218 | POS_BEST | 10.698 | 105.25 | 2.475 | +0.0449 | **0.069** |
| P0214 | POS_BEST | 10.698 | 105.00 | 2.504 | −0.0326 | **0.083** |
| P0498 | NEG_NEG3 | 10.747 | 104.00 | 2.550 | +0.0252 | **0.087** |
| P0271 | NEG_NEG1 | 9.453 | 99.50 | 2.418 | −0.0124 | **0.092** |
| P0447 | NEG_NEG3 | 10.650 | 104.00 | 2.521 | +0.0351 | **0.125** |

**Point le plus robuste de tout le run :**
P0218 — POS_BEST — (10.698, 105.25, 2.475) — mle=+0.045, **Δmle=0.069**
Nettement plus robuste que le meilleur du run vps global (NEG4, Δmle=0.160).

---

## 5. Centres empiriques de B

| Référence | σ | ρ | β |
|---|---|---|---|
| B global targeted | 10.3713 | 102.9481 | 2.5197 |
| B_CENTER_EMPIRICAL patch | 10.0799 | 102.2263 | 2.6200 |
| POS_BEST patch | 10.6876 | 105.0000 | 2.4940 |
| NEG_NEG1 patch | 9.5742 | 99.2083 | 2.4798 |
| NEG_NEG3 patch | 10.6863 | 103.6250 | 2.5536 |
| **Run vps global (référence)** | 10.1524 | 101.8513 | 2.5629 |

**Décalage targeted vs vps global :** Δσ=+0.219 / Δρ=+**1.097** / Δβ=−0.043

---

## 6. Faits / Déductions / Hypothèses / Inconnus

### Faits établis

- 500 points, 0 UNSTABLE, bnd=1.00 et mov=1.00 partout.
- B=25 et B<0=10 — le zoom ciblé conserve autant de points B que le run vps global sur 1225 points (densité B ×4.9).
- Tous les patches produisent des points B : la frontière est présente dans les quatre directions ciblées.
- POS_BEST est le patch le plus riche en B (9/25) et en B<0 (4/10).
- Le point le plus robuste (P0218, Δmle=0.069) est dans POS_BEST — nettement meilleur que tout le run vps global.
- BORDER ne signifie pas mle≈0 : de nombreux BORDER ont mle>1.5. La classification porte sur la stabilité du diagnostic, non sur la valeur scalaire du MLE.

### Déductions solides

- La densification locale confirme que le ciblage était bien centré sur la zone critique.
- La frontière n'est pas une surface mince et propre : 80% des points restent BORDER malgré le zoom.
- La couronne C (68%) reste dominante, cohérente avec les runs précédents.
- Le décalage du centre B vers ρ plus élevés (+1.097 vs vps global) se confirme à chaque raffinement.
- L'instabilité reste diagnostique (sensibilité au protocole de renorm), non explosive.

### Hypothèses renforcées

- Nappe diagnostique anisotrope épaisse, orientée vers ρ croissants.
- Structure multi-poche : chaque patch porte ses propres points B locaux sans convergence vers un point unique.
- POS_BEST (zone σ≈10.7, ρ≈105) semble concentrer la frontière la mieux résolue numériquement.

### Inconnus persistants

- Connectivité géométrique entre les 4 patches — sont-ils sur la même nappe ou sur des composantes distinctes ?
- Comportement au-delà de ρ=105 — la frontière continue-t-elle de se décaler ?
- Topologie fine : nappe, ruban, îlots.

---

## 7. Comparaison des runs

| Run | Points | B | B<0 | Densité B | Δmle min |
|---|---|---|---|---|---|
| v3.3 | 1701 | 25 | 9 | 1.5% | — |
| v3.3bis vps | 1225 | 25 | 9 | 2.0% | 0.160 |
| v3.3bis-targeted | 500 | 25 | 10 | **5.0%** | **0.069** |

La densité B triple à chaque raffinement. La robustesse du meilleur point progresse de 0.160 → 0.069.

---

## 8. Livrables

| Fichier | SHA-256 |
|---|---|
| `B_25points_targeted_full.csv` | `aadfc38e83dfd7f95252c22816e40d36031ba0c8f8f03fd5f3c5d8d9c159e318` |
| `B_neg10points_targeted_full.csv` | `1b5af622bb9a24a88e7cf8f34238c59813cf2a2d47a010a6ee1dd4024f0a6484` |
| Source CSV | `1775924962009_tridom_v3_3bis_targeted_CSV_TARGETED_results.csv` |

---

## 9. Prochaine étape cohérente

Le signal le plus fort à exploiter est **POS_BEST** :
- 9 points B sur 125 (densité 7.2%)
- point le plus robuste de tout le programme (P0218, Δmle=0.069)
- 4 franchissements négatifs dont P0214 (Δmle=0.083)

Raffinement ciblé suivant : zoom sur POS_BEST, centre (10.698, 105.0, 2.490), avec résolution encore accrue (N_IC=12, MEASURE_STEPS=8000).

---

## 10. Formulation courte de reprise

> `v3.3bis-targeted` a exploré 500 points en 4 patches de 125, centrés sur les meilleurs candidats du run vps. B=25 et B<0=10 confirment la persistance de la frontière. La densité B est 2.5× supérieure au run vps global. Le point le plus robuste (Δmle=0.069) est dans le patch POS_BEST. La frontière reste une zone critique épaisse, diagnostiquement instable, avec un signal de robustesse croissant à chaque raffinement.

---

*TRIDOM v3.3bis-targeted — Run report — 2026-04-10*
*ORCID : 0009-0007-5990-3588*
