# Reference weaknesses

## Cross-paper protocol weaknesses

- Same-time Q1/Q2 estimation is repeatedly called prediction without a future target time.
- The final Q4 issuance is never evaluated through rolling or multiple historical origins.
- No Q4 includes a persistence/naive comparator, common-origin model comparison or future per-horizon errors.
- No Q4 reports a calibrated prediction interval or empirical coverage.
- Fit residuals, AIC/BIC, stationarity tests, agreement between models and short historical splits are used as confidence for much longer extrapolations.
- Every absolute highway curve relies on external/reference-only/author-assumed metric scale; no paper validates it against paired highway MOR.
- Five papers report a 150m crossing despite the unclosed calibration + validation chain; R6 changes the threshold to 200m.
- Full 100-frame history at an end origin is **not** labelled leakage. The weakness is untested future performance.

## Paper-specific findings

| ID | Findings |
|---|---|
| R1 | Random Q2 image split; incomplete clock contract; assumed 9m Q3 separation; appendix ROI shape/divisor and POI2/POI1 conflicts; additive Holt prose vs exponential code; no Q4 backtest/interval |
| R2 | Q1 training/evaluation reuse; MSE called RMSE; Q2 MOR prose vs RVR code and time-rounding inconsistency; Q3 plotted/text scales conflict and printed `append` expression is invalid as written; ambiguous GM origin; no Q4 backtest/interval |
| R3 | Q2 author-defined 0.8RVR+0.2MOR target; augmentation grouping/split unknown; Q3 scale and C0 assumed; cubic long extrapolation with no backtest/interval |
| R4 | Q1 weak/negative fit still called reliable; Q2 training data explicitly reused for testing after global feature/window selection; Q3 external lane scale/C0 assumption; Q4 models disagree and 150m comes from cubic R²=0.0637; no backtest/interval |
| R5 | Q2 target and split ordering unclear; Q3 road/camera assumptions; interpolated historical short-step validation does not cover final horizon; 100-vs-99 step denominator and origin/index double counting; appendix ARIMA code uses unrelated dates/orders; model spread lacks coverage |
| R6 | Random Q2 split and unspecified 22-class target; calibration prose contradicted by hard-coded 30m; transmission/atmospheric-light code mismatch and `Jdack` typo; Q4 in-sample MAPE only; 101st timestamp overlaps last observation; 200m rule replaces example 150m |

These are G4 reference weaknesses and, where scale/source is involved, G5 limitations. They do not lower current Skill gates or create a new Skill requirement by repetition.
