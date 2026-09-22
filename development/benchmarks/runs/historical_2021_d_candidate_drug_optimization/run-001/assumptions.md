# Assumptions Register

| Assumption | Provenance | Use | Sensitivity or boundary |
| --- | --- | --- | --- |
| CYP3A4=1 counts as favorable | ASSUMED | primary Q4 hard gate | reversed to CYP3A4=0; selected candidate changes, so no unconditional candidate claim |
| q95 leave-one-out nearest-neighbor distance plus selected-feature ranges defines applicability | DERIVED | Q4 hard domain gate | q90/q99 pass counts retained; it is an empirical support rule, not synthetic feasibility |
| activity objective subtracts one outer-fold prediction SD | DERIVED | Q4 ranking | penalties 0, 1, and 2 checked |
| top 20 regression and top 30 classification descriptors | DERIVED capacity control | target-specific pipelines | selection re-fit within every training fold |
| source test rows represent prediction-only compounds | PROBLEM_GIVEN | all tasks | never used to fit selection, scaling, hyperparameters, or thresholds |

No arbitrary continuous descriptor perturbation, molecular reconstruction, or synthesis claim is assumed.
