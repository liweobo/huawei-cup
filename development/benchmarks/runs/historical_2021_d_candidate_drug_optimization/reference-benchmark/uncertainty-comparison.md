# Uncertainty Comparison

| solution | regression uncertainty | classification probability quality | Q4 use | interpretation |
|---|---|---|---|---|
| Frozen `run-001` | outer-fold prediction SD retained for every candidate | Brier/calibration diagnostics and validation-only thresholds | maximize predicted activity minus one prediction SD | uncertainty-aware surrogate decision |
| R1 | none propagated | no calibration | none | point predictions only |
| R2 | none propagated | no calibration | none | point predictions and assumed scalarization |
| R3 | no predictive interval/dispersion | no calibration | repeated DE runs | search variability, not prediction uncertainty |
| R4 | none propagated | log loss reported, no calibration analysis | none | point predictions only |
| R5 | none propagated | no calibration | heuristic comparison | algorithm comparison, not candidate uncertainty |

Fold SD is not a confidence interval and the frozen run does not claim that it is. It is a transparent conservative penalty under one declared model family. Other defensible uncertainty methods could be used, but the references do not demonstrate one.

The difference is a current-run strength, not evidence that every future problem must use the identical `mean − 1 SD` rule. `UNCERTAINTY_AWARE_DECISION` is rated `STRONG`.
