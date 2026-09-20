# Uncertainty Comparison

## What uncertainty each analysis reports

| aspect | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Sample size / replications | reported (128, 256; 512, 1024 cycles) | none | input sample sizes given (36/43/61) | input sample sizes given |
| Independent replication unit | complete trajectory | n/a | n/a | n/a |
| Standard error | reported per estimate | not reported | not reported | not reported |
| Confidence interval | reported per estimate | not reported | not reported | not reported |
| Seed | recorded | n/a | n/a | n/a |
| Convergence | horizon and replication refinement | none | none | none |
| Uncertainty on the optimum | flagged boundary cases, `ESTIMATE_UNSTABLE` where applicable | none | error radius < 0.01 for the Q4 search | none |

No reference reports any uncertainty on its estimated cost or on its fitted distribution.

## Period-as-iid risk

The instruction asked whether any paper treats serially dependent per-period data as iid when
computing a standard error or interval. None of the three computes a standard error or interval at
all, so none commits that specific error. R2's K-S test treats the 61 delivery observations as
exchangeable draws from one distribution, which does assume they are iid; R2 does not discuss
serial correlation. Using the blind run's own input audit, product 3's lag-1 autocorrelation is
about 0.47, so the iid premise is questionable for that sample. R2 stands behind the empirical
frequency table anyway, which is the same table the blind run used, so the practical consequence
is bounded by the blind run's block-resampling sensitivity rather than open-ended.

This is a genuine `REFERENCE_UNCERTAINTY_WEAKNESS` for R2's distribution test, but it does not
change the point estimate because R2 uses the empirical table regardless.

## Serial dependence in inventory paths

A long inventory path is serially dependent, so the number of periods is not the number of
independent observations. The blind run resolves this by making a complete trajectory the
replication unit and by running a circular block-resampling sensitivity on the lead process
(product 3, block length 4, 256 replications: cost 11.3586, CI [11.3321, 11.3852]).

No reference addresses within-path dependence, because none computes an interval. This is
`SKILL_STRENGTH` relative to the references, and the instruction explicitly says not to lower the
standard because the references omitted it.

## Rare events

The blind run's stockout probabilities are 0.278, 0.140 and 0.557 with large event counts, and it
labels them `ADEQUATE_EVENT_COUNT`. The one event-count concern, the discrete-uniform Q4 service
probability at a numerical boundary, is labelled `ESTIMATE_UNSTABLE`. No reference reports an
event count or a rare-event caveat, since none simulates.

## Classification

- Monte Carlo uncertainty reporting: `SKILL_STRENGTH`.
- Replication-unit discipline: `SKILL_STRENGTH`.
- Serial-dependence handling: `SKILL_STRENGTH`.
- Reference uncertainty reporting: `REFERENCE_UNCERTAINTY_WEAKNESS` for all three, most notably
  R2's silent iid premise in its K-S test.
