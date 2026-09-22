# Models

## Q1: contemporaneous relationship

`log1p(MOR)` is modeled with standardized temperature, relative humidity, dew-point spread, pressure, wind speed, and sine/cosine wind direction using Ridge (`alpha=10`). The fitted equation and feature scaling are retained in `outputs/q1_relationship_formula.json`.

Whole-event holdout shows no robust improvement over the event-median baseline. The Ridge model is therefore a descriptive association candidate, not an accepted predictive law: for the December holdout MAE rises to 3,509 m; for the March holdout it falls slightly to 3,220 m but RMSE rises to 4,688 m and Spearman correlation is −0.145.

## Labelled AMOS forecast diagnostic

At each origin, a fresh standardized Ridge fits `log1p(MOR(t+h))` separately for each horizon. Features include current and lagged MOR, right-aligned rolling statistics, and only meteorology observed at the origin. The strategy is DIRECT. Predictions are clipped to the audited operational range 50–10,000 m; actual zero/low special values remain in scoring.

This candidate is intentionally modest. It performs worse than persistence at every horizon and is rejected for final point-forecast preference. That is an empirical algorithm limitation, not a Skill gap.

## Highway scene

The current image is converted into a fixed-ROI relative contrast proxy: 90th-percentile Sobel gradient magnitude divided by mean luminance. A Theil–Sen slope over all 100 frames is `1.157e-6` proxy units/minute with a descriptive 95% slope interval `[3.916e-7, 1.968e-6]`, indicating improving scene contrast.

For protocol testing, separate Ridge mappings predict the proxy 1, 3, and 6 frames ahead from causal proxy lags/rolls. This is not a deep image network and is not claimed as an absolute highway-visibility solution. With no MOR labels, a deep model would add complexity without making MOR identifiable.

## Output semantics

- Airport output: physical MOR metres, supported only within the two supplied episodes.
- Highway output: dimensionless relative proxy and its relative trend.
- No highway probability, absolute MOR, regulatory status, or 150 m crossing time is emitted.
