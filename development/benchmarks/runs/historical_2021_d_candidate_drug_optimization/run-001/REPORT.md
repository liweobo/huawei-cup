# 2021D Final Graduation Blind Run

The blind run completes the chain `Problem → Evidence → Model → Result → Validation → bounded conclusion` without reference solutions or Skill edits. The result is a validated predictive and decision-support analysis of the source's breast-cancer ERα problem; Q4 remains conditional on an unresolved source semantic.

## 1. Source Provenance

Five immutable blobs match every supplied Git ID and retained SHA256. Only allowlisted sources were accessed.

## 2. Source Title Reconciliation

The filename says pancreatic cancer, while the internal title, body, ERα target, and datasets consistently say breast cancer. Classification: `MIRROR_FILENAME_ERROR`.

## 3. Problem Facts

Q1 ranks descriptors, Q2 predicts continuous activity, Q3 predicts five binary endpoints, and Q4 performs a constrained relative decision over source candidates.

## 4. Data Audit

Training data contain 1,974 compounds and 729 descriptors; prediction data contain 50. There are 225 constants, 264 exact duplicate columns, and no modeling missing values.

## 5. Entity Alignment

Exact SMILES sets and order agree across the three modeling workbooks; IDs are unique and train/test overlap is zero.

## 6. Target Definitions

Q2 models supplied pIC50; all ADMET endpoints are binary. Favorable labels are 1/1/0/1/0 in the primary Caco-2/CYP3A4/hERG/HOB/MN map, with CYP3A4 marked assumed.

## 7. Q1 Descriptor Audit

Scale ratio is 6.34e+06; 658 pairs have |r|≥0.95. Extreme candidates are flagged rather than automatically deleted.

## 8. Q1 Feature Selection

Fold-local filtering and F-regression select at most 20 activity descriptors. The final list is semantically mapped from the supplied dictionary.

## 9. Q1 Stability

Mean pairwise Jaccard is 0.812; the result is stable enough for a predictive feature set but is not called uniquely true or causal.

## 10. Q2 Baseline

Mean baseline RMSE is 1.423; median baseline RMSE is 1.423.

## 11. Q2 Activity Model

Extra Trees is selected over Ridge under the frozen RMSE rule; final parameters are `{'model__max_features': 0.5, 'model__min_samples_leaf': 1}`.

## 12. Q2 Validation

Outer MAE 0.538±0.043, RMSE 0.738±0.046, R² 0.729±0.035.

## 13. Q2 Predictions

All 50 pIC50 and IC50_nM outputs are generated only after model-family freeze; outer-fold prediction SD is retained.

## 14. Q3 Endpoint Audit

All five endpoints contain only labels 0 and 1 and have no missing training labels.

## 15. Q3 Class Distributions

Positive prevalence ranges from 0.258 for HOB to 0.767 for MN; every endpoint is evaluated against its own majority baseline.

## 16. Q3 Baselines

Majority Balanced Accuracy is 0.5 and majority PR-AUC equals endpoint prevalence; accuracy is never the sole criterion.

## 17. Q3 Models

Caco-2 logistic PR-AUC 0.892; CYP3A4 logistic PR-AUC 0.984; hERG extra_trees PR-AUC 0.958; HOB extra_trees PR-AUC 0.801; MN extra_trees PR-AUC 0.991.

## 18. Q3 Calibration / Thresholds

Brier and ten-bin calibration error are retained. Each threshold comes from validation-only probabilities after family freeze.

## 19. Q3 Predictions

The 50-row output retains endpoint probabilities, fold variation, thresholds, and classes separately; no composite probability is invented.

## 20. Q4 Decision Target

The decision ranks the fixed 50 source compounds, answering a relative candidate-selection question.

## 21. Q4 Design Variables

The only decision variable is candidate choice. Descriptor coordinates are observed attributes and cannot be edited independently.

## 22. Q4 Feasibility

Finite descriptors, ≥3 favorable endpoints, and all target-specific applicability gates are hard constraints.

## 23. Q4 Applicability Domain

Each surrogate uses selected-feature range checks and a q95 nearest-neighbor RMS standardized-distance gate.

## 24. Q4 Surrogate Models

Q2 activity and five Q3 probabilities/classes are labeled SURROGATE. Experimental activity and ADMET are not claimed.

## 25. Q4 Multi-objective Semantics

ADMET is a hard gate; activity minus one prediction SD is the sole soft objective. No arbitrary activity/ADMET weighted sum is used.

## 26. Q4 Baseline Candidate

Direction-robust observed baseline TRAIN1423 has pIC50 8.772 and IC50 1.691 nM.

## 27. Q4 Search

All 50 candidates are enumerated. A synthetic four-candidate check proves hard gates and incumbent updates precede objective competition.

## 28. Q4 Results

Primary direction selects TEST026; reversed CYP3A4 selects TEST019. The result is conditional.

## 29. Cross-task Dependency

Q1 policy feeds Q2; Q3 learns endpoint-specific feature sets; Q2 predictions, uncertainty, Q3 probabilities/classes/thresholds, and descriptor-domain records feed Q4.

## 30. Independent Audit

Q2 20/20, Q3 75/75, Q4, and artifact hashes all pass.

## 31. Sensitivity / Robustness

CYP3A4 direction changes the candidate; uncertainty penalties 0/1/2 do not change the top candidate within either direction. q90/q95/q99 domain pass counts are retained.

## 32. Claim Boundaries

Allowed: predictive association, held-out performance, relative surrogate rank. Forbidden: causality, new drug discovery, synthesis feasibility, or verified safety/efficacy.

## 33. Negative Results

No direction-robust test winner exists under the current hard-gate semantics. The highest predicted-activity compound fails the ADMET gate. These results are retained.

## 34. Skill Strengths

Validation-safe feature selection, imbalanced classification, evaluation semantics, feasibility-first search, provenance, and independent review all work together.

## 35. Skill Weaknesses

Generic predictive-surrogate applicability guidance is terse. This run still closes the boundary without a P0/P1 failure; the weakness is P2.

## 36. First Meaningful Failure

`NONE`. The first material limit is the source-specific CYP3A4 desirability ambiguity, handled before ranking.

## 37. Failure Classification

Failure level `NONE`; no model, dependency, feasibility, audit, or claim chain is invalidated.

## 38. Generalizable Gap Candidate

`NO_CONFIRMED_GAP`. The gap gate is not met because the actual run remains correct and auditable.

## 39. Historical Integrity

`skill/` and all frozen historical assets remain unchanged; the final integrity record and Git path audit verify that only this new run is submitted.

## 40. Graduation Verdict

**GRADUATION_BLIND_RUN_VALID_NO_MAJOR_FAILURE**. `graduation_verdict = PASS`.
