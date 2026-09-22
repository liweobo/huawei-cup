# Q2 Results

| Model | MAE mean | MAE SD | RMSE mean | RMSE SD | R² mean | R² SD |
| --- | --- | --- | --- | --- | --- | --- |
| mean | 1.190 | 0.016 | 1.423 | 0.018 | -0.002 | 0.002 |
| median | 1.190 | 0.016 | 1.423 | 0.018 | -0.003 | 0.002 |
| ridge | 0.815 | 0.015 | 1.023 | 0.024 | 0.482 | 0.017 |
| extra_trees | 0.538 | 0.043 | 0.738 | 0.046 | 0.729 | 0.035 |

Selected model: **extra_trees**, final parameters `{'model__max_features': 0.5, 'model__min_samples_leaf': 1}`. The 50 predicted pIC50 values span 5.075–9.824; outer-fold uncertainty SD spans 0.042–1.426. `q2-test-predictions.csv` contains candidate IDs, original SMILES, pIC50, derived IC50_nM, and uncertainty.
