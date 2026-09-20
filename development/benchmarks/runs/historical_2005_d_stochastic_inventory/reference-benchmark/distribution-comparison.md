# Distribution Comparison

## Q1-Q2 lead time

| question | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Distribution assumed | None for Q1; empirical PMF for Q2 | Normal, all three products | Discrete, empirical frequencies | Lorentzian for product 1, empirical otherwise |
| Parametric fit | No | Yes (SPSS) | No (after K-S rejection) | Yes (Origin Lorentzian) |
| Goodness-of-fit check | Recorded as unprovable from short samples | None reported | K-S against Normal, Uniform, Exponential; all rejected at p<=0.001 | Visual fit only |
| iid assumption | Stated as a limited-evidence assumption | Implicit | Implicit | Implicit |
| Serial dependence check | Block-resampling sensitivity on product 3 | None | None | None |
| Handling of ungiven law | Parametrize, do not invent | n/a (claims a fit) | n/a | n/a |

R2 is the important case. It runs one-sample Kolmogorov-Smirnov tests for Normal, Uniform and
Exponential on product 3 and obtains asymptotic significances of 0.001, 0.000 and 0.000, all
below 0.05, and concludes X is not one of those continuous families. It then adopts the empirical
frequency table. That is the same decision the blind run made, reached independently and with an
explicit test. This is `REFERENCE_CONSENSUS` and simultaneously a check that the blind run's
choice was not idiosyncratic.

R1 and R3 instead fit parametric families. R1 asserts "X follows a normal distribution" for each
product from SPSS output and reports means and standard deviations that match the sample moments
(2.9722/1.521, 2.535/0.855, 1.951/1.161). R3 fits a Lorentzian to product 1 and treats X as
continuous on a finer grid, noting that integer day labels should be read as intervals.

## Why the family choice matters

The empirical and normal laws differ most where the cost is nonlinear, near zero stock. Comparing
bin probabilities:

| product | empirical P(X<=1) | normal P(X<=1) | empirical mode | normal mode region |
|---|---:|---:|---|---|
| 1 | 0.167 | 0.167 | 3 (0.417) | 2-3 (0.469) |
| 2 | 0.047 | 0.113 | 2 (0.535) | 2-3 (0.758) |
| 3 | 0.443 | 0.349 | 1 (0.443) | 2 (0.333) |

Product 3 is the clearest case: the data put 44.3% of mass at exactly one day, which is the value
that decides whether stock runs out. A normal fit spreads that mass across two to three days.

Re-running the blind run's frozen cost function with only the law swapped gives:

| product | L* empirical | L* normal | cost/day at empirical L* (emp law) |
|---|---:|---:|---:|
| 1 | 36 | 48 | 3.4797 |
| 2 | 45 | 45 | 4.8754 |
| 3 | 39 | 39 | 11.4419 |

For product 1 the normal-based optimum (`L = 48`) evaluated under the empirical law costs 3.5312
per day versus 3.4797 at `L = 36`. The two laws do not simply relabel the same answer.

## Q4 Uniform(1,3)

| interpretation | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Continuous Uniform(1,3) | Primary | Yes (uses F(x) with density 1/2 on [1,3]) | No | No |
| Discrete Uniform{1,2,3} | Alternative scenario | No | Yes, explicitly "1,2,3 equally likely" | No |
| Other | Continuous primary with discrete sensitivity | Continuous | Discrete | Six arrival-time intervals by state, X continuous in the single-item part |

R2 states plainly that "since arrival time X is an integer, it can be considered a discrete
uniform between 1 and 3, equivalent to P(X=1)=P(X=2)=P(X=3)=1/3", and its Q4 program uses
`prob=[1/3 1/3 1/3]`. R1 uses the continuous distribution function with density 1/2 over [1,3].
The references therefore split, so the honest label is:

`MIXED_REFERENCES` for the Q4 uniform interpretation.

The blind run's decision to carry both readings is exactly the response this split warrants. It
is neither a strength relative to a unanimous consensus nor a gap; it matches the strongest
available reading of the ambiguity.

## Classification

- Q2 empirical-vs-parametric: `REFERENCE_CONSENSUS` with R2, and `SKILL_STRENGTH` relative to
  R1/R3, whose parametric fits change the optimum.
- Q4 continuous-vs-discrete uniform: `MIXED_REFERENCES`. The blind run's dual treatment is
  appropriate.
- Distribution provenance discipline: `SKILL_STRENGTH`. No reference labels its assumptions as
  given, estimated or assumed; the blind run does, and it does not promote a mean to a family.

## Verified numbers

The reference reported values were taken from `work/rendered/readable-*.txt` and cross-checked
against the visual page renders. The impact figures above were produced by the frozen run-001
cost function in `work/distribution-choice-impact.json`, not by a new model.
