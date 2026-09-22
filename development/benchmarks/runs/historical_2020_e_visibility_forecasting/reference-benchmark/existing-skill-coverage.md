# Existing Skill coverage

| Needed capability | Existing location | Coverage | Frozen-run evidence |
|---|---|---|---|
| Target, target time, horizon, lags, exogenous availability | `skill/references/models/prediction.md` | PRESENT | explicit 5/15/30min and 1/3/6-frame targets |
| Time-respecting backtest and naive/seasonal-naive baseline | prediction and evaluation-metrics references | PRESENT | rolling/common origins and persistence |
| Forecast origin / cutoff | `skill/references/gotchas.md`, workflows | PRESENT | origin and maximum fitting-label time recorded |
| Temporal Availability Contract | gotchas, experiment rule, reviewer, `scripts/temporal_availability.py` | PRESENT | future weather/targets and post-cutoff aggregations excluded |
| Fold/origin-safe preprocessing | experiment/model workflows | PRESENT | scaler and Ridge fit inside each origin |
| Random-split future warning | prediction/gotchas/reviewer | PRESENT | synthetic guards reject random future splits |
| Multi-step target discipline | prediction reference | PRESENT; taxonomy terse | DIRECT horizon-specific models executed correctly |
| Common-origin/model comparability | experiment/evaluation rules | PRESENT in same-task/split/metric constraints; presentation terse | persistence and Ridge use identical origins/targets |
| Per-horizon MAE/RMSE and coverage | evaluation-metrics/prediction | PRESENT | separate horizon tables and empirical coverage |
| Low-visibility, shift, caps and failure analysis | evaluation guidance + executed run | PRESENT | subset metrics, KS shift, cap errors and residual diagnostics |
| Absolute/relative output and physical claim boundary | `skill/references/evaluation-semantics.md`, modeling rule, design/validate workflows | PRESENT | proxy is not promoted to metres or 150m time |
| Runtime provenance and invalidation | `skill/scripts/runtime_provenance.py` | PRESENT | frozen reports retain cutoffs/status/limitations |

Two documentation areas are terse: named DIRECT/RECURSIVE/DIRREC/MULTI_OUTPUT strategies and a compact common-origin presentation contract. The frozen run nevertheless chose DIRECT, used common origins and reported per-horizon metrics correctly. G1 requires an actual frozen-run correctness failure caused by a missing Skill capability; neither wording gap meets that condition.

The helper's target-only cutoff fallback was reviewed. It did not create a failure in this run, whose origins and target times were explicit. Physical identifiability is already covered by parameter/unit provenance plus output semantics. A new proxy-to-metres forecasting gate would duplicate existing coverage.
