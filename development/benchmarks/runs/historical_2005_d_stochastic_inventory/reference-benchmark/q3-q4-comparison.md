# Q3-Q4 Joint Inventory Comparison

## Joint model structure

| aspect | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Simultaneous ordering | yes, common arrival | yes | yes | yes |
| Common lead time X | yes, one X for all items | yes | yes | yes |
| Own-storage allocation | reserved volumes `a_i`, `sum a_i = Q0` | `Q0_i`, `sum Q0_i = Q0` | `Q0_i`, `sum Q0_i = Q0` | `Q0_i`, `sum Q0_i = Q0` |
| Arrival target | `b_i`, `sum b_i = Q` | `Q_i`, `sum Q_i = Q` | `Q_i`, `sum Q_i = Q` | `Q_i`, `sum Q_i = Q` |
| Capacity coupling | via volume shares, ordered own-first | via case split per item | via case split per item | via six arrival-time states per item |
| Cross-item transfer | not modeled | not modeled | not modeled | not modeled |
| Objective | `E[total cycle cost] / E[cycle days]` | `min Σ E[loss_i]` | `min Σ E[f_i(L_i,X)]` | `min Σ E[Y_i(L,X)]` over state combinations |

All four share the same coupling idea: items are ordered together, arrive together, and must
share one own-warehouse volume `Q0` and one arrival target `Q`. No analysis permits cross-item
transfers. This is `REFERENCE_CONSENSUS`.

## Solution methods

| aspect | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Allocation search | gradient-free multistart over a bounded feasible region with the policies re-evaluated | Lingo NLP for allocation, then Lingo for order point | staged exhaustive search, step 1 then 0.1 then 0.01 | 6^m state enumeration, then per-state Matlab optimisation |
| Order-point search | continuous piecewise minimisation plus integer enumeration | Lingo | exhaustive integer `L` | Matlab iteration per state |
| Feasibility enforced | yes, hard constraints, infeasible policies rejected | yes | yes | yes |
| Search/evaluation separation | yes, separate draws | not applicable (deterministic search) | not applicable | not applicable |
| Optimality claim | "best found under the declared model", with the boundary case flagged | "optimal" | "global optimum" for Q2, approximate for Q4 | "optimal" |

R2 explicitly claims a global optimum for Q2 and an approximate global optimum with error under
0.01 for Q4, and it is honest about the stepwise search's error radius. R1 and R3 state optimality
without qualification. None of the three distinguishes an interior optimum from an infimum on an
open boundary.

## Reported Q4 results

| quantity | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| `L*` | 8.7288 | 6.240 m3 | 7.3333 | 7.8 |
| own allocation `Q0_i` | 1.179 / 1.332 / 3.489 | 3.123 / 0.49 / 2.628 m3 (order-time residual) | 10.27 / 10.68 / 30.05 | 3 / 3 / 0 |
| arrival target `Q_i` | 1.958 / 1.956 / 6.086 | 3.828 / 1.195 / 4.978 m3 (allocation model) | 21.05 / 22.30 / 56.65 | 3 / 3 / 4 |
| cost/day | 8.0483 | not reported as a rate | 17.494 | 3.1513 |

These are `NOT_DIRECTLY_COMPARABLE`. R2 reports a cost of 17.494 that is not on the same basis as
the blind run's 8.0483: R2's `Q_i` values sum to about 100 m3 against an arrival target of 10 m3,
so its allocation is on a different normalisation, and its `Q0_i` sum to about 51 against an own
capacity of 6. R3's 3.1513 is the minimal objective among its enumerated state combinations and
uses yet another convention. R1 reports a residual at the order instant rather than a stored
allocation.

The blind run's `Q0_i` sum to 6.0 and its `Q_i` sum to 10.0, and it verifies this in
`validation/final-model-audit.json`. That internal consistency is the property the other reports
cannot be cross-checked on without their full conventions.

## Classification

- Joint structure and capacity coupling: `REFERENCE_CONSENSUS`.
- Allocation convention (reserved vs residual): `REFERENCE_DIFFERENCE_ONLY`. The papers differ in
  what they report, and no single convention is established by the source.
- Search method: `REFERENCE_DIFFERENCE_ONLY`. Different optimisers on a similar objective are not
  a capability gap; the blind run does not need to copy Lingo or staged enumeration.
- Optimality qualification and boundary handling: `SKILL_STRENGTH`. The blind run labels its Q4
  answer as best-found-under-model and flags the product 3 open-boundary infimum, which no
  reference does.
