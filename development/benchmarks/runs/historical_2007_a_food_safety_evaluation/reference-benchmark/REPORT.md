# 2007A Excellent-Solution Post-hoc Benchmark

## 1. Reference Set

Six requested files were discovered and fully reviewed: `1000401-A.pdf`, `10052A.pdf`, `1028601.pdf`, `9000212.pdf`, `9001601.pdf`, and `9005210.pdf`. `10052A.pdf` and `9005210.pdf` are different PDF binaries but exact extracted-text duplicates identifying the same team `9005210`; the benchmark therefore contains six file records and five unique works.

No reliable official evidence for a specific prize tier was present. All six records use `award_level: UNKNOWN`, `award_verified: false`.

## 2. Source Reliability

All files came only from the user-designated GitHub directory. Blob IDs, bytes, SHA256, URLs, metadata, and page counts are retained in `source-ledger.md`. Text layers were extracted across all 164 file-pages. Thirty-nine selected pages covering identities/openings, risk formulas, quantile methods, threshold tables, numerical conclusions, limitations, and final sections were visually checked against Poppler-rendered pages. Extraction quality is `GOOD_WITH_EQUATION_LAYOUT_CAVEATS`; displayed mathematics was not trusted from plain text alone.

## 3. Frozen Blind Run

Before opening any reference PDF, the benchmark created `current-skill-solution.md` solely from frozen run-001 and fixed SHA256 `8c82f180a7cdc3619e9bc349adfd841b3311c899a73fe273ec7c4b5dbd428d6e`. Frozen run-001 tree: `75eadfc90829d2db17b563e51dad2e6b7f458ba6`. Its status remains `VALID`; none of its files, code, outputs, or claims was changed.

## 4. Problem Target

The references unanimously interpret the formal quantitative target as an absolute dietary-exposure distribution and its `99.999%` right quantile, followed by comparison with an authority/toxicological threshold. The problem is primarily statistical risk modeling. It does not require a multi-criteria alternatives ranking.

## 5. Risk Definition

Four unique works use exposure quantile/threshold semantics. `REF-01` mixes empirical exceedance probability, extreme quantile, adverse-event language, and a Pareto-style index. No work uses a relative composite score as the principal risk object.

## 6. Absolute vs Relative Outputs

Every primary reference output is intended to be absolute and physically dimensioned. Relative ranking scores are absent. Fuzzy similarity in `REF-02/06` is a data-matching coefficient, not a probability or absolute safety measure. The frozen run's optional triage is correctly labelled relative and secondary.

## 7. Quantile / Probability Semantics

A CDF value such as `F(q)=0.99999` has probability content; the quantile `q` is a physical exposure value, not “99.999% safe” or a harm probability. `REF-01` violates this boundary when it turns a dietary-intake quantile comparison into a lead-poisoning probability claim. This is a demonstrated semantic failure, not a hypothetical score example.

## 8. Regulatory Compliance Semantics

Compliance requires the model output and comparator to match in physical object, unit, population, geography, time, contaminant/food scope, and standard version. `REF-01` compares dietary intake in `µg/person-day` with blood concentration in `µg/L`. `REF-05` compares a daily intake quantile with a food-content limit and then generalizes nationally. Both formal safety conclusions are unsupported.

## 9. Ranking / Classification

No reference delivers formal ranking as a problem requirement. `REF-01` adds high-exceedance-probability regional screening, which is secondary triage. All works use a binary safe/warning conclusion from a threshold comparison; none establishes arbitrary high/medium/low risk classes.

## 10. Threshold Provenance

`REF-04` reports a PTWI and a dimensionally aligned body-weight/time conversion but lacks edition/effective-date provenance. `REF-05` names `GB 2762-2005` and a date but applies the limit to the wrong output. The other works invoke national/authority standards without sufficient version, value, unit, or scope. A named official source is not enough; applicability must be bound to the output.

## 11. Hard vs Soft Criteria

All unique works intend a hard threshold rule. None uses a fully compensatory MCDM total that lets ordinary benefits offset a safety violation. The current Skill already warns that hard constraints must not be reduced to a compensatory total; this is `ALREADY_PRESENT`, not a new gap.

## 12. Compensation

