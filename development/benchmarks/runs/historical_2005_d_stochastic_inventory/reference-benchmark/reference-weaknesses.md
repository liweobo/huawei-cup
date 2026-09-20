# Reference Weaknesses

Each item lists the reference, the evidence location and the consequence. Findings are limited to
what the papers actually show.

## Hidden or unjustified distribution assumptions

- R1 (`work/rendered/readable-仓库容量有限条件下的随机存贮管理.txt`, pages 6-8): asserts each
  product's delivery time "follows a normal distribution" from SPSS output, then uses that law for
  the cost probabilities. No goodness-of-fit test is reported and the conflict with the observed
  supports is not discussed, even though product 1's sample ranges over 0-7 days with two zero-day
  observations and product 3's mode is 1 day. Consequence: using the blind run's frozen cost
  function, the normal law moves product 1's optimum from `L = 36` to `L = 48`, and the
  normal-optimal point is worse than the empirical-optimal point when both are evaluated under the
  empirical law (3.5312 versus 3.4797 per day).
- R3 (pages 4-5): fits a Lorentzian density to product 1 by eye and extends X to a 0-8 range,
  treating each integer as a day interval. No fit statistic is reported. Consequence: product 1's
  reported `L` of 41 is above both the empirical-law and normal-law integer optima found by the
  blind run.
- R2 (pages 10-11) is the counterexample: it runs K-S tests and rejects the parametric families,
  then uses empirical frequencies. This weakness does not apply to R2.

## Mean-field reduction of a nonlinear expectation

- R1 (page 6): states that because delivery time is "relatively stable, essentially at its mean",
  the expected loss is evaluated at `X = E[X]`, reducing the objective to a function of the order
  time alone. `E[c(X)] = c(E[X])` is not valid for this convex cost, so the step is not
  justified in general. Consequence here: recomputing with the frozen cost function shows the
  reduced problem returns the same integer `L*` for all three products on this data, so R1's
  reported answer happens to survive despite the flaw. Recorded as a methodological weakness with
  limited practical effect on this problem.

## No event timing

- All three references: `EVENT_ORDER_UNSPECIFIED`. None states whether the arrival at the
  delivery instant is processed before or after demand and cost accumulation, nor the boundary
  condition for the cycle at that instant. R1 (pages 4-5), R2 (pages 3-5) and R3 (pages 2-4) each
  write a cycle cost as an integral or area without fixing this. Consequence: the papers' results
  cannot be reproduced from the text alone without choosing an order, and a different choice
  changes the boundary stock. The blind run shows this with a one-unit counterexample.

## No uncertainty on any estimate

- All three references: no standard error, confidence interval, replication or convergence check
  appears anywhere. Every reported `L*` and cost is a point value. Consequence: the papers provide
  no way to judge whether a difference between their answers and another analysis is meaningful.
  For product 1, R1 reports 34, R2 reports 36 and R3 reports 41, and no paper can say whether
  those gaps are larger than the uncertainty in the underlying estimate.

## Period-as-iid in the distribution test

- R2 (pages 10-11): the one-sample K-S test treats the 61 delivery observations as independent
  draws from a single distribution. Serial correlation is not examined. Consequence: the blind
  run's input audit finds product 3's lag-1 autocorrelation near 0.47, so the iid premise is
  doubtful for that sample. The effect is bounded because R2 then uses the empirical table anyway,
  and the blind run's block-resampling sensitivity under dependence gives a cost interval that
  overlaps the iid value.

## No convergence checks

- All three references: no horizon, cycle-count or sample-size stability check. R2 reports a
  search-grid error radius below 0.01 for Q4, which bounds the optimiser's precision but not the
  model's. Consequence: none of the reported optima is accompanied by evidence that a finer or
  longer analysis would not move it.

## No cost-unit audit; silent resolution of the c4 conflict

- R1, R2 and R3: the source prints `c4` as a per-lost-item amount in Q1 but as a per-box-day or
  per-volume-day amount in Q2 and Q3. R1 charges a per-unit amount, R2 and R3 include a duration
  factor, and none mentions the discrepancy. Consequence: using the blind run's frozen cost
  function, the two readings give different optima, product 1 moving between `L = 36` and
  `L = 45`. Every published `L*` therefore embeds an unstated unit convention.

## Shortage semantics only partly explicit

- R1 does not separate shortage quantity from shortage duration in the objective. R2 and R3 do
  include a duration term. None states in words whether unmet demand is permanently lost or
  served later, though all three compute as if it is lost. Consequence: the semantic label is
  inferred from the formulas rather than stated, which makes the models harder to reuse or to
  compare against a backorder formulation.

## Unsupported optimality claims

- R1 (page 4) and R3 (page 4) present their `L*` as optimal without qualification. R1's objective
  is evaluated at the mean lead time and R3's uses a fitted density with no statistic, so neither
  optimum is optimal for any clearly established objective. R2's Q2 claim of a global optimum is
  defensible because the search is exhaustive over an integer grid under a fixed empirical law,
  but it is still an optimum of a model rather than of the store, and R2 itself labels Q4 as
  approximate.

## Boundary and integrality handling

- All three references report the optimum as an integer or as a rounded value (R1 34/38/39,
  R2 36/45/34, R3 41/37/36) without distinguishing an attained integer optimum from an infimum
  on an open boundary. The blind run finds that product 3's unconstrained cost decreases toward
  `L = 40` without attaining it, with an admissible integer optimum at `L = 39`, and reports
  `validation/boundary-sensitivity.json` warning against rounding `L` to `Q` while preserving the
  same stockout probability.

## Not a weakness: absence of Monte Carlo

None of the three references simulates. That is not a weakness. A cycle cost is integrable in
closed form under a stated law, so the deterministic route is appropriate and matches the blind
run's analytic-first ordering. No `REFERENCE_UNCERTAINTY_WEAKNESS` is charged for the mere absence
of simulation; the charges above are about missing uncertainty on the analytic results.
