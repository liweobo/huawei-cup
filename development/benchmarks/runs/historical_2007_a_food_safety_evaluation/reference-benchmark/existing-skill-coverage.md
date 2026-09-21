# Existing Skill Coverage

Frozen Skill tree: `2b29e8ffa7c15d33bf81e675e8f1dcb240c226a6`.

Files reviewed include `skill/SKILL.md`, `rules/evidence.md`, `rules/modeling.md`, `rules/experiment.md`, `references/problem-taxonomy.md`, `references/model-selection.md`, `references/models/evaluation.md`, applicable workflows, reviewer rules, and probability/claim helpers. This is a coverage audit only; no Skill file was modified.

## Already present

| capability | evidence in frozen Skill | assessment |
|---|---|---|
| understand before model choice | Iron Rule 1 and model-selection decision frame require problem structure, inputs, outputs, constraints, assumptions, baseline, validation | `ALREADY_PRESENT` |
| evidence/source provenance | Evidence Rules require traceable sources, run IDs, hashes, active evidence, and forbid fabricated claims | `ALREADY_PRESENT` |
| units and parameter/boundary source | Modeling Rule 6 requires source/estimation for parameters, boundaries, and units; Reviewer treats unit error as P0 | `ALREADY_PRESENT` |
| indicator direction and units | evaluation family Fit requires direction, unit, weight semantics, and compensation interpretation | `ALREADY_PRESENT` |
| weight semantics | evaluation family and validation require weight provenance/sensitivity; entropy dispersion is not automatically importance | `ALREADY_PRESENT` |
| hard constraint awareness | evaluation family explicitly says hard constraints must not be only a compensatory total score | `ALREADY_PRESENT` |
| baseline | equal-weight or business-rule baseline is required | `ALREADY_PRESENT` |
| normalization and weight sensitivity | explicit requirement in evaluation family | `ALREADY_PRESENT` |
| ranking stability and rank reversal | evaluation family requires stability, effect of new alternatives, and ranking changes | `ALREADY_PRESENT` |
| redundancy, missingness, extremes, zero handling | evaluation family Data/Validation section | `ALREADY_PRESENT` |
| probability quality for classifiers | classification metrics distinguish true probabilities from ranking scores and restrict Brier score to probability outputs | `ALREADY_PRESENT_BUT_CLASSIFICATION_SCOPED` |
| allowed claims for mechanism models | mechanism closure has explicit allowed-claim levels | `ALREADY_PRESENT_BUT_MODEL_FAMILY_SCOPED` |

These capabilities must not be relabeled as a new post-hoc gap. In particular, hard-gate-before-compensation is already covered and should be referenced, not reimplemented.

## Missing or not operationally connected

| required field/guard | frozen Skill status | consequence in 2007A |
|---|---|---|
| `evaluation_object` | no mandatory evaluation-family contract field | a paper can drift from dietary intake to blood concentration or food concentration without an explicit object mismatch gate |
| `decision_question` | general input/output understanding exists, but no required decision question before weighting/normalization | a ranking or “safe” statement can be produced without proving that it answers the regulatory decision |
| `output_semantics` / output type | no enumerated distinction among probability, quantile, physical estimate, compliance, relative score, rank, and class | a quantile/score may be promoted to probability/compliance |
| `absolute_or_relative` | absent from evaluation guidance | candidate-dependent scores are not explicitly barred from absolute interpretation |
| probability semantics for general evaluation outputs | classification helpers distinguish probability, but the evaluation family has no equivalent guard | `REF-01`-type quantile-to-poisoning-probability promotion is not directly trapped |
| compliance semantics | competition-rule compliance exists, but model-output regulatory compliance semantics do not | `REF-05`-type output/standard mismatch can reach a “safe” conclusion unless unit review catches it incidentally |
| threshold provenance plus applicability | units/boundary sources are required generally, but no compact threshold record binds value, unit, scope, version/date, and output | a named official standard can still be applied to the wrong mathematical object |
| `allowed_claim` for evaluation outputs | mechanism/association routes have scoped claim gates; evaluation does not | synthetic/relative results can be overgeneralized |
| ordering of semantic contract before weighting/normalization | absent | method selection may start before the output meaning is frozen |

## Absence verification

A repository-wide search found no general evaluation requirement for `absolute vs relative`, regulatory-compliance semantics, score-to-probability prohibition, an evaluation-object field, or an output-semantics contract. The few occurrences of “absolute/relative” belong to spectral quantities or sensitivity changes; “compliance” belongs to competition submission status, not regulatory model output.

## Coverage judgment

The Skill is strong on how to construct and stress-test a multi-criteria ranking after the task is correctly framed. It is weak on forcing that framing into a machine/reviewer-visible contract before the first score, normalization, threshold, or class is interpreted. General evidence and unit rules can sometimes catch downstream symptoms, but they do not replace the missing semantic gate.
