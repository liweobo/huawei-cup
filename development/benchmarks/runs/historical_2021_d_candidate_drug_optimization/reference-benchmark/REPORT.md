# 2021D Final Graduation Post-hoc Benchmark

## 1. Reference Set

Five papers and 291 pages were fully reviewed. Each reviewed PDF reproduces the user-supplied Git blob; independent SHA256 values, page counts, titles, authors, institutions, and method summaries are in [source-ledger.md](source-ledger.md). No reliable official award evidence was present, so all five award levels are `UNKNOWN` and `award_levels_verified = 0`.

The papers are comparison evidence rather than ground truth. Their methods, numbers, assumptions, and claims are audited before use.

## 2. Frozen Graduation Run

The pre-reference summary is frozen in [current-skill-solution.md](current-skill-solution.md) with SHA256 `2b4e65b5a73fe7465e1e34891da91270f2d4f3ffb17b741faa608e8989c95bea`. Neither that file nor `run-001` was changed after reference reading.

The frozen result uses 20 descriptors with mean fold Jaccard `0.812`; Extra Trees with outer MAE `0.538±0.043`, RMSE `0.738±0.046`, and R² `0.729±0.035`; five endpoint-specific ADMET classifiers with PR-AUC `0.801–0.991` and validation-only thresholds; and an exhaustive search over 50 real source candidates using hard ADMET/applicability gates and activity minus one prediction SD.

## 3. Problem / Source Interpretation

All references use breast-cancer and ERα wording, but this is only reference consensus. It does not rewrite the frozen source finding `MIRROR_FILENAME_ERROR`. The frozen run's exact entity reconciliation is also stronger than the papers' generally implicit row alignment. See [problem-interpretation-comparison.md](problem-interpretation-comparison.md).

## 4. Q1 Descriptor Selection

All papers reduce 729 descriptors to 20 using combinations of constant/sparsity checks, correlation/dependence screens, LASSO, RF importance, RFE, SHAP, or voting. R3 has the most substantial repeat-selection procedure. Every paper nevertheless performs supervised selection on the full labeled data before its reported validation, yielding `REFERENCE_FEATURE_SELECTION_LEAKAGE_RISK`. See [q1-feature-comparison.md](q1-feature-comparison.md).

## 5. Q1 Stability

R1, R2, R4, and R5 report a single final Top-N without fold/bootstrap stability. R3 repeats RFE/importance, but its repeats still use all labels and do not make evaluation fold-safe. The frozen mean Jaccard `0.812` and range `0.739–0.905` quantify stability within the outer protocol and remain a clear strength.

## 6. Q2 Activity Modeling

Reference winners are RF, HGBRT, GBRT, LightGBM, and XGBoost. These algorithms expand the comparison set but do not reveal a missing general capability. The frozen Extra Trees model is selected under a stricter full-pipeline protocol. See [q2-activity-comparison.md](q2-activity-comparison.md).

## 7. Q2 Validation

The references use random 75/25 or 80/20 splits, often with CV tuning, but none evaluates the entire selection/tuning pipeline in nested or fold-local form. R2 and R4 reuse held-out information. None defines a clean trivial baseline contract. The frozen run retains a same-fold baseline, outer metrics, fold membership, and candidate prediction dispersion. See [validation-protocol-comparison.md](validation-protocol-comparison.md).

## 8. Q3 Endpoint Semantics

All solutions model Caco-2, CYP3A4, hERG, HOB, and MN separately. R2–R5 use endpoint-specific feature sets; R1 reuses one common 359-feature pool without comparative justification. Desired-state mappings agree except for CYP3A4. See [q3-admet-comparison.md](q3-admet-comparison.md).

## 9. Q3 Imbalance / Metrics

All references report accuracy, and some add ROC-AUC, precision, recall, F1, PR curves, or log loss. None reports the frozen run's complete prevalence-relative PR-AUC, majority baseline, balanced/minority metric, and fold-dispersion evidence. R4 is the broadest reference but places SMOTE before the reported split. The frozen imbalance discipline is stronger.

## 10. Q3 Threshold / Calibration