No reference shows safety compensation across population, coverage, economics, and contamination. Fuzzy matching and regional/population weights operate upstream in data integration. The post-hoc failure is an invalid output/comparator/claim binding, not compensation.

## 13. Weighting

Weights are regression, sampling, population-mixture, importance-sampling, neural-network, or fuzzy-matching weights. No AHP, entropy-importance, TOPSIS, or criterion-weighted safety score occurs. `REF-02/06`'s fuzzy scale is subjective and uncalibrated but is not presented as a probability.

## 14. Normalization

The works normalize densities, mixture weights, or matching weights; none uses current-alternative min-max/vector normalization for a formal risk score. Candidate-set dependence is therefore not the reference failure. The frozen run's ranking normalization checks remain useful only for its optional triage.

## 15. Tail Modeling

All five unique works explicitly attempt the `99.999%` tail. Methods include EVT/Hill/Pareto, quadrature of a product distribution, importance/ordinary Monte Carlo, histogram quantile search, and polynomial CDF root solving. These are G2 problem-specific techniques. `REF-05`'s multiple roots and unverified CDF are especially weak.

## 16. Uncertainty

No unique work reports a confidence/credible interval or validated uncertainty upper bound for `Q_0.99999`. Bootstrap in two works reconstructs/enlarges data rather than quantifying final-tail uncertainty. This shared weakness supports the frozen run's cautious `UNCERTAIN` class but does not itself prove the output-semantics gap.

## 17. Population / Regional Aggregation

References use stratification, demographic proportions, clustering, density mixtures, or assumed representativeness. These are sampling/transport issues. `REF-05` overgeneralizes one region-season-food result nationally. The frozen run is stronger because it explicitly limits transport claims and records crosswalk/dependence assumptions.

## 18. Numerical Comparability

No reported q values share the same data, population, food, contaminant, standard, units, censoring, or time scope. `REF-01`, `REF-04`, and `REF-05` report respectively `41.9259 µg`, `0.027 mg`, and `0.989689 µg`, but all cross-paper numeric comparisons are `NOT_DIRECTLY_COMPARABLE`. Frozen run numbers are synthetic and likewise incomparable.

## 19. Reference Consensus

Consensus is strong for absolute exposure distribution (`6/6` files, `5/5` unique works), the exact extreme quantile (`6/6`, `5/5`), and threshold-based decision (`6/6`, `5/5`). Formal relative score and formal ranking appear in `0/6`. Quantified q uncertainty appears in `0/6`. Output/comparator semantic failure appears in `2/6` files and `2/5` unique works.

## 20. Blind Run Strengths

Frozen run-001 explicitly fixes the evaluation target; separates absolute quantile, probability, compliance, relative score, rank, and class; preserves threshold provenance; gates before optional triage; invents no real standard; maintains a synthetic-only claim boundary; uses an equal-weight baseline without fake expert/AHP weights; tests weights, normalization, indicator deletion, rank reversal, dominance, monotonicity and units; retains near ties; and discloses tail uncertainty.

## 21. Blind Run Weaknesses

Real survey/monitoring data and an applicable historical standard are absent. Extreme-tail estimates remain unstable. Dependence, taxonomy crosswalk, and regional transport are assumptions. Ranking stability is `PARTIAL`. The result is operationally synthetic-only. These are G2/G5 limitations, not all Skill defects.

## 22. Existing Skill Coverage

The frozen Skill already covers indicator direction, units, weight semantics, hard constraints, equal-weight/business baselines, weight/normalization sensitivity, rank stability/reversal, redundancy, missingness, extremes, and evidence provenance. General rules also flag unit errors and unsupported evidence. It does not require a pre-weighting evaluation object/decision/output-semantics contract, absolute-versus-relative tag, general score-to-probability prohibition, regulatory-compliance binding, threshold applicability record, or evaluation-specific allowed claim.

## 23. Reference Weaknesses

References show incompatible units/scope, unversioned standards, a quantile promoted to poisoning probability, ambiguous polynomial quantiles, no rare-tail uncertainty, point-only safety declarations, and unsupported geographic generalization. The duplicate file also shows why counts require content identity checks. References are evidence of failure modes, not truth.

## 24. Generalizable Gaps

