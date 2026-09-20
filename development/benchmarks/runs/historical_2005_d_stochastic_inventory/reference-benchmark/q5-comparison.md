# Q5 Comparison

Q5 is open-ended: sales are often random and ordering conditions change after some time. The
source supplies no demand law, no parameters, no change date, no horizon and no service
requirement.

## How each analysis handled an under-specified problem

| aspect | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Demand randomness | declared two-point daily multiplier scenario | continuous random demand, Normal-parameterized | Markov-chain sales rate `{R_t}` | jointly random `(X, r)` with joint density `f(X,r)` |
| Provenance labelling | explicit `SCENARIO`, not claimed as empirical | presented as a model assumption without a scenario label | presented as a model assumption | presented as a model assumption |
| Change over time | explicit shift at a declared day | not modeled | periodic order cost `c1(t)` with period `T`, periodic Markov chain | not modeled |
| Horizon | finite 120 days, no period deleted | not stated | not stated | not stated |
| Policy discussed | static vs adaptive threshold, compared with CRN | `(R,Q)` policy, EOQ and reorder-level formulas | Markov framework, `min E[E[f(R_t,L,X)]]` | joint density objective |
| Optimality claim | none for Q5; scenario result only | discusses formulas, no unique optimum claimed | framework only, explicitly says solving requires extra assumptions | objective stated, no solved optimum |

## Assumption provenance

This is the sharpest difference. The source gives Q5 no numbers, so every analysis must invent
something. The question is whether the invention is labelled.

- R1 introduces continuous random demand with mean `D` and standard deviation `δ`, writes
  `f(x, DL, δ, L)`, and derives EOQ and reorder formulas. It presents these as the model's demand
  law without flagging that the law is the author's choice, and it does not present the result as
  a scenario.
- R2 is the most careful: it explicitly states "this model only establishes a basic theoretical
  framework; the concrete model must be built with the actual problem, and whether `L*` can be
  solved depends on the problem's complexity and the parameters' distributions". It claims no
  numeric optimum.
- R3 writes a joint density `f(X, r)` and an objective integral but similarly stops at the
  framework.

The blind run's Q5 is the only analysis that (a) fully specifies its scenario numbers, (b) labels
the demand law `SCENARIO` rather than a model fact, (c) declares a finite horizon explicitly, and
(d) reports the result as a scenario comparison with an interval rather than as an optimum.

## Reported Q5 results

R1, R2 and R3 report no numerical Q5 result, so there is no numeric comparison to make. Only the
blind run produces numbers: static cost/day 13.3559 with CI [13.1855, 13.5263], adaptive 12.8835
with CI [12.7406, 13.0264], paired difference -0.4724 with CI [-0.6207, -0.3241].

Because the blind run's scenario is its own construction, these numbers are not comparable to any
reference even in principle. They are reported as `SCENARIO_RESULT`.

## Classification

- Q5 assumption provenance: `SKILL_STRENGTH`. The blind run labels a self-invented law as a
  scenario; R1 presents an invented demand law as the model.
- Q5 caution about unsolvable frameworks: `REFERENCE_CONSENSUS` with R2, which reaches the same
  caution explicitly. R1 is the outlier in deriving EOQ-style formulas from unlabelled
  assumptions.
- Q5 numeric comparability: not applicable; no reference reports a number.
