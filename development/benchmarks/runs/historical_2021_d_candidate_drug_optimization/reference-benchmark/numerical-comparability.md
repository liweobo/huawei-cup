# Numerical Comparability

## Q2

Direct comparison requires identical training rows, target transformation, feature-set scope, selection scope, split membership, tuning policy, and metric aggregation. None of the five papers matches the frozen run on those conditions. Their single-split metrics and full-data selection cannot be ranked against repeated outer-fold means as if they measured the same protocol.

| reference | apparently stronger number | comparability decision | reason |
|---|---|---|---|
| R1 | R² `0.7367` vs frozen `0.729±0.035` | `NOT_DIRECTLY_COMPARABLE` | single holdout; full-data feature selection |
| R2 | R² `0.7812` | `NOT_DIRECTLY_COMPARABLE` | test reuse and different model/feature protocol |
| R3 | R² `0.8076` | `NOT_DIRECTLY_COMPARABLE` | single holdout and full-data selection |
| R4 | MSE `0.4424` | `NOT_DIRECTLY_COMPARABLE` | test-informed feature selection; aggregation differs |
| R5 | R² `0.7821` | `NOT_DIRECTLY_COMPARABLE` | pre-CV feature selection and incomplete error metrics |

The frozen mean lies near R1's single-split result, but even that numerical proximity is not evidence of equivalence.

## Q3

Accuracy/AUC values are not directly comparable to the frozen PR-AUC range without identical folds, positive labels, prevalence, threshold, resampling boundary, and metric definition. Reference accuracies do not displace imbalance-aware outer evidence.

## Q4

Direct candidate comparison requires the same candidate space, CYP3A4 direction, ADMET rule, activity output scale, applicability policy, and uncertainty rule. Every reference searches a continuous descriptor space; the frozen run searches 50 real source compounds. Thus all Q4 candidate/score comparisons are `NOT_DIRECTLY_COMPARABLE`.

No reference outputs a source candidate ID, so a match or mismatch with `TEST026`/`TEST019` cannot be evaluated.

## Decision

Numerical superiority under a different or leakage-prone protocol is `G3 REFERENCE DIFFERENCE` or `G5 ALGORITHM / SEARCH QUALITY`. It is not a general Skill gap.
