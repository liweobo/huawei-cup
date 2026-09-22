# Problem Facts

| Question | Input | Output | Target | Constraints | Required deliverable | Data dependency | Claim type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 1,974 training descriptor rows + pIC50 | ranked ≤20 descriptors and screening rationale | pIC50 predictive association | ≤20; fold-safe learned selection | ranked variables, stability, semantic explanation | descriptor + activity training sheets | predictive association |
| Q2 | Q1 policy, training pIC50, 50 descriptor rows | pIC50 and derived IC50_nM predictions | continuous pIC50 | same folds; no prediction-row fitting | model comparison, validation, 50 predictions | Q1 → Q2 | out-of-sample prediction |
| Q3 | training descriptors + five target-specific labels | five probabilities/classes for 50 rows | five independent binary endpoints | endpoint-specific folds/features/thresholds | class audit, baselines, metrics, predictions | descriptor + ADMET sheets | binary prediction |
| Q4 | Q2 predictions, Q3 outputs, observed descriptors | conditional candidate rank and empirical descriptor ranges | finite-candidate constrained ranking | ≥3 favorable endpoints; applicability gate; surrogate claim | baseline, search trace, sensitivity, candidate ledger | Q1 → Q2/Q3 → Q4 | relative surrogate decision |

The problem defines `pIC50` as the negative base-10 logarithmic activity representation; from the supplied nM unit this is `pIC50 = 9 - log10(IC50_nM)`. All 1,974 rows satisfy that identity to a maximum absolute deviation of 2.49e-14.
