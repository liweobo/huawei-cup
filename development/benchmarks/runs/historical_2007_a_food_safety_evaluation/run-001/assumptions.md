# Assumptions and Claim Boundaries

## Structural assumptions

1. **Canonical taxonomy.** Every observed food category maps to one or more canonical food groups through nonnegative shares whose row sum is one. Ambiguous shares remain scenario parameters rather than silently choosing a label.
2. **Conditional integration.** Because the intake and contaminant samples are unpaired, their draws are independent only after conditioning on the declared region, season, demographic, and food group. Residual dependence is a sensitivity dimension.
3. **Sampling designs matter.** Household and monitoring inclusion probabilities enter estimates. Selected-region observations do not become national observations without declared target-population weights or a transport model.
4. **Nondetects are left-censored.** A nondetect means the latent concentration is below a method-specific detection limit. It is neither known zero nor a detected value at the limit.
5. **No universal distribution.** Candidate distributions must be checked by food/contaminant/stratum. The lognormal family in the executable experiment is a synthetic test scenario, not a universal food-safety assertion.
6. **Unit compatibility.** Food intake, concentration, body-weight adjustment, and the standard are converted to a common physical unit before multiplication or comparison.
7. **Hard gate.** A point or uncertainty threshold violation cannot be compensated by coverage, sample size, or other ordinary criteria.
8. **Tail uncertainty.** A `99.999%` quantile needs model-form, parameter, and numerical-tail uncertainty. Monte Carlo precision alone is insufficient.

## Synthetic experiment assumptions

- Three food groups; 3,000 synthetic intake records; 600 synthetic monitoring values per group.
- Lognormal intake medians: 250, 120, and 50 synthetic food-mass units/person-day; log standard deviations: 0.35, 0.55, and 0.75.
- Lognormal concentration medians: 0.08, 0.20, and 0.60 synthetic contaminant/food units; log standard deviations: 0.80, 1.00, and 1.20.
- Detection limits: 0.05, 0.10, and 0.30 in the same synthetic concentration units.
- Random seed `2007`; all stochastic outputs are simulation, not measurement.
- The illustrative standard is `0.95 ×` the known-parameter synthetic oracle quantile. Its provenance is `ASSUMED_SYNTHETIC`; it must not be cited as regulation.
- The six assessment units used for ranking sensitivity are fictional. Names are neutral scenario labels, not real regions or contaminants.

## Missing-data and extreme-value policy

- Record mechanism by field: design absence, nondetect censoring, item nonresponse, and taxonomy mismatch are different.
- Do not fill missing concentrations with zero.
- Audit extreme observations against lab method, units, sampling context, and influence. Retain plausible true hazards; correct documented errors; compare robust/tail models when unclear.
- Do not delete extremes solely because an IQR rule flags them.

## Allowed claims

Allowed: formulas, conditional model architecture, reproducible synthetic behavior, and identified failure modes.

Not allowed: actual Chinese exposure estimates, actual contaminant ranking, legal compliance, a safety probability, a verified `99.999%` national quantile, or a policy action justified only by this synthetic run.
