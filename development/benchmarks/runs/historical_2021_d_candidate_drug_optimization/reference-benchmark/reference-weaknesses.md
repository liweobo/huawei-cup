# Reference Weaknesses

## Per-paper audit

| weakness | R1 | R2 | R3 | R4 | R5 |
|---|:---:|:---:|:---:|:---:|:---:|
| full-data supervised feature selection before CV/holdout | ✓ | ✓ | ✓ | ✓ | ✓ |
| no fold-safe feature stability | ✓ | ✓ | partial: repeats, still full-data | ✓ | ✓ |
| no explicit trivial regression baseline | ✓ | ✓ | ✓ | partial | ✓ |
| imbalance evaluation centered on accuracy | partial | ✓ | ✓ | partial | ✓ |
| test/holdout reused for selection or tuning | — | ✓ | unclear | ✓ | unclear |
| threshold provenance missing/default | ✓ | ✓ | ✓ | ✓ | fixed/default |
| calibration absent | ✓ | ✓ | ✓ | ✓ | ✓ |
| arbitrary endpoint/activity weighting | — | ✓ | — | partial | — |
| overall endpoint-score semantics weak | — | ✓ | — | partial | partial |
| CYP3A4 direction lacks authoritative provenance | ✓ | ✓ | ✓ | ✓ | ✓ |
| descriptor feasibility unverified | ✓ | ✓ | ✓ | ✓ | ✓ |
| no meaningful applicability-domain check | ✓ | ✓ | ✓ | ✓ | ✓ |
| Q4 prediction uncertainty absent | ✓ | ✓ | ✓ | ✓ | ✓ |
| no best observed/feasible baseline under same Q4 rule | ✓ | ✓ | ✓ | ✓ | ✓ |
| heuristic result described too strongly | ✓ | ✓ | no: limitation stated | partial | ✓ |
| no independent audit/reconstruction | ✓ | ✓ | ✓ | ✓ | ✓ |
| final claim exceeds predictive evidence | ✓ | ✓ | partial | ✓ | ✓ |

`—` means the specific weakness was not needed for that paper's formulation; it does not imply a fully valid protocol.

## Required named findings

- `REFERENCE_FEATURE_SELECTION_LEAKAGE_RISK`: R1–R5.
- `REFERENCE_DATA_LEAKAGE`: R2 test-guided penalty/model decisions; R4 test-informed feature choice and pre-split SMOTE risk.
- `CROSS_TARGET_FEATURE_REUSE_UNJUSTIFIED`: R1.
- `REFERENCE_ARBITRARY_WEIGHTING`: R2; partially R4 where objective preference/provenance is not source-derived.
- `REFERENCE_OUTPUT_SEMANTICS_WEAKNESS`: weighted endpoint rewards are not calibrated overall ADMET probabilities.
- `DESCRIPTOR_FEASIBILITY_UNVERIFIED`: R1–R5.
- `SURROGATE_EXTRAPOLATION_UNVERIFIED`: R1–R5.
- `REFERENCE_SURROGATE_CLAIM_OVERREACH`: R1, R2, R4, R5; partly bounded in R3.
- `HEURISTIC_BEST_FOUND`: the defensible status for every reference Q4 result.

## Use in this benchmark

These findings prevent references from serving as ground truth. They do not invalidate every idea in the papers: multi-method screening, boosted trees, endpoint-specific features, and repeated heuristic runs are useful alternatives. The benchmark separates those algorithm ideas from validation and claim weaknesses.
