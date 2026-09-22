# Q1 estimation comparison

| ID | Target | Method | Generalization classification | Sensor cap treatment | Future forecast evidence? |
|---|---|---|---|---|---|
| Frozen | MOR | contemporaneous log-MOR Ridge; other-event median baseline | EVENT_HOLDOUT diagnostic; unstable transfer | 0–10,000m distribution and cap pileup disclosed | NO; explicitly estimation |
| R1 | MOR | correlation/Lasso + cubic regressions | TRAIN_FIT_ONLY | >10,000m range discussed | NO |
| R2 | RVR and MOR | normalized OLS | TRAIN_FIT_ONLY; 2020 rows reused after combined fit | 10,000m cap named, no censor model | NO |
| R3 | MOR | correlation + separate-date nonlinear regression | TRAIN_FIT_ONLY; each date fitted separately | not reported | NO |
| R4 | MOR | correlation + GA nonlinear regression | TRAIN_FIT_ONLY | not reported | NO |
| R5 | RVR | hand-selected nonlinear transforms + regression | TRAIN_FIT_ONLY | 3,000m plateau used as piecewise level | NO |
| R6 | RVR and MOR | quantile/nonlinear regression | TRAIN_FIT_ONLY; forms/quantiles selected on same sample | 3,000/10,000m ceilings explicitly recognized | NO |

All six references use the word “prediction” in places, but their Q1 evidence is contemporaneous estimation. None establishes a target time after a forecast origin or a temporal/event holdout that supports a future claim. The frozen solution's separation is therefore retained as a strength.
