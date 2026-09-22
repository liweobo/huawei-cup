# Q4 forecasting comparison

| ID | Information used | Class / strategy | Final claim | Validation of future claim | Key limitation |
|---|---|---|---|---|---|
| Frozen | history available at each origin | TRUE_ORIGIN_BASED_FORECAST; DIRECT 1/3/6-frame proxy and AMOS 5/15/30min diagnostic | proxy improves; no physical crossing | 30/43 common rolling origins, naive baseline, per-horizon errors | source/scale prevent absolute Q4 |
| R1 | all 100 Q3 estimates | B FULL_SEQUENCE_EXTRAPOLATION; Holt | ≈09:05 at 150m | IN_SAMPLE_FIT / NO future validation | printed additive equations vs exponential code; conditional Q3 scale |
| R2 | all 100 Q3 estimates + OCR times | B; linear and GM curve extrapolation | linear 10:44:31; GM ≈2h30 later | IN_SAMPLE_FIT / NO future validation | scale/text/appendix inconsistencies and ambiguous GM origin |
| R3 | all 100 Q3 estimates | B; cubic curve extrapolation | ≈08:50 at 150m | IN_SAMPLE_FIT / NO future validation | long extension of nearly flat series; fixed 42s grid |
| R4 | all 100 Q3 estimates | B; ARIMA, GM, cubic curve extrapolation | cubic 08:50:56 at 150m | IN_SAMPLE_FIT / NO future validation | ARIMA/GM worsen while low-R² cubic clears |
| R5 | all 100 Q3 estimates; interpolated historical augmentation | B; ARIMA + RECURSIVE Seq2seq | 09:29:48–09:37:43 at 150m | short historical split only; NO long-horizon validation | step denominator and crossing-index/origin error; stale appendix code |
| R6 | all 100 Q3 estimates | B; PSO-NGBM + recursive ARMA | 200m at 2016-04-15 07:39:47 | IN_SAMPLE_FIT / NO future validation | hard-coded Q3 scale and 101st-point timestamp overlap |

Using all 100 frames as history at a last-frame origin is not leakage by itself. The missing evidence is prospective-style performance: none of the papers rolls the intended algorithm through earlier origins and scores the resulting future horizons. Their fitted residuals, AIC/BIC, stationarity tests, model agreement and historical short-window accuracy do not validate the long 150m/200m crossing.
