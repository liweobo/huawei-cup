# 2023年中国研究生数学建模竞赛 E 题

## 出血性脑卒中临床智能诊疗建模

Source: `../raw/出血性脑卒中临床智能诊疗建模.docx` (ART-001) and
`../raw/附件2-相关概念.docx` (ART-002). The original documents are retained;
this file records题面 facts and the modeling interfaces without adding a
solution or external clinical claims.

## Data and information availability

The package contains 160 patients: training patients `sub001`–`sub100`,
test set 1 `sub101`–`sub130` with personal/clinical data and first imaging
only, and test set 2 `sub131`–`sub160` with personal/clinical data plus first
and follow-up imaging but no 90-day mRS label.

Table 1 contains patient ID, 90-day mRS where available, history, onset-related
features, first-imaging serial number, onset-to-first-imaging interval, blood
pressure, and seven treatment indicators. Table 2 contains first and follow-up
serial numbers with hematoma (`HM_volume`) and edema (`ED_volume`) volumes and
ten-region location ratios. Table 3 contains ED and Hemo shape and intensity
features keyed by serial number. Appendix 1 maps serial numbers to actual
imaging timestamps; the 14-digit serial number is not a clock time. Table 4 is
the answer template.

## Explicit questions

### Q1 Hematoma expansion

For `sub001`–`sub100`, determine whether expansion occurs within 48 hours of
onset using later-versus-first hematoma volume. Expansion is present when the
absolute increase is at least 6 mL or the relative increase is at least 33%.
For positive cases record the expansion time. Use onset-to-first-imaging time
from Table 1 plus the actual serial-number timestamp from Appendix 1. Then,
using only first-imaging information for prediction, estimate expansion
probabilities for all `sub001`–`sub160`.

### Q2 Perihematomal edema

Using the first 100 patients and repeated imaging times, fit an overall
`ED_volume` trajectory against onset-to-imaging time and compute full-cohort
residuals. Explore clinically interpretable 3–5 patient subgroups, fit subgroup
trajectories and residuals, analyze the association of seven treatments with
edema progression, and examine the joint relationship among hematoma volume,
edema volume and treatment.

### Q3 90-day mRS prognosis

Using only first information, predict 90-day mRS for all 160 patients. Using
all known clinical, treatment and follow-up imaging information, predict mRS
for `sub001`–`sub100` and `sub131`–`sub160`. Analyze associations with history,
treatment and imaging features and formulate clinical decision suggestions.
mRS is an ordered 0–6 outcome; any baseline must discuss the implications of
using multiclass or ordinal methods.

## Time and leakage boundaries

Q1 probability prediction and Q3 first-information prediction are BASELINE
tasks: no post-baseline follow-up measurements, derived changes, or outcome
labels may enter their features. Q3 follow-up prediction is a separate
FOLLOW_UP scenario. Q1 expansion labels, Q2 residuals, and Q3 mRS labels are
OUTCOME/derived targets and must never be prediction features.

## Evidence boundary

This extraction does not contain a best model, official score, or causal
treatment effect. Any numeric model result must come from a run-scoped code
execution and structured experiment record.
