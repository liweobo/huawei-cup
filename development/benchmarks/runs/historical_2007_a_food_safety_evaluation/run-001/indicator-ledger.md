# Indicator Ledger

The problem is not treated as a generic multi-indicator ranking task. The following ledger separates physical risk, hard compliance, triage context, and evidence quality.

| name | meaning | source | unit | direction | scale_type | benefit_or_cost | hard_constraint_or_soft_criterion | measurement_quality | missingness | redundancy_risk | aggregation_level |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `I_j` | daily intake of canonical food group `j` | survey; source requires total-diet information | food mass/person-day | NON_MONOTONIC across nutrients; COST only for a fixed contaminant pathway | ratio | context/input | input, not criterion | survey weights, household allocation, recall/weighing error | likely | overlaps derived `D` if reused | person-day/stratum |
| `C_jc` | contaminant `c` concentration in food group `j` | monitoring/port/emission-linked evidence | contaminant mass/food mass | COST | ratio, left-censored | cost | input; food-level regulatory limit may be hard if applicable | method, LOD/LOQ, sampling design | nondetect is censored, not zero | overlaps derived `D` | sample-food-region-season |
| `D_c` | daily intake `Σ_j I_j C_jc` | DERIVED | contaminant mass/person-day | COST | ratio | cost | risk input | inherits both component errors and dependence assumptions | propagates source missingness | composite of `I` and `C`; do not weight again | person-day/population |
| `q_0.99999(D_c)` | high-exposure right quantile required by source | PROBLEM_GIVEN + DERIVED from fitted distribution | same as `D_c` | COST | ratio | cost | compared with hard threshold | extreme-tail model and Monte Carlo uncertainty | unavailable without model/data | strongly overlaps point ratio | population/assessment cell |
| `T_c` | applicable authority safety standard | EXTERNAL/REGULATION required operationally | same as `D_c` | TARGET/INTERVAL boundary | ratio | neither | hard constraint | version/scope/unit must be verified | missing in supplied problem | denominator of ratios | contaminant/population/time |
| `ρ=q/T` | point high-tail-to-standard ratio | DERIVED | dimensionless | COST with hard target at 1 | ratio | cost | hard gate | sensitive to both q and T | missing if either is missing | overlaps q and upper ratio | assessment cell |
| `ρ_U=q_U/T` | uncertainty-upper ratio | DERIVED | dimensionless | COST with hard target at 1 | ratio | cost | uncertainty gate | depends on bootstrap/scenario/model-form coverage | unavailable without uncertainty analysis | highly correlated with point ratio | assessment cell |
| `P(D>T)` | exceedance probability, only if a probability model is defensible | DERIVED OPTIONAL | probability | COST | ratio | cost | hard/soft per policy | calibration and tail fit required | often unavailable | correlated with q/T but not identical | assessment cell |
| `population_exposed` | number of people in the assessment cell | survey/census required operationally | persons | COST for action priority, not individual safety | ratio | cost | soft triage criterion | coverage/year must match | possible | can duplicate sampling weights | geography/time |
| `monitoring_coverage` | proportion of declared scope covered by valid monitoring | DERIVED from design | proportion | BENEFIT | ratio | benefit | evidence-quality flag; cannot offset hazard | frame and denominator required | possible | overlaps effective sample size | assessment cell |
| `effective_sample_size` | information after survey weights/clustering/censoring | DERIVED | count-equivalent | BENEFIT but NON_MONOTONIC as a safety claim | ratio | benefit | evidence-quality flag | design-specific | possible | correlated with coverage | assessment cell/model |

## Composite-indicator provenance

`D_c` retains the raw `I_j`, `C_jc`, canonical taxonomy, mapping matrix, units, dependence assumption, and formula. `q`, `ρ`, and `ρ_U` retain their probability level, model, threshold, and uncertainty method. A final column without these ancestors is not admissible evidence.

The synthetic baseline includes both `ρ` and `ρ_U`; this is deliberately flagged as semantic/derived-variable overlap. It is acceptable only as a transparent stress-test baseline. The primary noncompensatory rule does not additively double-weight them.

## Qualitative codes

- `VIOLATION`: point ratio above one;
- `UNCERTAIN`: point ratio at or below one but upper ratio at or above one;
- `COMPLIANT_UNDER_MODEL`: upper ratio below one.

These definitions are derived from the threshold ratio and uncertainty envelope. They are not expert scores and are not historical legal labels.
