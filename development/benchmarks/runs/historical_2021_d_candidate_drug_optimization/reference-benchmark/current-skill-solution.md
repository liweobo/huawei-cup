# Frozen Current-Skill Solution

## Freeze record

- Benchmark: `historical_2021_d_candidate_drug_optimization`
- Frozen run: `run-001`
- Repository commit: `98df927c567fe26544d8c55515c755f3088303fb`
- Run tree: `2bfd6738fe4428be8f7dfa286b43b5c22448ebdd`
- Source: frozen `run-001` artifacts only
- Reference methods reviewed before this file was written: `NO`
- Status: immutable after SHA256 recording

## Q1

- Final descriptor count: 20
- Selection discipline: fold-local near-constant filtering, exact-duplicate removal, and F-regression screening
- Mean pairwise fold Jaccard: 0.812
- Jaccard range: 0.739-0.905
- Interpretation: predictive association and model importance; no causal claim

## Q2

- Selected model: Extra Trees
- Outer MAE: 0.538 +/- 0.043
- Outer RMSE: 0.738 +/- 0.046
- Outer R-squared: 0.729 +/- 0.035
- Prediction scope: 50 source prediction compounds after model-family freeze
- Uncertainty: outer-fold prediction standard deviation retained

## Q3

- Targets: 5 independent binary ADMET endpoints
- Endpoints: Caco-2, CYP3A4, hERG, HOB, MN
- Selected-model PR-AUC range: 0.801-0.991
- Threshold provenance: validation-only probabilities after model-family freeze
- Evaluation: endpoint-specific prevalence, majority baseline, imbalance metrics, calibration diagnostics, and thresholds

## Q4

- Candidate domain: fixed 50 real source compounds
- Hard constraints: finite descriptors, at least 3 favorable ADMET classifications, and all target-specific applicability-domain gates
- Soft objective: predicted activity minus 1 prediction standard deviation
- Search: exhaustive enumeration of the fixed finite domain
- Primary CYP3A4 direction: `TEST026`
- Reversed CYP3A4 direction: `TEST019`
- Unconditional recommendation: `WITHHELD`
- Reason: the source does not resolve the favorable CYP3A4 label direction
- Claim boundary: conditional surrogate ranking, not experimental drug efficacy or safety

## Graduation status

- First meaningful failure: `NONE`
- Failure level: `NONE`
- Generalizable gap candidate: `NO_CONFIRMED_GAP`
- Final decision: `GRADUATION_BLIND_RUN_VALID_NO_MAJOR_FAILURE`
- Graduation verdict: `PASS`
