# Forecast-origin comparison

| ID | Stated/recoverable origin | Status | Index/time issue |
|---|---|---|---|
| Frozen highway | last available highway frame at issuance | EXPLICIT | origin, target frame and horizon recorded per prediction |
| Frozen AMOS | each of 43 historical origins | EXPLICIT | maximum fitting-label time is recorded and ≤ origin |
| R1 | future index begins 2016-04-14 07:39:11 in appendix p52 | RECOVERABLE_BOUNDARY | future grid uses 40s while observed span is not exactly 40s/frame |
| R2 | end of the OCR-timestamped 100-point sequence | FORECAST_ORIGIN_UNSPECIFIED | GM step/count semantics unclear |
| R3 | after x=1…100 beginning 06:30:26 | FORECAST_ORIGIN_UNSPECIFIED | 42s regularization replaces actual timestamps |
| R4 | inferred after 07:39:11 | FORECAST_ORIGIN_UNSPECIFIED | cubic plot extends the series without an issuance record |
| R5 | explicitly after 07:39:11 | EXPLICIT_BOUNDARY | crossing index counted from series start, then full index time added again to last-frame origin |
| R6 | 101st point labelled 07:39:11 | RECOVERABLE_WITH_AMBIGUITY | last observed endpoint is also 07:39:11 |

No reference records an origin contract comparable to the frozen prediction table (`prediction_as_of_time`, target time/frame, permitted features, fitting cutoff). Three allow the boundary to be located; only R5 clearly describes the last frame as the clock origin, and its subsequent index conversion is inconsistent.
