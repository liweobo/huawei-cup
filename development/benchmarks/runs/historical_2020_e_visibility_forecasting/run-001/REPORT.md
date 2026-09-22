# 2020E Ninth-Problem Blind Run

## 1. Source Provenance

All six designated files were retained byte-for-byte. Supplied Git blob SHA-1 values and independently computed SHA-256 values pass. Both legacy DOCs were opened read-only and visually verified after rendering; the five-page PDF was text-extracted and visually checked page by page, including image equations.

No excellent-solution PDF or directory was opened. An unintended search-result snippet from a 2020E-specific blog appeared during source-link troubleshooting; it repeated task text and a generic formula/fitting phrase. No solution page, method detail, code, or result was consumed. This is `UNINTENDED_NON_SUBSTANTIVE_SEARCH_SNIPPET_EXPOSURE` and is disclosed as a conservative limitation.

## 2. Source Variant Reconciliation

Decision: `CORRECTED_VERSION`. The four-page DOC omits the atmospheric-transparency definition and renumbers later definitions. The five-page DOC and PDF match each other and carry the complete definition list; their four subproblems are semantically the same as the earlier DOC. The corrected pair supplies the operative facts.

## 3. Attachment Completeness

AMOS data and 100 highway BMP frames are complete and verified. The Baidu-linked airport video could not be obtained: `SOURCE_ATTACHMENT_UNAVAILABLE`. Essential-attachment status is `PARTIAL`; Q2 alone is directly blocked by that unavailable stream.

## 4. Problem Facts

Q1 asks for the contemporaneous meteorology–visibility relationship using AMOS. Q2 asks for airport-video same-time estimation against AMOS. Q3 asks for video-only highway estimation and a 100-frame curve. Q4 asks for future trend and dispersal time at a specified MOR such as 150 m. MOR and RVR are distinct and measured in metres.

## 5. Estimation vs Forecasting

Q1–Q3 are current/same-time estimation tasks. Q4 is the only future forecast. Q1 event-holdout metrics are never presented as future-forecast performance.

## 6. Prediction Setting

Formal Q4 uses the last available highway frame as origin and future frame/time as target, but its absolute MOR target is unlabelled. A direct 1/3/6-frame relative-proxy experiment is therefore only a diagnostic. Separately, labelled AMOS uses explicit origins and 5/15/30-minute targets to validate the forecasting protocol.

## 7. Time Grid Audit

Each AMOS event contains 1,440 PTU rows and 5,755 VIS/WIND rows over 24 hours. Within-minute median aggregation yields two complete 1,440-row, one-minute grids with no missing cells, duplicates, or non-one-minute gaps. Events remain separate. Highway frames 1–100 have visible timestamp anchors consistent with approximately 41.67-second spacing.

## 8. Target Definition

Airport target is `MOR_1A` metres. Its observed range is 0–10,000 m, with 518 readings at or below 50 and 225 at 10,000, so tails are treated as special/censored-like sensor behavior. Highway target is explicitly a dimensionless relative contrast proxy, not MOR.

## 9. Feature Availability

All lags/rolling statistics end at the origin. Current origin weather is allowed only in the AMOS diagnostic. Realized future weather, future images, and future MOR are excluded. Fitting labels satisfy `target_time <= origin`; scaler fitting occurs inside each origin. Synthetic probes reject future exogenous fields, post-origin rolling values, global scaling, random splits, recursive true-target use, and reversed time.

## 10. Baseline

Q1 baseline is the other event’s median. Forecast baseline is persistence on common origins. Seasonal naive is not defensible with two isolated 24-hour episodes. Persistence is also used for the relative highway proxy.

## 11. Backtest Protocol

AMOS20191216 supplies the initial historical event; AMOS20200313 is the later contiguous event-transfer holdout. Forty-three origins, spaced 30 minutes apart, are shared across 5/15/30-minute horizons. Highway uses 30 common rolling origins across 1/3/6-frame horizons. No random split or target-row cherry-picking is used.

## 12. Forecast Origins

Each retained prediction table includes origin, target time/frame, horizon, truth, prediction, method ID, training-row count, and maximum training target time/frame. Airport feature maximum time equals its origin.

## 13. Forecast Horizons

Airport: 5, 15, and 30 minutes. Highway: 1, 3, and 6 frames, approximately 0.69, 2.08, and 4.17 minutes. Metrics are not pooled across horizons.

## 14. Primary Model

The fixed primary candidate is standardized Ridge with causal lag/rolling features. Q1 uses a separate contemporaneous log-MOR Ridge. Deep learning is not used: the unavailable airport video blocks Q2, and 100 unlabelled highway frames cannot support a defensible deep absolute-MOR estimator.

## 15. Multi-Step Strategy

`DIRECT`: each horizon has a separate target shift/model. Recursive observed-target leakage is not applicable to the executed model and is explicitly blocked by a synthetic reviewer test.

## 16. Exogenous Variables