No paper documents validation-only threshold selection or probability calibration. Thresholds are default/unstated, R5 uses rounding/0.5, and R2 consults test accuracy during penalty choice. The frozen run selects thresholds from validation probabilities and reports calibration diagnostics; no new gap is exposed.

## 11. CYP3A4 Direction

R1, R3, and R5 treat label `1` as favorable; R2 and R4 treat `0` as favorable. None gives a reliable official quotation or cited external definition that closes the dataset-specific mapping. This is `G6 SOURCE / SEMANTIC AMBIGUITY`. Frozen outputs remain `TEST026` under the primary direction, `TEST019` under reversal, and `WITHHELD` unconditionally. See [cyp3a4-semantics-comparison.md](cyp3a4-semantics-comparison.md).

## 12. Q4 Candidate Domain

Every paper searches a continuous descriptor vector (20, 20, 56, 196, or 70 variables). None returns a source candidate ID or reconstructs a molecular graph. The frozen search evaluates the 50 real compounds supplied for prediction, making its candidate identity and feasibility auditable. See [q4-optimization-comparison.md](q4-optimization-comparison.md).

## 13. Q4 ADMET Semantics

R1, R3, and R5 apply an at-least-three favorable rule. R2 uses a manually weighted activity/ADMET scalarization, and R4 uses multiobjective/primary-target logic. Unsupported weighted endpoint sums are not overall ADMET probabilities, and soft weights cannot substitute for declared hard conditions. The frozen run applies hard endpoint and applicability gates before its soft activity ranking.

## 14. Q4 Surrogate Optimization

The reference pipelines optimize model predictions, yet most conclusions do not consistently preserve the surrogate boundary. Descriptor optima lack structure and experimental validation. The frozen run labels its result a conditional surrogate ranking and makes no drug-efficacy or safety claim. See [surrogate-claim-comparison.md](surrogate-claim-comparison.md).

## 15. Applicability Domain

References constrain descriptors mainly by marginal min/max ranges. None checks joint train distance, leverage, neighbor support, density, or predictive disagreement; all receive `SURROGATE_EXTRAPOLATION_UNVERIFIED`. The frozen run applies target-specific empirical support gates. The reusable Skill's dedicated wording is terse, so this capability is rated `ADEQUATE` at the generic level and strong in the run. The ten-condition G1 gate fails. See [applicability-domain-comparison.md](applicability-domain-comparison.md).

## 16. Uncertainty

No reference propagates predictive uncertainty into Q4. R3's repeated optimizer runs measure search variability. The frozen activity-minus-one-fold-SD objective is a transparent uncertainty-aware decision rule and is not claimed as a confidence interval. See [uncertainty-comparison.md](uncertainty-comparison.md).

## 17. Optimization Status

All references use heuristics: GA, NSGA-III, differential evolution, PSO, simulated annealing, or artificial-fish comparison. Their defensible status is `HEURISTIC_BEST_FOUND`; R3 states this limitation most clearly. The frozen exhaustive result is exact only within its declared finite 50-candidate domain.

## 18. Cross-task Integration

The papers conceptually connect Q1/Q2/Q3 to Q4, though R5's appendix leaves the joint activity/ADMET implementation ambiguous. The frozen run additionally preserves feature contracts, aligned IDs, prediction artifacts, hard/soft separation, candidate ledger, and independent reconstruction. See [cross-task-integration-comparison.md](cross-task-integration-comparison.md).

## 19. Numerical Comparability

No reference matches the frozen training rows, fold-safe selection, split membership, tuning policy, metric aggregation, candidate space, CYP3A4 rule, applicability rule, and uncertainty rule. Q2, Q3, and Q4 numbers are therefore `NOT_DIRECTLY_COMPARABLE`. Better point scores are not evidence of a Skill gap. See [numerical-comparability.md](numerical-comparability.md).

## 20. Reference Consensus

All papers choose 20 activity features, a tree-based winning regressor, separate endpoint classifiers, and continuous descriptor optimization. Zero use fold-safe supervised selection, a meaningful Q4 applicability domain, or Q4 predictive uncertainty. CYP3A4 direction splits 3–2. Counts and confidence are in [reference-consensus.md](reference-consensus.md).

