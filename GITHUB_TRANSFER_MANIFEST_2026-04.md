# GITHUB_TRANSFER_MANIFEST_2026-04

**Projet :** Tridom  
**Date du manifest :** 2026-04  
**Objet :** manifest exact de transfert des fichiers pour mise à jour GitHub

---

## 1. Objectif du transfert

Ce manifest définit les fichiers à communiquer à GitHub afin de refléter l'état scientifique actuel du projet Tridom après clarification de l'archive et séparation des branches targeted.

La priorité est de communiquer :

1. la documentation mise à jour,
2. la branche canonique de raffinement targeted multi-patches,
3. le contexte minimal reproductible permettant de comprendre la provenance et le statut.

---

## 2. Fichiers de documentation à pousser

### Cibles documentaires canoniques

- `README.md`
- `RESULTS_STATUS_2026-04.md`
- `BLOCK03_vs_TARGETED_MULTIPATCH500.md`

### Rôle de chaque fichier

* **README.md** — page d'accueil principale de GitHub, contient le bloc de statut courant et la lecture scientifique mise à jour
* **RESULTS_STATUS_2026-04.md** — référence compacte de statut scientifique, explique la hiérarchie canonique et l'interprétation actuelle
* **BLOCK03_vs_TARGETED_MULTIPATCH500.md** — comparaison scientifique finale entre le bloc de référence canonique et la branche targeted canonique

---

## 3. Fichiers canoniques targeted multi-patches à pousser

### 3.1 Fichiers d'extraction

- `B_25points_targeted_full.csv`
- `B_neg10points_targeted_full.csv`

### 3.2 Fichiers de grille d'entrée targeted

- `refine_centers.csv`
- `refine_manifest.json`
- `refine_points.csv`

### 3.3 Sorties brutes canoniques du run targeted

- `1775924962009_tridom_v3_3bis_targeted_CSV_TARGETED_results.csv`
- `tridom_v3_3bis_targeted_CSV_TARGETED_results.json`
- `tridom_v3_3bis_targeted_summary.csv`
- `tridom_v3_3bis_targeted_summary.json`
- `RUN_REPORT_tridom_v3_3bis_targeted.md`

---

## 4. Fichier additionnel fortement recommandé

- `tridom_v3_3bis_targeted.py`

Sans ce script, GitHub recevra les fichiers d'extraction, la grille d'entrée targeted, et les sorties brutes, mais pas le script principal d'exécution qui a produit le run targeted. Pour un dépôt public scientifiquement plus propre, ce fichier devrait être inclus.

---

## 5. Fichiers qui ne doivent PAS être confondus avec la branche targeted canonique

- `pos_best_v2_441pts` — zoom local distinct, ne doit pas être présenté comme le run parent de `multi_patch_500pts`
- Fichiers de `90_review_manual` — ne doivent pas être poussés aveuglément comme résultats canoniques

---

## 6. Narration canonique à communiquer sur GitHub

1. `v3.3bis_vps_reference_7nuclei` est le bloc de référence canonique.
2. `multi_patch_500pts` est la branche canonique de raffinement targeted.
3. La frontière doit actuellement être interprétée comme une zone de transition diagnostique épaisse.
4. Le raffinement targeted :
   - conserve B = 25,
   - augmente B<0 de 9 à 10,
   - augmente la densité frontière de 2.0% à 5.0%,
   - améliore la meilleure robustesse locale de Δmle = 0.160 à Δmle = 0.069.

---

## 7. État de transfert (rempli par l'agent)

| Fichier | Statut | Commit |
|---------|--------|--------|
| README.md | ✅ poussé | e4933df |
| RESULTS_STATUS_2026-04.md | ✅ poussé | e4933df |
| BLOCK03_vs_TARGETED_MULTIPATCH500.md | ✅ poussé | (ce commit) |
| B_25points_targeted_full.csv | ✅ poussé | e4933df |
| B_neg10points_targeted_full.csv | ✅ poussé | e4933df |
| refine_centers.csv | ✅ poussé | 86ad246 |
| refine_manifest.json | ✅ poussé | 86ad246 |
| refine_points.csv | ✅ poussé | 86ad246 |
| 1775924962009_tridom_v3_3bis_targeted_CSV_TARGETED_results.csv | ✅ poussé | 79d7338 |
| tridom_v3_3bis_targeted_CSV_TARGETED_results.json | ✅ poussé | 79d7338 |
| tridom_v3_3bis_targeted_summary.csv | ✅ poussé | 79d7338 |
| tridom_v3_3bis_targeted_summary.json | ✅ poussé | 79d7338 |
| RUN_REPORT_tridom_v3_3bis_targeted.md | ✅ poussé | 79d7338 |
| tridom_v3_3bis_targeted.py | ⬜ non reçu | — |

---

*GITHUB_TRANSFER_MANIFEST_2026-04 — Traçabilité de transfert — 2026-04-16*
