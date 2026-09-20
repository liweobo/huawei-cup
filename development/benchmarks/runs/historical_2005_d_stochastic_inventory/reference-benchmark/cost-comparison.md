# Cost Comparison

## Cost components

| component | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Fixed order fee `c1` | yes, per order | yes, `c1` in `A` | yes, `c1` in `A` | yes, `c1` |
| Own holding `c2` | yes, integrated on own segment | yes | yes | yes, `c2 ∫q2(t)dt` |
| Rented holding `c3` | yes, integrated on rented segment | yes | yes | yes, `c3 ∫q3(t)dt` |
| Shortage `c4` | primary per lost item; alternative duration exposure | per-unit, one reading | per-unit with duration term | per-unit with duration term |
| Purchase cost | not modeled (source gives none) | not modeled | not modeled | not modeled |
| Disposal / overflow penalty | not modeled (overflow is rented, not penalized) | same | same | same |

## Units and timing

The blind run records every component with its unit, timing and source in `cost-ledger.md`, and
flags the printed `c4` inconsistency as `SOURCE_UNIT_CONFLICT` rather than resolving it. It also
separates per-item quantities from per-volume quantities and converts only where the source gives
unit volumes, so yuan-per-item-day and yuan-per-m3-day are never added directly.

None of the three references provides a cost ledger. Each writes a combined expression. R2 and R3
do express the shortage term with a duration factor, which is closer to the source's printed
"per day" wording than R1's single per-unit reading, but neither discusses that the Q1 definition
differs from Q2/Q3.

## Aggregation and reconstructability

| aspect | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Total reconstructable from components | yes, asserted | yes, algebraically | yes, algebraically | yes, algebraically |
| Component-level audit reported | yes (`validation/final-model-audit.json`) | no | no | no |
| Unit consistency checked | yes | not discussed | not discussed | not discussed |
| Objective normalisation | `E[cycle cost] / E[cycle days]` | expected loss per cycle, then minimised | average daily loss `E[f(L,X)]` | average daily loss `E[Y(L,X)]` |

All four aggregate the same four components. The difference is that the blind run also checks that
the aggregate equals the sum of its parts to floating-point tolerance (max component error
`1.8e-15`) and that units are homogeneous before adding.

## The c4 unit conflict, quantified

The source's own inconsistency is the one place where cost accounting changes the answer. Running
the blind run's frozen cost function under each reading:

| product | L* (per lost item) | L* (per day exposure) |
|---|---:|---:|
| 1 | 36 | 45 |
| 2 | 45 | 44 |
| 3 | 39 | 38 |

The references choose one reading each without stating the convention, so their published `L*`
values embed an unlabelled cost-unit choice.

## Classification

- Cost component structure: `REFERENCE_CONSENSUS`.
- Cost-unit audit and c4 conflict preservation: `SKILL_STRENGTH`.
- Component reconstructability: `REFERENCE_CONSENSUS` for the algebra, `SKILL_STRENGTH` for the
  explicit audit.