Only weather observed at the forecast origin is used in the labelled AMOS diagnostic. No future meteorological forecast is supplied; realized `t+h` weather is `UNKNOWN_AT_ORIGIN` and excluded. Highway uses image-history features only.

## 17. Preprocessing Provenance

Minute aggregation is event-local and timestamp-local. Standardization is fitted separately within each origin’s training subset. There is no interpolation, imputation, centered smoothing, global decomposition, or post-origin fitting.

## 18. Point Forecast Metrics

At 5/15/30 minutes, persistence MAE is 267/360/410 m and RMSE 820/972/998 m. Direct Ridge MAE is 972/1104/1050 m and RMSE 1536/1718/1707 m. Ridge loses clearly, so persistence remains preferred. Q1 Ridge also lacks stable whole-event generalization.

## 19. Horizon-Specific Metrics

Full tables appear in `horizon-metrics.md`. Highway proxy Ridge is mixed: slightly lower 1-frame MAE and lower 6-frame MAE/RMSE, but worse 3-frame error. These are proxy-unit results from one episode.

## 20. Interval Forecast / Coverage

Sequential 80% intervals use only earlier origin errors. Airport coverage is 0.939–0.970 with average width 1,295–2,498 m for persistence and 3,958–4,724 m for Ridge. Highway coverage is 0.90–1.00 with 20 intervals per cell. Overcoverage and wide bands reveal uncertainty rather than validate precision.

## 21. Low-Visibility Performance

Using the statement’s 150 m example, evaluated AMOS low-visibility targets number 12/12/14. Persistence MAE is 12.5/4.2/92.9 m; Ridge MAE is 42.2/75.2/112.3 m. Instrument floor behavior and small counts limit interpretation. Highway low-MOR evaluation is unavailable because no MOR labels exist.

## 22. Distribution Shift

The later event median is 3,200 versus 5,000 m; ≤150 m counts are 421 versus 223; only the later event has 225 observations at the 10,000 m cap. KS statistic is 0.375. This is an event/regime transfer, not IID generalization.

## 23. Failure Analysis

Largest errors coincide with abrupt changes from the 10,000 m cap and rapid increases. Ridge has negative bias at all horizons and lag-1 residual correlations 0.14–0.27. Early-half errors are far larger than late-half errors, showing time-local nonstationarity. Missing-period analysis is not applicable because the audited grids are complete.

## 24. Final Forecasts

The retained highway curve has a positive robust slope, so the allowed qualitative conclusion is `improving_contrast` over the supplied sequence. Rolling short-horizon proxy predictions and uncertainty bands are retained. Absolute highway MOR and the time to MOR = 150 m are `NOT_IDENTIFIABLE_FROM_AVAILABLE_ATTACHMENTS`; no fabricated number is emitted.

## 25. Skill Strengths

Temporal-horizon/availability gates, origin-aware aggregation, naive baseline, rolling backtest, future-exogenous warning, fold-safe preprocessing, output semantics, and interval coverage all operated successfully. They prevented a proxy-to-MOR claim and exposed Ridge underperformance.

## 26. Skill Weaknesses

The prediction reference is terse about named multi-step strategies and common-origin/per-horizon presentation. In this run, that brevity caused no model-behavior failure: existing target-time and feature-cutoff rules already invalidate observed future recursive inputs, and the executed evidence is origin/horizon complete.

## 27. First Meaningful Failure

`NONE_IN_FROZEN_SKILL`. The first material blockers are source/data limitations: unavailable airport video and absence of an identifiable highway proxy-to-MOR mapping.

## 28. Failure Classification

Skill failure level: `NONE`. Ridge underperformance is `ALGORITHM_QUALITY_LIMIT`. Missing Q2/Q4 information is `SOURCE_ATTACHMENT_UNAVAILABLE / DATA_IDENTIFIABILITY_LIMIT`, not a generalizable forecasting-Skill defect.

## 29. Generalizable Gap Candidate

`NONE`. No candidate satisfies both “missing from current Skill” and “actually caused a correctness failure here.” No Skill modification is justified.

## 30. Remaining Uncertainty

Airport video remains unavailable; highway absolute labels and landmark geometry are absent; MOR floor/ceiling semantics are only partially documented; only two airport episodes and one highway episode exist; interval samples are small; proxy changes may mix visibility and illumination.

## 31. Historical Integrity

The Skill tree remains `8deb5278e19862738d8f04f21d8a7b6d3f5eb45e`. Frozen 2007A, 2017F, 2005D, 2020A, 2011B, 2022C, 2023E, and 2024C tree hashes match their starting values. Routes remain 10. No excellent solution, PDF render/cache, extracted archive, video cache, or Python cache is committed.

## 32. Final Decision

`BLIND_RUN_PARTIAL`.

Available-data work is valid and leak-free, but the run cannot honestly complete Q2 or produce absolute Q3/Q4 MOR/dispersal-time claims. The non-substantive search-snippet exposure is also disclosed. The correct next action is human review; do not modify the Skill or start a new problem.
