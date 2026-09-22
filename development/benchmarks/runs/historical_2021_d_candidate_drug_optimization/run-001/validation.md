# Validation

## Layers

- **DATA VALIDATION:** all blobs, sheets, transforms, IDs, missingness, duplicates, formulas, and train/test boundaries audited.
- **MODEL VALIDATION:** nested fold-safe Q2/Q3 comparison with baselines, variation, calibration, thresholds, and overfitting audit.
- **TASK-DEPENDENCY VALIDATION:** Q1 policy feeds Q2; Q3 uses independent target-specific policies; Q2/Q3 outputs join by candidate ID/SMILES into Q4.
- **OPTIMIZATION FEASIBILITY:** hard ADMET and applicability gates precede the objective; all 50 candidates are enumerated; synthetic guard passes.
- **CLAIM VALIDATION:** ranks remain relative surrogate outputs; descriptor associations are not causal or chemically generative.

## Repository and run checks

| Check | Exit | Classification | Evidence |
| --- | --- | --- | --- |
| smoke_test | 1 | EXISTING_SMOKE_FAILURES_PRESERVED | - unfinished placeholder in: development\benchmarks\runs\historical_2007_a_food_safety_evaluation\run-001\vali |
| routing_test | 0 | PASS | Routing Heuristic Test: 50/50 passed \| {'normal': 12, 'adversarial': 20, 'risk': 10, 'non_trigger': 4, 'ambigu |
| trigger_test | 0 | PASS | Trigger Boundary Test: 44/44 passed |
| adversarial_trigger_test | 0 | PASS | false positives=0, false negatives=0 |
| behavior_contract_test | 0 | PASS | Static Behavior Contract: PASS (10 contracts) |
| trajectory_test | 0 | PASS | Trajectory Benchmark: PASS (4 trajectories, 52 turns) |
| trajectory_safety_test | 0 | PASS | Trajectory Safety Test: 8/8 passed |
| historical_artifact_test | 0 | PASS | Historical Artifact Test: PASS (27/27 checks) |
| postmortem_regression_test | 0 | PASS | Postmortem Regression Test: PASS (7/7 checks) |
| problem_facts_test | 0 | PASS | Problem Facts Regression: PASS (42/42 checks) |
| run001_integrity_test | 0 | PASS | Run-001 Integrity Test: PASS (10/10 checks) |
| run002_integrity_test | 0 | PASS | Run-002 Integrity Test: PASS (15/15 checks) |
| run003_integrity_test | 0 | PASS | Run-003 Integrity Test: PASS (11/11 checks) |
| run_attempt_integrity_test | 0 | PASS | Run Attempt Integrity: PASS (14/14 checks) |
| clean_room_regression_test | 0 | PASS | Clean-room Regression Test: PASS (13/13 checks) |
| temporal_availability_regression_test | 0 | PASS | Temporal Availability Regression: PASS (10/10 checks) |
| runtime_binding_regression_test | 0 | PASS | Runtime Binding Regression: PASS (17/17 checks) |
| portable_runtime_regression_test | 0 | PASS | 32 passed in 16.82s |
| repository_packaging_regression_test | 0 | PASS | 6 passed in 0.13s |
| phase5_regression_test | 0 | PASS | Phase 5 Regression Test: PASS (15/15 checks) |
| protocol_order_regression_test | 0 | PASS | Protocol Order Regression Test: PASS (0 failures) |
| development_tests | 0 | PASS | 321 passed in 36.66s |
| graduation_artifact_tests | 0 | PASS | 5 passed in 0.42s |
| compileall | 0 | PASS | PASS |
| skill_only_package | 0 | PASS | C:\Users\lwb\Desktop\test\huawei-cup\.tmp\2021d-validation\huawei-cup-2026-skill.zip |

Effective regression status: **PASS**. `development/tests` reports 321 passed; graduation artifact checks report 5 passed. `DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING` remains because the default interpreter lacks pytest. Structural smoke retains the previously frozen four path/placeholder findings and is classified `EXISTING_SMOKE_FAILURES_PRESERVED`; no historical file was changed to silence them.