Only one G1 is confirmed: `EVALUATION_TARGET_AND_OUTPUT_SEMANTICS_CONTRACT`. The hard-versus-soft rule is not counted again. Tail estimation, censoring, sampling, crosswalks, dependence, and transport are classified G2/G5. Reference mathematical mistakes are G4 unless they expose the confirmed reusable guard.

## 25. Problem-Specific Techniques

EVT, censored distribution estimation, importance sampling, Monte Carlo rare tails, food taxonomy reconciliation, unpaired-sample dependence, and regional transport remain problem/risk-family methods. The proposed Skill repair adds none of them.

## 26. Top-1 Candidate

Before weighting, normalization, thresholding, ranking, or classification, require:

`evaluation_object`, `decision_question`, `output_semantics`, `absolute_or_relative`, `threshold_and_provenance`, link to the existing `hard_gate`, and `allowed_claim`.

Forbid relative score/rank/membership from becoming probability or compliance, and require comparator/output scope and unit agreement.

## 27. Gap Severity

`P0` is retained as **missing-guard severity**, because `REF-01` and `REF-05` demonstrate that the absent guard can authorize an invalid formal safety conclusion. It is not a statement that frozen run-001 is invalid; run-001 remains `VALID`.

## 28. Current Skill Level

| dimension | level | reason |
|---|---|---|
| `EVALUATION_TARGET_DEFINITION` | `WEAK` | general input/output framing exists, but no required evaluation target contract |
| `OUTPUT_SEMANTICS` | `WEAK` | no probability/quantile/compliance/relative score/rank/class separation |
| `INDICATOR_PROVENANCE` | `ADEQUATE` | general source/evidence rules exist; evaluation family lacks a mandatory indicator ledger |
| `NORMALIZATION_DISCIPLINE` | `STRONG` | direction, scaling, alternative effects and sensitivity covered |
| `WEIGHT_DISCIPLINE` | `STRONG` | source, semantics, compensation and sensitivity covered |
| `HARD_SOFT_SEPARATION` | `STRONG` | explicit noncompensation guard exists |
| `RANKING_STABILITY` | `STRONG` | sensitivity, new-alternative effect and rank changes covered |
| `CLAIM_SEMANTICS` | `WEAK` | strong scoped gates exist elsewhere, but not for evaluation outputs |
| `SOLUTION_QUALITY` | `STRONG` | frozen run is careful and valid under user/run-local guards |
| `OVERALL` | `NEEDS_EVALUATION_IMPROVEMENT` | one lightweight but conclusion-critical semantic guard is missing |

## 29. Final Decision

`GENERALIZABLE_EVALUATION_GAP_FOUND`

- `gap_name`: `EVALUATION_TARGET_AND_OUTPUT_SEMANTICS_CONTRACT`
- `failure_level`: `P0` missing-guard severity
- `blind_run_evidence`: run-local contract prevented probability/compliance/ranking confusion and preserved hard gating
- `reference_evidence`: two independent works make output/comparator semantic errors that invalidate safety conclusions
- `existing_skill_absence`: evaluation guidance lacks the required fields and prohibitions
- `why_generalizable`: every evaluation domain translates mathematical outputs into decisions and claims
- `why_not_2007a_specific`: no food, contaminant, censoring, or tail algorithm is part of the repair
- `demonstrated_failure_mode`: quantile/physical-output mismatch -> unsupported probability or compliance claim
- `minimal_skill_scope`: seven declarative fields, two semantic prohibitions, and a link to the existing hard-constraint rule
- `future_regression_plan`: safety, supplier, city, education, credit/risk, and mismatched-quantile comparator cases

Recommended next action: human review of this frozen post-hoc decision. If accepted, implement the minimal contract in a separate non-blind change; do not modify run-001 and do not start problem nine.

## 30. Validation

The full repository suite passes (`305 passed`). All six references passed checksum review, all required artifacts exist, and the pre-reference solution hash remains frozen. `DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING` and four frozen smoke/path placeholders remain recorded rather than repaired. See `validation.md`.

## 31. Historical Integrity

`skill/`, 2007A run-001, and the protected 2017F, 2005D, 2020A, 2011B, 2022C, 2023E, and 2024C trees have no working-tree differences. Their tree hashes are recorded in `integrity.json`. Only this `reference-benchmark/` directory is in submission scope.
