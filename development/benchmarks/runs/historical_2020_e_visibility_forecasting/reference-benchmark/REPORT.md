# 2020E post-hoc excellent-solution benchmark

## Completion and decision

`2020E_REFERENCE_BENCHMARK_COMPLETE`

Six papers were discovered and all six were reviewed across all 326 PDF pages, including appendices; 69 important pages were visually checked. No award level was independently verified, so all six remain `UNKNOWN`.

**Final decision: `NO_MAJOR_GENERALIZABLE_GAP`.**
**Top generalizable gap: `NONE`.**
**Failure level: `NONE`.**

The reference set does not show that the current Skill lacks a general forecasting capability that caused a frozen-run correctness failure. It shows different image algorithms, greater source access, many unverified physical-scale assumptions, and weaker future-validation practices. The frozen run remains partial for source and identifiability reasons.

## Frozen baseline preserved

The pre-reference summary [current-skill-solution.md](current-skill-solution.md) remains byte-identical to its freeze record:

- base commit: `71f4c11d7aeab8e6ca789d0f5d2b6138f47f7739`
- bytes: 7,666
- SHA256: `7ecd6ced497b53473f7b7122975574bf933d31f35bb5f0a8011da3f2534a05d8`
- `reference_methods_read_before_freeze: false`

Its conclusions remain valid: Q2 lacks locally verified video; highway Q3 retains a relative proxy; absolute MOR and a 150m time are unidentifiable; Ridge loses to persistence at 5/15/30 minutes; `first_meaningful_failure: NONE_IN_FROZEN_SKILL`.

## Core results

### Estimation versus forecasting

All six Q1 methods fit same-time meteorology to RVR/MOR. None supplies future-target validation. Q2 likewise performs same-time video estimation or classification. The frozen solution correctly keeps those tasks separate from Q4 future forecasting.

### Q4 forecast discipline

All six papers fit or train on the complete 100-point Q3-derived series and extrapolate beyond it. This is `FULL_SEQUENCE_EXTRAPOLATION`; using all 100 observations at a last-frame origin is not automatically leakage. The common weakness is that no paper reissues its final algorithm at multiple earlier origins and scores future observations. None includes a persistence baseline, future per-horizon error table, calibrated prediction interval or coverage test.

Five papers claim a 150m time; R6 substitutes a 200m clearing rule. Every crossing combines an assumed/unverified metric image scale with an unvalidated long extrapolation. Their numbers are therefore `UNVERIFIED` and `NOT_DIRECTLY_COMPARABLE` with the frozen proxy or AMOS diagnostic.

### Physical output identifiability

All six references report metres. Every chain depends on an external/reference-only/author-assumed scene scale. R1–R5 are `PARTIALLY_SUPPORTED` only as conditional physical models; none validates highway estimates against paired MOR. R6 is `UNSUPPORTED` because the appendix hard-codes a 30m distance while the prose promises camera calibration that is never instantiated.

These repeated assumptions form `REFERENCE_CONSENSUS`; they do not recover an official attachment fact and cannot be inserted into run-001.

### Source provenance

All six use an airport video, but that proves only author access to a video or equivalent source. It does not prove byte equivalence to the current remote listing. Frame-label alignment is incomplete in every paper under the full local/UTC/tolerance contract. The corrected five-page problem statement remains the frozen operative version; references do not change its provenance.

## Current Skill level

| Dimension | Level | Evidence |
|---|---|---|
| ESTIMATION_FORECAST_SEPARATION | STRONG | tasks and evidence types are explicitly separated |
| FORECAST_TARGET_DEFINITION | STRONG | origin, target time/frame and horizon are recorded |
| TEMPORAL_AVAILABILITY | STRONG | contract, causal aggregation and synthetic guards |
| FORECAST_ORIGIN_DISCIPLINE | STRONG | rolling issuance and fitting cutoff records |
| BACKTEST_DISCIPLINE | STRONG | common rolling origins and persistence baseline |
| MULTISTEP_DISCIPLINE | ADEQUATE | correct DIRECT execution; named-strategy documentation is terse |
| EXOGENOUS_FEATURE_DISCIPLINE | STRONG | no realized future weather; availability checked |
| FORECAST_UNCERTAINTY | STRONG | predictive intervals and empirical coverage, limitations disclosed |
| PHYSICAL_OUTPUT_IDENTIFIABILITY | STRONG | proxy/physical boundary enforced; unsupported threshold claim withheld |
| SOLUTION_QUALITY | ADEQUATE | disciplined partial solution; source limits and weak Ridge performance remain |
| OVERALL | STRONG | no major general forecasting gap found |

## Generalizable-gap decision

Forecast-origin, temporal-availability, naive-baseline, rolling-origin, per-horizon, interval-coverage and physical-output boundaries are already present. Named multi-step taxonomy and common-origin presentation are terse, but the frozen run used them correctly. The only large outcome gaps are unavailable video, unverified highway scale and model performance; they are G5/G6 rather than G1.

The full 12-condition audit is in [generalizable-gaps.md](generalizable-gaps.md). No Skill modification or regression plan follows from this benchmark.

## Historical status and existing findings

- `run_001_status_remains: BLIND_RUN_PARTIAL`
- `source_recovery_status_remains: ORIGINAL_SOURCE_NOT_RECOVERED`
- `DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING` remains recorded: the default Python lacks pytest; the historical effective result was 321 passed.
- Four frozen structural smoke findings remain unchanged:
  - `historical_2022_c_buffer_scheduling/run-002/REPORT.md`
  - `historical_2017_f_underground_logistics_network/run-001/REPORT.md`
  - `historical_2017_f_underground_logistics_network/run-001/validation.md`
  - `historical_2007_a_food_safety_evaluation/run-001/validation-results/README.md`

No modelling suite was rerun: this stage reviews references and validates file integrity rather than changing executable behavior.

## Artifact map

- Source and coverage: [source-ledger.md](source-ledger.md), [review-coverage.md](review-coverage.md), [paper-reviews](paper-reviews/)
- Core comparisons: [problem interpretation](problem-interpretation-comparison.md), [Q1](q1-estimation-comparison.md), [Q2](q2-video-comparison.md), [Q3](q3-absolute-mor-comparison.md), [Q4](q4-forecasting-comparison.md)
- Forecast protocol: [origin](forecast-origin-comparison.md), [validation](validation-protocol-comparison.md), [future features](future-feature-comparison.md), [multistep](multistep-comparison.md), [uncertainty](uncertainty-comparison.md)
- Claim controls: [identifiability](identifiability-comparison.md), [numerical comparability](numerical-comparability.md), [consensus](reference-consensus.md), [reference weaknesses](reference-weaknesses.md)
- Skill decision: [existing coverage](existing-skill-coverage.md), [generalizable gaps](generalizable-gaps.md), [completion](completion.json)

## Recommended next action

`HUMAN_REVIEW_REFERENCE_BENCHMARK`. Preserve the partial historical result, do not modify the Skill, do not reconstruct sources from papers, and do not begin the tenth problem.
