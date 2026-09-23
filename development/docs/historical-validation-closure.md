# Historical Validation Closure

- Final historical main base: `79f505df99960ab6aa988d9138dfd28079b6252d`.
- Historical development: `HISTORICAL_PROBLEM_DEVELOPMENT_COMPLETE`.
- Final comparison: `2021D_FINAL_REFERENCE_BENCHMARK_COMPLETE`;
  `FINAL_HISTORICAL_VALIDATION_COMPLETE_NO_MAJOR_GAP`.
- Graduation: `PASS` / `GRADUATION_BLIND_RUN_VALID_NO_MAJOR_FAILURE`;
  overall skill level `STRONG`; top generalizable gap `NONE`.
- Decision evidence: [final 2021D post-hoc report](../benchmarks/runs/historical_2021_d_candidate_drug_optimization/reference-benchmark/REPORT.md).

## Covered Problem Families

The completed ten-problem sequence covers material/core-loss prediction
(2024C), clinical longitudinal prediction and observational association
(2023E), stateful scheduling (2022C), physical/mechanism closure (2011B),
signal and spectral conventions (2020A), stochastic inventory and event order
(2005D), underground logistics/network decisions (2017F), evaluation and
comparator semantics (2007A), visibility forecasting (2020E), and high-dimensional
multi-endpoint surrogate decisions (2021D). Coverage preserves each run's
source restrictions and verdict; it does not turn incomplete-source findings
into new readiness claims.

## Capability Inventory

This is the single current inventory. Locations are in the distributable
Skill; validation links point to existing active tests or frozen evidence.
`CONFIRMED` records existing readiness, not a guarantee of better scores or a
new model family. The final report above supplies the integration verdict.

