# Future-feature comparison

| ID | Q4 exogenous variables | Availability at origin | Future-target feedback | Finding |
|---|---|---|---|---|
| Frozen | current-origin weather and causal lags in AMOS; highway history only | KNOWN at each origin | DIRECT models; no observed future targets | PASS |
| R1 | none in final Holt Q4 | not applicable | no established observed-future feedback | no leakage shown |
| R2 | none in linear/GM Q4 | not applicable | no established observed-future feedback | no leakage shown |
| R3 | none; weather is qualitative explanation | not applicable | no recursive formal feedback | no leakage shown |
| R4 | none in ARIMA/GM/cubic Q4 | not applicable | no established observed-future feedback | no leakage shown |
| R5 | none | not applicable | Seq2seq feeds predictions into later steps | formal future path is recursive, not teacher-forced |
| R6 | none | not applicable | ARMA dynamic recursion | no observed-future target shown |

The references do not demonstrate realized-future weather leakage in their published Q4 models. Several mention temperature, sunlight or humidity as causal explanations, but do not enter realized future values into the forecast equation. This evidence supports retaining the current Temporal Availability Contract; it does not reveal a new contract gap.
