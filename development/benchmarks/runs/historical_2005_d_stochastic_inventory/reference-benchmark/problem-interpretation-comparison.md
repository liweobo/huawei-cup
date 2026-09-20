# Problem Interpretation Comparison

## What the source actually says vs what each reading assumes

All four analyses (blind run plus three references) agree on the Q1-Q4 skeleton: one or more
products with constant sales rate, a random delivery lead time, a fixed own warehouse capacity
`Q0`, a fixed arrival top-up level `Q`, own and rented holding costs, a fixed order fee, and a
shortage cost. They diverge on four points that decide the numbers.

| element | Blind run (run-001) | R1 | R2 | R3 |
|---|---|---|---|---|
| Objective | Long-run expected cost per calendar day | Expected loss on one cycle, minimized at `X = E[X]` | Average daily loss `E[f(L,X)]`, minimized over `L` | Average daily loss over one cycle, `E[Y(L,X)]` |
| Lead-time law | Empirical PMF (Q2); parametrized where ungiven (Q1) | Normal fitted to each sample (SPSS) | Empirical frequencies after K-S rejection | Lorentzian fit (product 1); empirical probabilities elsewhere |
| Shortage reading | Lost sales, run twice for the c4 unit conflict | Lost sales, single reading | Lost sales with an explicit shortage-duration term | Lost sales with explicit shortage-duration term |
| Own/rented split | Own filled first, overflow rented; holding integrated on both segments | Same structure, three arrival-stock cases | Same structure, three cases | Same structure, three cases |
| c4 unit conflict | Preserved and both readings run | Silently taken as the printed per-unit value | Taken as per-unit per-day in the loss term | Taken as per-unit per-day in the loss term |

## Where the interpretation genuinely diverges

The source's `c4` is printed inconsistently: Q1 defines it per lost item, while Q2 and Q3 print
it per box-day or per volume-day. The blind run treated this as a source defect and ran both
readings. All three references pick one reading without noting the conflict. Using the blind
run's own frozen cost function, the choice is not cosmetic:

| product | L* under per-item lost sale | L* under per-day exposure |
|---|---:|---:|
| 1 | 36 | 45 |
| 2 | 45 | 44 |
| 3 | 39 | 38 |

For product 1 the two readings differ by nine units. Any single published L* therefore carries an
unstated unit convention.

The second divergence is the lead-time law, and it produces the largest spread across all four
analyses. Using the same frozen cost function and swapping only the law:

| product | L* under empirical PMF | L* under discretized Normal |
|---|---:|---:|
| 1 | 36 | 48 |
| 2 | 45 | 45 |
| 3 | 39 | 39 |

The normal assumption moves product 1 by twelve units. Evaluating the normal-optimal `L = 48`
under the empirical law costs 3.5312 per day, worse than the 3.4797 obtained at `L = 36`, so the
reference point is not merely different, it is dominated once the empirical law is taken as the
better estimate of the same data.

One reference choice turns out to be harmless. R1 evaluates the expected cost at `X = E[X]`
instead of over the full law, which is not mathematically justified for a nonlinear cost. On this
data it happens to return the same integer `L*` for all three products, so it is a methodological
weakness that did not change R1's answer here.

## Classification

- c4 unit handling: `SKILL_STRENGTH`. The blind run detects and preserves a genuine source
  ambiguity that the references silently resolve.
- Empirical vs parametric lead law: `SKILL_STRENGTH`. R2's K-S evidence matches the blind run's
  decision to avoid an invented parametric family, and R1/R3's parametric fits change the answer.
- Cycle-versus-long-run objective: `REFERENCE_WEAKNESS`. The references optimize an expected
  per-cycle ratio without establishing the long-run rate; see `q1-q2-comparison.md`.
- Overall problem interpretation: `REFERENCE_CONSENSUS` on structure, with the blind run adding
  provenance discipline rather than a different model skeleton.
