# RUN_NOTES.md — Reproductibilité Tridom

## Seed
- Tous les scripts utilisent `SEED = 42`
- `torch.manual_seed(42)` + `np.random.seed(42)` fixés en début de fichier
- La seed est journalisée dans la sortie console

## Fichiers de sortie

| Script | Sortie | Format |
|---|---|---|
| `tridom_atlas.py` | `tridom_atlas.json` | JSON |
| `test_tridom_calibration.py` | `test009_calibration.csv` | CSV |
| `test_tridom_calibration.py` | `test009_config.json` | JSON (config de reproductibilité) |
| `tridom_tgs_v2.py` | Console (à persister) | — |

## Dépendances
```
pip install -r requirements.txt
```

## Exécution
```bash
python tridom_atlas.py
python test_tridom_calibration.py
python tridom_tgs_v2.py
```

## Notes
- v0.5 working — manuscrit extrait du PDF, patché conceptuellement
- Pipeline Lyapunov : approximation simple (perturbation), pas de QR ré-orthogonalisation
- TGS v2 : résultats en console uniquement (persistance à venir)
