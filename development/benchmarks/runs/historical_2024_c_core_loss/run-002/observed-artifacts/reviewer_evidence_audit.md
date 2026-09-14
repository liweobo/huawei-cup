# Reviewer Evidence Audit

Overall Status: NEEDS EVIDENCE

Scope: This audit covers the currently available paper-facing numbers and planned claims. No final paper manuscript is present in the workspace, so sentence-level review is not possible. The audit therefore checks the Q1/Q2 outputs, the Q4 alignment check, and the evidence ledger.

## P0 Critical

| ID | Evidence location | Issue | Impact | Minimal fix | Recheck |
|---|---|---|---|---|---|
| P0-1 | `evidence_ledger.json`; `q4_alignment_check.json` | No Q4 loss-prediction run exists. Any numeric loss prediction for the 400 Attachment 3 samples would be unsupported. | Writing such values as measured or predicted would be fabrication and fails the required deliverable. | Run a named Q4 model against Attachment 1, save predictions, metrics, script and hashes; only then write column C. | `paper_write_status.can_write_q4_loss_predictions` must become true and every row must map to sample_id 1..400. |
| P0-2 | `outputs/q1_model_comparison/attachment2_model_predictions.csv` | This file contains Q1 classification labels for Attachment 2, not Q4 losses for Attachment 3. | Copying it to Attachment 4 column C would mix target, dataset and row count. | Keep it in the Q1 evidence folder; create a separate Q4 prediction artifact. | File must have 400 rows and a loss-valued target column before writing Attachment 4 C2:C401. |

## P1 Serious

| ID | Evidence location | Issue | Impact | Minimal fix | Recheck |
|---|---|---|---|---|---|
| P1-1 | `outputs/q1_baseline/metrics.json`; `outputs/q1_model_comparison/comparison.json` | Q1 accuracy=1.0 is an internal validation result, not a measured accuracy on Attachment 2. Attachment 2 has no labels. | Calling Attachment 2 predictions “100% accurate” or “verified by experiment” is false. | Use “holdout/CV accuracy on labeled Attachment 1” and “predictions on unlabeled Attachment 2”; do not report test accuracy. | Check all paper sentences and captions for `附件二准确率`, `实测准确率`, or equivalent. |
| P1-2 | `outputs/q1_model_comparison/comparison.json` | 100% results rely on engineered shape features and may reflect an unusually separable synthetic/controlled dataset. | Overclaiming real-world robustness or universal applicability is not supported. | State the validation scope: Attachment 1 distribution, waveform-only features, fixed protocol; present material-leave-out as a robustness check, not proof of field performance. | Require scope qualifier in abstract/conclusion. |
| P1-3 | `outputs/q2_validation/q2_validation.json` | Row-order 80/20 is explicitly only a diagnostic; no timestamp exists. | Calling it a “time split” or using it as temporal generalization evidence is incorrect. | Write “row-order diagnostic split; no time variable provided”; do not infer chronology. | Search manuscript for “时间切分/时序验证/未来预测” and qualify or remove. |
| P1-4 | `q4_alignment_check.json` and `evidence_ledger.json` | Attachment 3/4 ID columns use formula chains; formula strings are not sample IDs until evaluated. | Naive code can shift rows or compare `=A2+1` as text. | Validate cached IDs 1..400 and write by explicit sample_id lookup. | Re-run alignment check after creating Q4 predictions. |

## P2 Important

| ID | Evidence location | Issue | Fix |
|---|---|---|---|
| P2-1 | `attachment1_audit.json` | 163 training frequencies are 49990 or 501180 Hz, slightly outside the stated 50000–500000 range. | State that values were retained as recorded; do not silently clip or call the range exact. |
| P2-2 | `attachment1_audit.json`; `locate_duplicates.py` output | One exact duplicate full row exists in Material 3 (rows 432 and 908). | Report it; check whether it crosses train/validation partitions and include a sensitivity note. |
| P2-3 | `q2_validate_protocol.py` | Q2 uses (B_m=(B_{max}-B_{min})/2), normalized (f_0=100,kHz), (B_0=0.1T), and θ=(T−25)/65. These are modeling choices, not all explicit题面 facts. | Label them as definitions/assumptions and give their rationale. |
| P2-4 | `q2_validation.json` | Bootstrap intervals and perturbation results are actual outputs, but only for Material 1 + sine-wave data. | Attach the population scope to every reported number. |
| P2-5 | `q1_model_comparison/comparison.json` | “Confidence=1.0” in the CSV is tree/SVM model probability/decision output, not empirical correctness probability. | Call it model confidence/score; do not interpret as true probability of correctness without calibration. |

## P3 Polish

| ID | Evidence location | Issue | Fix |
|---|---|---|---|
| P3-1 | All paper-facing tables | Labels can be garbled if encoding is not UTF-8; ensure Chinese labels render correctly in the manuscript. | Keep source files UTF-8 and verify rendered tables. |
| P3-2 | Q1 summaries | Distinguish “真实标签” (Attachment 1) from “预测类别” (Attachment 2). | Use separate column names and captions. |

## Required Evidence / Questions

- Is there a final paper manuscript to review? Currently no `.docx`, `.tex` or final report file is present.
- Has Q4 loss prediction actually been run? Currently no.
- Are any Q3 or Q5 numerical effects, optimal combinations, or prediction tables already drafted? If yes, each needs a run artifact and evidence row before use.
- Are all equations using (B_m), temperature normalization and frequency normalization labeled as assumptions/definitions rather than quoted as题面给定 constraints?

## Safe wording

- Q1: “On labeled Attachment 1 samples, the fixed holdout and 5-fold protocols produced 1.0000 accuracy and Macro-F1. Attachment 2 is unlabeled; the reported class counts are model predictions, not measured labels.”
- Q2: “Under the Material 1 + sine-wave subset and the stated (B_m)/log-scale definitions, the temperature-corrected model reduced validation error relative to the baseline.”
- Q4 before a run: “NOT RUN; no loss predictions are available yet.”
- Q5 before a run: “NOT RUN; no numerical optimum is available yet.”

## Fix Order

Must Fix:

1. Do not write any Q4 loss number until a Q4 run artifact exists.
2. Do not describe Q1 Attachment 2 predictions as measured values or measured accuracy.
3. Add scope qualifiers and assumption labels to Q1/Q2 claims.

Should Fix:

1. Add duplicate/frequency-boundary notes to the data section.
2. Re-run alignment after Q4 output generation.

May Defer:

1. Typography and table polish after the evidence boundary is correct.