## 21. Reference Weaknesses

The dominant weaknesses are full-data feature selection, missing trivial baselines, accuracy-centered imbalance evaluation, threshold/calibration gaps, held-out reuse, arbitrary multi-endpoint scoring, unrealized descriptor vectors, missing applicability and uncertainty, heuristic optimality overstatement, and final-claim promotion. See [reference-weaknesses.md](reference-weaknesses.md).

## 22. Frozen Skill Strengths

The frozen run demonstrates source title reconciliation, exact entity alignment, constant/duplicate/correlation audit, fold-local selection, stability, Q2 baseline and outer validation, endpoint-specific Q3 models, imbalance metrics, validation-only thresholds, calibration, hard/soft separation, a finite candidate domain, empirical applicability, surrogate labeling, uncertainty adjustment, exhaustive search, independent reconstruction, conditional handling of CYP3A4, and no fake drug-discovery claim.

## 23. Frozen Skill Weaknesses

Generic predictive-surrogate applicability guidance remains terse. The source does not resolve CYP3A4 desirability, final candidate labels are unavailable, Q2 has a training/validation gap, and empirical descriptor support cannot prove chemical efficacy/safety. The first item is a P2 documentation weakness; the others are bounded source/model limitations, not workflow failures.

## 24. Existing Skill Coverage

Feature-set discipline, baselines, imbalance handling, threshold provenance, evaluation semantics, hard feasibility, source/evidence provenance, reviewer checks, cross-task evidence, and claim boundaries are `FULLY_PRESENT`. Predictive-surrogate applicability wording and a universal uncertainty pattern are `PARTIALLY_PRESENT`, with concrete guards supplied in this run. See [existing-skill-coverage.md](existing-skill-coverage.md).

## 25. Generalizable Gap Assessment

The only plausible candidate is a dedicated `PREDICTIVE_SURROGATE_APPLICABILITY_DOMAIN_CONTRACT`. It fails G1 because the governing principles already exist, the run did not make or approach a material error, the run-local prompt supplied the concrete guard, and none of the references demonstrates a stronger validated integration. Other differences fall under G2–G6. See [generalizable-gaps.md](generalizable-gaps.md).

## 26. Top-1 Candidate

`top_generalizable_gap: NONE`.

The applicability candidate remains an optional P2 documentation hardening item for release/readiness work. It is not a P0/P1 historical-development gap and is not being implemented in this phase.

## 27. Graduation Assessment

- `SOURCE_AND_ENTITY_PROVENANCE: STRONG`
- `HIGH_DIMENSIONAL_FEATURE_DISCIPLINE: STRONG`
- `REGRESSION_VALIDATION: STRONG`
- `MULTI_ENDPOINT_CLASSIFICATION: STRONG`
- `THRESHOLD_AND_CALIBRATION_DISCIPLINE: STRONG`
- `CROSS_TASK_INTEGRATION: STRONG`
- `SURROGATE_OPTIMIZATION: STRONG`
- `APPLICABILITY_DOMAIN: ADEQUATE`
- `UNCERTAINTY_AWARE_DECISION: STRONG`
- `CLAIM_BOUNDARY: STRONG`
- `SOLUTION_QUALITY: STRONG`
- `OVERALL: STRONG`

The frozen status remains `GRADUATION_BLIND_RUN_VALID_NO_MAJOR_FAILURE`; the graduation verdict remains `PASS`; the frozen run failure level remains `NONE`.

## 28. Historical Development Closure

`HISTORICAL_PROBLEM_DEVELOPMENT_COMPLETE`.

Ten historical problems plus this final post-hoc comparison have not identified a new P0/P1 generalizable integration gap. The historical suite should be frozen. The recommended next action is to move to release/readiness hardening only; no eleventh problem is recommended.

## 29. Final Decision

`2021D_FINAL_REFERENCE_BENCHMARK_COMPLETE`

`FINAL_HISTORICAL_VALIDATION_COMPLETE_NO_MAJOR_GAP`

This decision preserves all frozen artifacts and does not modify the Skill.

Repository and artifact checks are recorded in [validation.md](validation.md).
