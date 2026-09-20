# State / Event Comparison

## State variables actually used

| state element | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| On-hand inventory | yes, `I(t)` continuous | yes, `F(t) = Q - r t` | yes, `q` | yes, `q2(t)` own, `q3(t)` rented |
| Own/rented split | yes, boundary at `Q0` | yes, three cases by arrival stock | yes, three cases | yes, explicit `q2(t)`/`q3(t)` |
| Outstanding order | yes, single-order flag | implicit (one order per cycle) | implicit | implicit |
| Lead time / residual time | yes, elapsed time since review `tau` | yes, X | yes, X | yes, X plus `T_L` |
| Overflow quantity | yes (rented segment) | yes | yes | yes |
| Backorder | no (lost sales) | no (lost sales) | no (lost sales) | no (`L_i<0` means stockout, not backlog) |
| Allocation across items | yes, reserved volumes `a_i`, `b_i` | yes, `Q_i`, `Q0_i` | yes, `Q_i`, `Q0_i` | yes, `Q_i`, `Q0_i` |

All four carry the same essential state. No reference omits a state the blind run needed, and the
blind run adds only the explicit elapsed-time variable that makes event timing well defined.

## Event timing

This is where the references are silent and the blind run is not.

| aspect | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Order of demand-integration vs receipt within a cycle | Explicit assumption: integrate demand and holding over the open interval, then receive and top up, then review | `EVENT_ORDER_UNSPECIFIED` | `EVENT_ORDER_UNSPECIFIED` | `EVENT_ORDER_UNSPECIFIED` |
| Cost accumulation | Integrated exactly between events | Area formulas over the cycle | Area formulas over the cycle | Integral of `q2(t)`, `q3(t)` over the cycle |
| Whether the choice was examined | Yes, with a one-unit counterexample | No | No | No |

R1, R2 and R3 all write a cycle cost as an integral or area and then optimize `L`. None states
whether the receipt at the arrival instant is processed before or after demand and cost for that
instant. That is `EVENT_ORDER_UNSPECIFIED` in all three. Because each paper works with a
continuous-time integral, the question is partly hidden: the integral is insensitive to the
ordering of a single instant, but the boundary condition at the arrival instant (whether the
cycle ends with stock `L` or with a shortage) does depend on it.

The blind run states the order explicitly and demonstrates with a one-unit example that the two
orders give different fulfilled, lost and ending-inventory values. It then verifies directly that
the production implementation follows the stated order.

## Capacity semantics

| aspect | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Own capacity `Q0` | hard cap, own filled first | hard cap, case split at `Q0` | hard cap, case split at `Q0` | hard cap, split at `Q0` |
| Overflow handling | rented storage at `c3` | rented storage at `c3` | rented storage at `c3` | rented storage at `c3` |
| Truncate/reject/discard | never | never | never | never |
| Silent clipping | none | none | none | none |

Full agreement, and agreement with the source. No paper treats `Q0` as a truncation limit; all
four route excess into rented capacity and charge `c3`. This is `REFERENCE_CONSENSUS` and also a
confirmation that the blind run's hard-capacity handling matches the problem's intent.

## Shortage semantics

| aspect | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Lost sales vs backorder | lost sales | lost sales | lost sales | lost sales |
| Shortage quantity | lost demand, `d * (tau - b/d)+` | computed per case | computed per case | computed per case |
| Shortage duration term | in the alternative c4 reading | not used | yes, in the cost expression | yes, in the cost expression |
| Service failure defined | stockout probability and fill rate, separately | not defined | not defined | not defined |

All four read shortages as lost sales, which matches the source's "reduces sales" language. The
blind run is the only one that both computes a duration-based charge and keeps it as a labelled
alternative rather than the default.

## Classification

- Capacity handling: `REFERENCE_CONSENSUS`.
- Shortage semantics: `REFERENCE_CONSENSUS` on lost sales.
- Event timing: `SKILL_STRENGTH`. The blind run is the only analysis that states the intra-cycle
  order; the references are `EVENT_ORDER_UNSPECIFIED`.
- State completeness: `REFERENCE_CONSENSUS`.