| name | location | activation | validation evidence | status |
|---|---|---|---|---|
| TEMPORAL_HORIZON_GATE_READY | [temporal helper](../../skill/scripts/temporal_availability.py), [data workflow](../../skill/workflows/audit-data.md) | Time-dependent features, longitudinal aggregation, future targets | [temporal regression](../harness/temporal_availability_regression_test.py), [2023E tests](../tests/test_2023e_imbalanced_q1.py) | CONFIRMED |
| IMBALANCED_CLASSIFICATION_READY | [imbalance reference](../../skill/references/imbalanced-classification.md), [metrics](../../skill/scripts/metrics.py) | Imbalanced binary targets and probability/threshold claims | [classification tests](../tests/test_imbalanced_classification.py), [2021D validation](../benchmarks/runs/historical_2021_d_candidate_drug_optimization/run-001/validation.md) | CONFIRMED |
| ORDINAL_MODELING_READY | [ordinal reference](../../skill/references/ordinal-modeling.md), [helper](../../skill/scripts/ordinal.py) | Targets with an explicitly sourced order | [ordinal tests](../tests/test_ordinal.py), [2023E Q3](../tests/test_2023e_ordinal_q3.py) | CONFIRMED |
| GROUPED_LONGITUDINAL_VALIDATION_READY | [group reference](../../skill/references/group-validation.md), [helper](../../skill/scripts/group_validation.py) | Repeated entities; entity-aware generalization | [group tests](../tests/test_group_validation.py), [2023E Q2](../tests/test_2023e_group_validation_q2.py) | CONFIRMED |
| OBSERVATIONAL_ASSOCIATION_READY | [association reference](../../skill/references/observational-association.md), [helper](../../skill/scripts/association_analysis.py) | Observational measures/interventions, confounding and dependence | [association tests](../tests/test_association_analysis.py), [2023E association](../tests/test_2023e_association_q2.py) | CONFIRMED |
| VALIDATION_SAFE_FEATURE_SET_DESIGN_READY | [feature reference](../../skill/references/feature-set-design.md), [helper](../../skill/scripts/feature_sets.py) | Feature groups, selection and incremental information claims | [feature tests](../tests/test_feature_sets.py), [2023E feature tests](../tests/test_2023e_feature_sets.py) | CONFIRMED |
| STATEFUL_SCHEDULING_SEARCH_READY | [scheduling reference](../../skill/references/stateful-scheduling.md), [helper](../../skill/scripts/stateful_scheduling.py) | Feasibility depends on evolving state or a verified decoder | [tests](../tests/test_stateful_scheduling.py), [2022C postfix](../benchmarks/runs/historical_2022_c_buffer_scheduling/run-003-postfix/REPORT.md) | CONFIRMED |
| FEASIBILITY_PRESERVING_STRUCTURED_IMPROVEMENT_READY | [improvement reference](../../skill/references/structured-improvement.md), [helper](../../skill/scripts/structured_improvement.py) | Feasible incumbent without exact proof; bounded structural moves | [tests](../tests/test_structured_improvement.py), [retained negative result](structured-improvement-readiness.md) | CONFIRMED |
| MECHANISM_MODEL_CLOSURE_READY | [closure reference](../../skill/references/mechanism-closure.md), [helper](../../skill/scripts/mechanism_closure.py) | Mechanism/physical/dynamic numerical claims | [tests](../tests/test_mechanism_closure.py), [2011B closure gate](../benchmarks/runs/historical_2011_b_absorbing_material_anechoic_chamber/run-002-closure-gate/REPORT.md) | CONFIRMED |
| SPECTRAL_CONVENTION_AND_NORMALIZATION_READY | [spectral reference](../../skill/references/spectral-conventions.md), [helper](../../skill/scripts/spectral_conventions.py) | Sampled signals, Fourier transforms, frequency or power claims | [tests](../tests/test_spectral_conventions.py), [2020A regression](../benchmarks/runs/historical_2020_a_chip_phase_noise/run-002-spectral-contract/README.md) | CONFIRMED |
| ORDERED_PROTOCOL_NORMALIZATION_READY | [runtime provenance](../../skill/scripts/runtime_provenance.py), [experiment rules](../../skill/rules/experiment.md) | Comparing planned and executed ordered protocols | [order regression](../harness/protocol_order_regression_test.py), [2005D evidence](../benchmarks/runs/historical_2005_d_stochastic_inventory/run-002-protocol-order/README.md) | CONFIRMED |
| EVALUATION_TARGET_AND_OUTPUT_SEMANTICS_READY | [semantics reference](../../skill/references/evaluation-semantics.md), [helper](../../skill/scripts/evaluation_semantics.py) | Ranking, evaluation, grading, comparator or decision claims | [tests](../tests/test_evaluation_semantics.py), [2007A regression](../benchmarks/runs/historical_2007_a_food_safety_evaluation/run-002-evaluation-semantics/REPORT.md) | CONFIRMED |
| Trigger boundary and ten-route navigation | [trigger boundary](../../skill/references/trigger-boundary.md), [routing](../../skill/routing.yaml) | Established mathematical-modeling project context | [trigger](../harness/trigger_test.py), [routing](../harness/routing_test.py), [trajectory](../harness/trajectory_test.py) | CONFIRMED |
| Source/data audit and evidence provenance | [data audit](../../skill/scripts/data_audit.py), [evidence rules](../../skill/rules/evidence.md) | Inputs, real experiments and paper evidence | [audit tests](../tests/test_data_audit.py), [historical integrity](../harness/historical_artifact_test.py), [postmortem](../harness/postmortem_regression_test.py) | CONFIRMED |
| Baseline comparison and model selection | [model selection](../../skill/references/model-selection.md), [baseline workflow](../../skill/workflows/build-baseline.md) | Selecting or claiming improvement over a model | [behavior contracts](../harness/behavior_contract_test.py), [2021D frozen report](../benchmarks/runs/historical_2021_d_candidate_drug_optimization/run-001/REPORT.md) | CONFIRMED |
| Validation, sensitivity and robustness | [validation workflow](../../skill/workflows/validate-model.md), [metrics reference](../../skill/references/evaluation-metrics.md) | Generalization, feasibility, uncertainty and perturbations | [sensitivity](../tests/test_sensitivity.py), [robustness](../tests/test_robustness.py), [metrics](../tests/test_metrics.py) | CONFIRMED |
| Run isolation and active evidence binding | [runtime helper](../../skill/scripts/runtime_provenance.py), [experiment record](../../skill/templates/experiment-record.yaml) | Real execution and cross-task evidence consumption | [clean room](../harness/clean_room_regression_test.py), [runtime binding](../harness/runtime_binding_regression_test.py) | CONFIRMED |
| Paper/reviewer/claim and submission checks | [reviewer](../../skill/workflows/reviewer.md), [final check](../../skill/workflows/final-check.md) | Paper claims, traceability and submission readiness | [behavior contracts](../harness/behavior_contract_test.py), [2021D reviewer](../benchmarks/runs/historical_2021_d_candidate_drug_optimization/run-001/reviewer-report.md) | CONFIRMED |

## Remaining P2 Items

The retained P2 item is terse predictive-surrogate applicability wording.
Existing [validation](../../skill/workflows/validate-model.md),
[hard feasibility](../../skill/rules/modeling.md), and [claim review](../../skill/workflows/reviewer.md)
already provide navigation. Keep applicability `ADEQUATE` at the generic
level; do not add a dedicated contract. A universal uncertainty-to-objective
recipe is not prescribed; that partial coverage is not promoted to a new P2
item. CYP3A4 desirability, unavailable final
labels, training/validation gaps and empirical chemical support remain the
2021D source/model limitations recorded in its report, not release blockers.

## Freeze and Next Maintenance Mode

No problem 11, new historical/reference benchmark, new excellent-paper review,
new algorithm module, or new modeling semantics. All completed historical
runs, source-recovery records, reference comparisons and targeted regressions
under `development/benchmarks/runs/`, plus all `run-attempts/` evidence, are
permanently immutable. This includes 2024C and the archived platform incident;
2023E source/evidence and earlier invalidation decisions also stay unchanged.
No edits to reports, validation, links, wording, formatting, or line endings
may be used to make historical smoke pass.

Maintain active documentation, declared test environments, packaging and
integrity checks only. Live smoke and frozen evidence integrity have separate
scopes. See [release readiness](release-readiness.md) for hashes and results;
after completion, stop and await human release review.
