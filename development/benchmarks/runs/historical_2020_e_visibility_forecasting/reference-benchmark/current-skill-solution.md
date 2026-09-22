# Current Skill solution frozen before reference review

This summary uses only the committed 2020E run-001 and source-recovery evidence at main `71f4c11d7aeab8e6ca789d0f5d2b6138f47f7739`. No excellent-solution method has been read for this benchmark. This file is immutable after its SHA256 is recorded in `current-skill-solution.freeze.json`.

## Interpretation and original-source limits

Q1 is contemporaneous AMOS meteorology-to-MOR estimation; Q2 is same-time airport-video estimation aligned to AMOS; Q3 is highway image-only current visibility estimation and a 100-frame curve; Q4 is future highway trend and time until a specified MOR, with 150 m a problem example rather than a newly imported legal threshold. MOR and RVR remain distinct.

The corrected five-page DOC/PDF supplies the operative statement; the earlier four-page DOC omits atmospheric transparency's definition. Both ZIPs (AMOS and 100 highway BMPs) are available and verified in the frozen mirror. The airport video was not obtained. Source recovery reopened its remote listing but obtained neither the complete video nor the full official RAR. Its duration/resolution are provider declarations, not local media verification. AMOS/highway equivalence to the official package and additional official Q3/Q4 calibration remain UNVERIFIED. No official-package absence claim is made.

Q2 remains source-blocked. Available highway images lack an independently verified absolute-scale/paired-MOR mapping, so Q3/Q4 absolute MOR and 150 m dispersal time are not identifiable from the available inputs. No reference-only frame, distance, label or calibration may be added to this baseline.

## Q1-Q3 estimation actually retained

Q1 uses an other-event median baseline and contemporaneous log-MOR Ridge, with event-holdout checks. It is not future-forecast evidence and Ridge does not show stable whole-event generalization. Q2 has no fitted video estimator because the indispensable video is absent. Q3 retains a dimensionless, fixed-ROI relative scene-contrast proxy and its 100-frame curve. Illumination may confound the proxy, so it is never promoted to metres or a calibrated 150 m decision.

AMOS observations were aggregated within each minute using medians. Each of the two isolated 24-hour events becomes a complete 1,440-row minute grid; event boundaries are respected. `MOR_1A` is the target in metres, not RVR. Floor/cap behavior is disclosed: observed 0-10,000 m, 518 readings at/below 50 m and 225 at 10,000 m. Sensor limits are not treated as fully documented exact ordinary measurements.

## Q4 and the separate AMOS protocol diagnostic

Formal Q4's origin is the last available highway frame at issuance. Future frames, realized future weather and future MOR are unavailable at origin. The executed highway diagnostic uses DIRECT independent models at 1/3/6 frames (approximately 0.69/2.08/4.17 min) and 30 common rolling origins, frames 36,38,...,94. Persistence and fixed standardized Ridge use the same origin/target rows. Results concern the proxy only, from one episode with no independent-scene final test. The allowed full-sequence qualitative conclusion is `improving_contrast`; no absolute future MOR or 150 m time is emitted.

Separately, the labelled AMOS diagnostic checks general forecasting protocol. It does not use airport measurements to substitute for highway Q4. Training begins with AMOS20191216; AMOS20200313 supplies a later event-transfer evaluation period. Forty-three common origins spaced 30 minutes apart evaluate 5/15/30 min ahead. At each origin, expanding training labels end at or before the origin, and scaler/model fitting stays inside that origin. The fixed primary strategy is DIRECT, with separate horizon targets/models. Current-origin weather and causal MOR lags/rolling features are allowed; realized future weather, future targets, centered windows and global preprocessing are excluded.

## Frozen forecast results (no recomputation)

| AMOS horizon | Persistence MAE / RMSE (m) | Direct Ridge MAE / RMSE (m) |
|---|---|---|
| 5 min | 266.9 / 820.4 | 972.3 / 1535.7 |
| 15 min | 360.5 / 972.0 | 1103.7 / 1718.5 |
| 30 min | 410.5 / 997.6 | 1049.7 / 1706.8 |

Ridge loses to persistence at all three horizons; persistence remains preferred. Highway Ridge's relative-proxy advantage is mixed (small 1-frame MAE improvement, worse 3-frame errors, lower 6-frame errors) and does not establish physical visibility quality. No seasonal-naive pattern is defensible from the two isolated airport episodes.

Sequential nominal 80% prediction intervals use only earlier out-of-origin errors after ten prior errors exist for a method/horizon. AMOS coverage is 0.939-0.970 with 33 evaluated intervals per cell; persistence mean widths are 1,295-2,498 m and Ridge widths 3,958-4,724 m. Highway coverage is 0.90-1.00 with only 20 intervals per cell. These are empirically evaluated predictive bands, not coefficient-fit confidence intervals; overcoverage, width and small samples constrain operational claims.

AMOS targets at/below the 150 m example number 12/12/14 at the three horizons. Persistence MAE is 12.5/4.2/92.9 m versus Ridge 42.2/75.2/112.3 m. Floor/special values and small counts limit interpretation. Highway low-MOR evaluation is unavailable without labels. Distribution shift is recorded (event medians 5,000 versus 3,200 m, KS 0.375), along with cap-related large errors, bias, residual dependence and time-local nonstationarity.

## Frozen strengths, limitations and verdict

The run records origin, target time/frame, horizon, method, prediction, truth, training rows and maximum fitting-label time. It separates estimation and forecasting; enforces temporal availability and origin-safe preprocessing; excludes random-split future claims and realized future exogenous inputs; uses common origins, a naive baseline, per-horizon MAE/RMSE, empirical interval coverage, low-visibility checks, shift and failure analysis. Synthetic guards reject future exogenous/rolling fields, global scaling, random splits, observed recursive future targets and reversed time.

The frozen reviewer notes that prediction.md is terse about named multi-step strategies and common-origin/per-horizon presentation. That brevity did not cause a correctness failure here. The airport evaluation is isolated from model/hyperparameter selection, while the highway diagnostic has no independent final episode; overall `final_holdout_isolated: NO` is retained rather than overstating independence. Algorithm quality, source completeness, absolute-scale identifiability and protocol correctness are distinct.

`first_meaningful_failure: NONE_IN_FROZEN_SKILL`.
`failure_level: NONE`; `generalizable_gap_candidate: NONE`.
`run_001_status: BLIND_RUN_PARTIAL`.
`source_recovery_status: ORIGINAL_SOURCE_NOT_RECOVERED`.

Existing results record 321 effective pytest passes, 10 routes and Skill-only self-containment. `DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING` and four frozen smoke/path findings remain existing issues; this benchmark does not repair them. Earlier incidental source-search snippet exposure is disclosed in the frozen records; excellent papers were not opened before this benchmark.

## Frozen evidence used

- [Run report](../run-001/REPORT.md), [completion](../run-001/completion.json), [reviewer](../run-001/reviewer-report.md).
- [Prediction setting](../run-001/prediction-setting.md), [backtest](../run-001/backtest-protocol.md), [horizon metrics](../run-001/horizon-metrics.md), [interval validation](../run-001/interval-validation.md).
- [Source-recovery completion](../source-recovery/completion.json) and [report](../source-recovery/REPORT.md).
