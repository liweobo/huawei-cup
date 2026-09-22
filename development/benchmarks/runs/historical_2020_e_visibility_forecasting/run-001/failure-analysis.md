# Forecast failure analysis

## Largest errors and rapid changes

The airport’s largest common failure occurs at origin 2020-03-12 16:30, where current MOR is at the 10,000 m cap but future targets fall to 5,000/4,750/4,600 m at 5/15/30 minutes. Persistence and clipped Ridge both miss by roughly 5,000–5,400 m. Other large Ridge misses include a rise to 9,000 m at 15 minutes predicted near 4,493 m and a rise to 8,000 m at 30 minutes predicted near 3,554 m.

These are rapid transition/cap-exit cases. `outputs/amos_largest_errors.csv` retains the 30 largest absolute errors with rapid-change and low-visibility flags.

## Low visibility

Using 150 m solely because the problem gives it as an example, persistence is better than Ridge at all horizons. The subset contains only 12–14 evaluated origins per horizon and is dominated by instrument floor behavior. It supports a warning, not a precise rare-event performance claim.

## Distribution shift

The later event has a lower median, more ≤150 m readings, and a new 10,000 m ceiling mass. The KS statistic is 0.375. Cross-event Q1 Ridge performance is unstable, and its correlation reverses sign on one holdout. The event distribution shift is disclosed rather than diluted with random CV.

## Residual audit

Ridge bias is negative at every horizon (−384 to −482 m); persistence bias is positive (53–99 m). Ridge lag-1 residual correlations are 0.14–0.27, compared with −0.04–0.08 for persistence. For both methods, first-half MAE is much larger than second-half MAE (for example, 5-minute Ridge 1,708 vs 270 m), showing strong time-local regime dependence rather than stationary errors. Absolute-error/prediction correlations of roughly 0.18–0.28 provide a descriptive heteroskedasticity warning. These diagnostics are retained in `outputs/amos_residual_audit.csv` and do not justify a formal stochastic residual model with only one held-out event.

## Missing-data periods

There are no missing minute rows after audited within-minute aggregation, so no missing-period failure subset applies. No interpolation crosses a split.

## Highway limitations

Proxy forecast residuals are scene/lighting sensitive. The single scene provides no way to separate fog change from illumination/contrast change, and no absolute label exists. Therefore the model does not emit a fabricated 150 m dispersal time.

## Algorithm versus Skill

Ridge underperformance is `ALGORITHM_QUALITY_LIMIT`, not a generalizable Skill gap. The current Skill required the baseline, temporal split, feature cutoff, horizon-specific metrics, and interval coverage that exposed the failure.
