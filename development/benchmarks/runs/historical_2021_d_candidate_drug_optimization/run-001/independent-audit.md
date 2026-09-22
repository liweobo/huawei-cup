# Independent Audit

- Q2: 20/20 saved model-fold prediction groups reproduce MAE, RMSE, and R² within 1e-12.
- Q3: 75/75 endpoint/model/fold groups reproduce probability metrics, threshold metrics, confusion counts, Brier, and calibration error within 1e-12.
- Q4: favorable counts, six applicability gates, feasibility, uncertainty-adjusted objective, feasible count, and selected rank all reproduce from `candidate-ledger.csv`.
- Prediction/ledger hashes: **PASS**.
- Overall independent audit: **PASS**.

The audit reads retained CSV/JSON records and does not trust model console text or serialized estimators.
