# 2007A Post-fix Evaluation-Semantics Targeted Regression

## Status

`EVALUATION_TARGET_AND_OUTPUT_SEMANTICS_READY`

This is a `POST_FIX_TARGETED_REGRESSION`, not a blind run and not a re-solution of 2007A. It validates the new generic contract against the frozen semantics and two demonstrated failure modes. It does not rerun the exposure model, estimate `Q_0.99999`, change synthetic outputs, or recompute ranking.

## Capability scope

The fix adds one lightweight Evaluation Target & Output Semantics Contract. It requires, before weighting, normalization, thresholding, ranking, classification, or evaluation-algorithm selection:

- stable `evaluation_object` and `decision_question`;
- `PROBABILITY | QUANTILE | PHYSICAL_ESTIMATE | COMPLIANCE | RELATIVE_SCORE | RANK | CLASS` output type;
- `ABSOLUTE | RELATIVE`, output unit, and output scope;
- comparator value, unit, provenance, source, object/population/geography/time/category scope, and version/date;
- a link to the existing hard-constraint rule rather than a second hard-gate framework;
- human-readable `allowed_claim` plus machine-checkable allowed semantics;
- `VERIFIED | PARTIAL | UNVERIFIED` status.

The helper validates contracts and produces the eight requested reviewer codes. It implements no AHP, entropy weighting, TOPSIS, fuzzy evaluation, probability calibration, statistical risk model, tail estimator, or regulatory database.

## Activation boundary

The contract activates for composite evaluation, relative scoring, ranking/grading, risk indices, threshold/standard comparison, probability-like evaluation output, decision-use quantiles or physical estimates, AHP/entropy/TOPSIS/fuzzy evaluation, and multi-criteria decision. Ordinary regression, predictive classification, optimization objective values, and mechanism parameter estimation do not activate without an evaluation-output-to-decision conversion.

## Frozen 2007A instantiation

The primary contract identifies one declared population × geography × time × food-taxonomy × contaminant cell. Its output is the absolute physical `Q_0.99999` exposure quantile. The comparator is explicitly an `ASSUMED` synthetic fixture with identical unit and scope; it is not represented as a real standard. The existing hard-constraint rule remains the compliance gate. The allowed claim is limited to synthetic threshold-comparison behavior.

The secondary contract is a separate `RELATIVE` `RANK` for noncompensatory monitoring triage among the current frozen synthetic cells. It cannot become probability or legal compliance.

## Targeted results

| case | result | guard |
|---|---|---|
| valid primary absolute quantile | `PASS` | none |
| valid synthetic threshold class | `PASS` | none |
| valid secondary relative triage | `PASS` | none |
| quantile promoted to probability | `BLOCKED` | `QUANTILE_PROBABILITY_CONFLATION` |
| dietary-intake quantile vs blood concentration | `BLOCKED` | `COMPARATOR_SCOPE_MISMATCH` |
| daily-intake quantile vs food-content limit | `BLOCKED` | `COMPARATOR_SCOPE_MISMATCH` |
| frozen run/reference status | `PASS` | run-001 remains `VALID`; reference decision unchanged |

The complete machine-readable results are in `outputs/results.json`.

## Generic regression coverage

The generic suite covers city relative score, supplier rank, calibrated credit probability, loss quantile, education class thresholds, a derived ratio threshold, both 2007A comparator mismatches, relative-score compliance promotion, allowed-claim overreach, hard-threshold noncompensation, and a valid relative city ranking. It also checks fuzzy membership, explicit calibrated conversion, undeclared target/output, and the negative activation boundary.

## Existing rules reused

- Hard safety/legal/feasibility violations still use the existing hard-constraint rule; an excellent soft score cannot compensate.
- Indicator direction, units, weighting, normalization, sensitivity, rank stability/reversal, evidence provenance, missingness, extremes, and redundancy were not redesigned.
- Route count remains `10`.

## Verification

- generic evaluation-semantics tests: `16 passed`;
- generic plus isolated self-contained capability tests: `17 passed`;
- full Python suite: `321 passed`;
- standalone harnesses: `19/19 passed`;
- targeted 2007A tests: `5 passed`;
- skill-only copy/import/behavior: `PASS`;
- current route count: `10`.

`DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING` remains: the default interpreter lacks pytest. The existing frozen smoke/path placeholders are recorded and not repaired.

## Historical integrity

Frozen 2007A run-001 and `reference-benchmark/` have no working-tree differences. Run-001 `final_result_status` remains `VALID`; the reference benchmark remains `GENERALIZABLE_EVALUATION_GAP_FOUND`. Protected 2017F, 2005D, 2020A, 2011B, 2022C, 2023E, and 2024C trees are unchanged. Tree hashes are recorded in `integrity.json`.

## Final decision

All definition-of-done guards are satisfied. The demonstrated comparator errors fail closed, valid cross-domain evaluation semantics remain accepted, existing capabilities regress cleanly, and the capability is self-contained inside `skill/`.
