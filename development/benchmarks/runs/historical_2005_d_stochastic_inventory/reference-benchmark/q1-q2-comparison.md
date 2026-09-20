# Q1-Q2 Comparison

## Method family

| aspect | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Analytical structure | Regenerative renewal-reward; `E[cycle cost] / E[cycle days]` in closed form | Expected loss on one cycle, minimised | `E[f(L,X)]` with `df/dL = 0` via Maple, plus exhaustive search | `E[Y(L,X)]` via Matlab iteration |
| Long-run rate established | yes, from renewal-reward | no | partial: `f(L,X)` is an average per day, expectation taken over X | partial: same |
| Process model | Renewal process | Single cycle | Single cycle | Single cycle |
| Simulation used | yes, as independent verification | no | no | no |
| Search method | Exact finite-support piecewise minimisation; integer enumeration checked | Lingo NLP | Exhaustive integer search over `L` (order `Q0` values) | Iterative solve |

## The `E[cost/duration]` question

The instruction was to check whether any reference substitutes `E[cost / duration]` for
`E[cost] / E[duration]`, or fails to justify a long-run average.

R1 optimises `min C` where `C` is an expected loss per cycle, and then divides by the cycle length
only inside `f(L,X) = Y(L,X)/T`. It never forms a long-run rate, and it does not claim to have
proved one. More importantly, R1 evaluates the expectation at `X = E[X]` rather than over the law,
justified by "delivery is usually stable and essentially at its mean". That is a mean-field
reduction, not a proven identity. On this data it happens to give the same integer `L*` for all
three products (verified with the frozen cost function), so the flaw is real but did not change
R1's reported answer.

R2 does better. It defines `f(L,X)` as an average per-day loss and then takes
`E[f(L,X)] = Σ f(L,x_i) P(x_i)`, which is a genuine expectation of a ratio. Whether that equals a
long-run cost rate is not argued, but the object it computes is at least well defined and, because
cycles are regenerative under the model's assumptions, the value is the correct renewal-reward
rate. R2 does not state this, so its result is correct for a reason it does not give.

R3 defines `Y(L,X)/T` per cycle and minimises `E[Y(L,X)]`, again without a long-run justification.

The blind run is the only analysis that names the renewal structure and reports
`E[cycle cost] / E[cycle days]` as a ratio of expectations, with the ratio bias from finite
replications explicitly measured.

## Verification strategy

| aspect | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Closed form provided | yes | yes | yes (with Maple derivative) | yes |
| Special-case checks | zero-lead, long-lead, exact enumeration, hand-computed cycles, finite-day oracle | none | none | none |
| Independent simulator cross-check | yes | no | no | no |
| Monte Carlo uncertainty | yes | no | no | no |

R2 comes closest to the blind run's rigour: it writes the derivative of the expected cost and a
full search program, and its published code can be re-executed. But it reports no uncertainty, no
convergence and no independent check.

## Reported results

| product | Blind run L* | R1 L* | R2 L* | R3 L* |
|---|---:|---:|---:|---:|
| 1 | 36 | 34 | 36 | 41 (41.3918) |
| 2 | 45 | 38 | 45 | 37 (37.0612) |
| 3 | 39 | 39 | 34 | 36 (36.4637) |

The blind run agrees exactly with R2 on products 1 and 2, which is notable because R2 is the only
reference that also uses the empirical frequency table. Products 2 and 3 diverge across all
references, and those divergences are explained by the two convention choices quantified in
`distribution-comparison.md` and `cost-comparison.md`, not by arithmetic error.

## Direct numeric comparability

Under §32 a numeric comparison requires the same shortage semantics, the same c4 unit
interpretation, the same lead-time law, the same joint-allocation convention and the same
objective. None of the three references satisfies all five at once against the blind run:

- R1 uses a Normal law and a per-unit c4.
- R2 uses the empirical law and a duration-based c4, matching on the first and differing on the
  second.
- R3 uses a Lorentzian and a duration-based c4.

Therefore the product-level numbers are `NOT_DIRECTLY_COMPARABLE` in general. The one defensible
statement is that the blind run and R2 agree on products 1 and 2 despite using the empirical law
in both, because the remaining differences do not bind for those two products.

## Classification

- Lead-law handling: `REFERENCE_CONSENSUS` with R2; `SKILL_STRENGTH` against R1/R3.
- Long-run renewal formulation: `SKILL_STRENGTH`. No reference establishes it, and R2 only gets
  it right implicitly.
- Analytic-before-simulation: `SKILL_STRENGTH`. Every reference is analytic or search-based; the
  blind run adds a simulator purely as an independent check, so it does not fall into
  Monte-Carlo-only reasoning, and it does not assume simulation is required merely because the
  problem is stochastic.
- Small-case validation: `SKILL_STRENGTH`. No reference reports any.
