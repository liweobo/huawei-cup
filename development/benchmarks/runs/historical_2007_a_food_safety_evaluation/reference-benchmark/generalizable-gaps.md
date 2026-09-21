# Generalizable Gap Adjudication

## Top-1 decision

`top_generalizable_gap: EVALUATION_TARGET_AND_OUTPUT_SEMANTICS_CONTRACT`

`classification: G1_GENERALIZABLE_SKILL_GAP`

`failure_level: P0_MISSING_GUARD_SEVERITY`

`final_decision: GENERALIZABLE_EVALUATION_GAP_FOUND`

The P0 label describes the severity of conclusions that the missing guard can permit. It does **not** invalidate frozen run-001, whose `final_result_status` remains `VALID`.

## G1 gate

| requirement | evidence | result |
|---|---|---|
| 1. absent from current Skill | evaluation guidance covers direction, units, weights, compensation, sensitivity and rank stability, but has no mandatory evaluation-object/output-semantics/probability/compliance contract | PASS |
| 2. actually needed by 2007A | formal output is a physical `Q_0.99999` and threshold decision, while ranking is not required | PASS |
| 3. blind run correctness came from run-local/user guard | `evaluation-target.md` was created under the stress prompt; no corresponding frozen-Skill contract exists | PASS |
| 4. real failure mode demonstrated | `REF-01` converts a dietary-intake quantile into a poisoning-probability conclusion using a blood concentration comparator; `REF-05` compares daily intake with a food-content limit and declares national safety | PASS |
| 5. not food-specific | every evaluation must bind object, decision, output type, comparator and allowed claim | PASS |
| 6. cross-domain portability | applies to supplier scores vs failure probabilities, city ranks vs absolute quality, ecological indices vs compliance, education scores vs classes, credit scores vs default probabilities | PASS |
| 7. affects formal correctness | the demonstrated mismatches reverse/authorize a “safe” compliance conclusion unsupported by the model | PASS |
| 8. lightweight repair | seven declarative fields plus two prohibitions; no new algorithm | PASS |
| 9. synthetically testable | threshold, supplier, city, education and credit/risk semantic cases are deterministic | PASS |
| 10. no platform required | a Markdown/YAML contract and reviewer rule suffice | PASS |

## Demonstrated, not merely theoretical

The evidence is stronger than a hypothetical “someone might call 0.82 a probability.” Two independent reference works produce formal safety conclusions from semantically incompatible output/threshold pairs; one also promotes the result to a poisoning-probability claim. These errors survive substantial mathematical machinery because the mathematical output type, comparator, and allowed claim were never frozen together.

General evidence provenance and unit rules in the current Skill could catch parts of these defects during review, especially the visible unit mismatch. They do not require the semantic contract before model/normalization/threshold selection, do not distinguish quantile from probability/compliance, and do not prevent scope promotion. The gap is therefore additive and non-duplicative.

## Minimal Skill scope

Before weighting, normalization, thresholding, ranking, or classification, record:

```yaml
evaluation_object: ""
decision_question: ""
output_semantics: "PROBABILITY | QUANTILE | PHYSICAL_ESTIMATE | COMPLIANCE | RELATIVE_SCORE | RANK | CLASS"
absolute_or_relative: "ABSOLUTE | RELATIVE"
threshold:
  value: null
  unit: ""
  provenance: "PROBLEM_GIVEN | OFFICIAL_STANDARD | EXTERNAL_REFERENCE | DERIVED | ASSUMED"
  scope_and_version: ""
hard_gate: "NONE | LINK_TO_EXISTING_HARD_CONSTRAINT_RULE"
allowed_claim: ""
```

Rules:

1. A relative score/rank/fuzzy membership/TOPSIS closeness cannot be reported as probability or regulatory compliance.
2. A probability, quantile, and physical estimate are distinct outputs; one cannot inherit another's semantics.
3. Compliance requires comparator/output agreement in object, unit, population, geography, time, contaminant/category, and standard scope/version.
4. Use the existing hard-constraint rule for the gate; do not duplicate a new compensation framework.

## Future regression plan (not executed here)

- A. Safety threshold: improve ordinary indicators while violating the hard threshold; compliance must remain failed.
- B. Supplier evaluation: a relative supplier rank must not become a component-failure probability.
- C. City ranking: TOPSIS closeness must remain current-set relative and cannot become absolute city quality.
- D. Education: a high/medium/low class threshold without provenance must be rejected or labelled assumed.
- E. Credit/risk: a calibrated default probability and a composite credit score must remain distinct outputs.
- F. Quantile comparator: dietary-intake quantile versus blood concentration or food concentration must fail the scope/unit gate.

## Non-G1 findings

| finding | class | reason not top gap |
|---|---|---|
| EVT/importance sampling/rare-tail estimation | G2 `2007A_SPECIFIC_METHOD` | statistical risk technique, not generic evaluation semantics |
| censoring, food taxonomy, regional transport, dependence | G2/G5 | problem/data-estimation layer |
| missing real survey and standard | G5 `DATA_ESTIMATION_LIMITATION` | cannot be fixed by Skill wording |
| reference point-only tail certainty | G4 `REFERENCE_WEAKNESS` | reference quality issue; uncertainty is already a general validation concern |
| wrong units in references | G4 plus existing Skill coverage | current Skill already treats unit errors as P0; the new contribution is object/output/claim binding |
| hard-vs-soft compensation | existing coverage | evaluation.md already contains the rule |

No second generalizable gap is confirmed.
