# Tail-Risk Comparison

| ref | distribution family/body model | fitting method and sample source | tail / extrapolation method | `99.999%` handled? | numerical result | validation | uncertainty |
|---|---|---|---|---|---|---|---|
| `REF-01` | regression intake; Nakagami-m contamination candidate | literature/sample tables; bootstrap augmentation of roughly 2% quantitative data | EVT maximum-domain approximation, Hill estimator, Pareto/slowly varying correction | yes in formula and example | `41.9259 µg/person-day` | small illustrative dataset; no tail coverage study | none for q; qualitative only |
| `REF-02` | truncated-normal intake; lognormal-kernel contaminant KDE | simulated data and bootstrap reconstruction | integrate product CDF by Gauss-Legendre and solve `F(z)=0.99999` | yes in derivation | no auditable real-data q | density simulations, not rare-tail validation | none for q |
| `REF-03` | candidate parametric fits or density evolution | iterative allocation of nondetects; no actual monitoring dataset | Monte Carlo/importance sampling and weighted/order-statistic tail estimate; states `M>=10^7` | yes in explicit algorithm | none | explicitly untested on real data | none for q |
| `REF-04` | lognormal intake; beta contaminant | maximum-entropy argument and sparse literature-derived data | ordinary Monte Carlo, histogram accumulation and numerical quantile search | yes in algorithm/example | about `0.027 mg/person-day` | shape/scale comparison only | none for q |
| `REF-05` | BP intake model; polynomial contaminant/exposure density | cited data and fitted polynomial | integrate polynomial CDF and solve a seventh-degree equation | yes nominally | selected `0.989689 µg` from two positive roots | no CDF-validity/root-selection/tail validation | none |
| `REF-06` | same as `REF-02` | same | same | same | same | duplicate | same |

## Tail audit

All five unique works address the requested `99.999%` tail in more than name; none substitutes only a mean, 95%, or 99% statistic. Quality varies substantially:

- `REF-01` is the only work to introduce explicit extreme-value/Pareto tail machinery.
- `REF-03` recognizes the required rare-event sample scale and importance sampling, but its proposed estimator is not validated.
- `REF-02/06` and `REF-04` use numerical integration or ordinary Monte Carlo without demonstrating adequate effective tail sample size.
- `REF-05` uses a fitted polynomial CDF and selects one of multiple roots without verifying monotonicity, support, or unique quantile existence.

These defects are G2 `2007A_SPECIFIC_METHOD` or G5 `DATA_ESTIMATION_LIMITATION`. They do not by themselves prove an evaluation-semantics Skill gap.
