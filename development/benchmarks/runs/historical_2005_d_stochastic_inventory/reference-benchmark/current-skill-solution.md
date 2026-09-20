# Current Skill Solution (frozen before reading references)

This file freezes what the blind run produced. It was written before any excellent-paper
text was read, and nothing in it is revised from reference material. Authoritative detail
lives in `../run-001/`.

## Method

Problem family: stochastic inventory with a capacity-limited warehouse. The Skill treated
Q1-Q4 as a regenerative renewal-reward process and computed the long-run expected cost per
calendar day in closed form, using `E[cycle cost] / E[cycle days]`. Q5, whose source text
declares no demand law and an environment change, was modeled as an explicitly declared
finite-horizon (120-day) scenario rather than a solved stochastic optimum.

An independent event-path simulator advances event to event with exact interval integration
of demand and holding. Its role is verification of the analytic result, not production of the
headline numbers. A tiny deterministic state space, hand-computed single-cycle costs, and a
finite-day oracle were used as small-case checks.

## Stochastic primitives and provenance

- Q1 lead time: no distribution is given by the source. Handled parametrically; no invented family.
- Q2 lead time: the 36/43/61 ordered delivery-time observations are used as an empirical PMF.
  Whether the samples are iid or stationary is recorded as an unprovable assumption, not a fact.
- Q4 lead time: `Uniform(1,3)` is given, but continuous vs integer-valued is not stated, so both
  readings are retained (continuous as primary, discrete as an alternative scenario).
- Q5 demand: a fully declared scenario law, explicitly not an empirical estimate.

No mean or range was silently upgraded to Normal, Poisson or Exponential. Every law carries a
`GIVEN` / `DERIVED` / `ESTIMATED` / `ASSUMED` / `SCENARIO` tag.

## State, timing, capacity, shortage

State: on-hand inventory, the own/rented split at Q0, an outstanding-order flag, and elapsed
time since review. No backorder state exists, because shortages are lost.

Event timing (explicit assumption, source does not state it): integrate demand and holding over
the open interval, then receive and top up at the arrival instant, then review and order. A
receipt at a shared timestamp precedes the review at that timestamp.

Capacity is hard: own storage holds at most Q0 and all excess goes to rented storage at c3.
Nothing is clipped, rejected or discarded. Shortage is lost-sales: unmet demand is never served
later. The source's `c4` unit conflict (per lost item vs per box-day vs per volume-day) is
preserved and both readings are run rather than silently resolved.

## Results (as reported by the blind run)

| Quantity | Value |
|---|---|
| Product 1 optimal L, cost/day | 36, 3.4797 |
| Product 2 optimal L, cost/day | 45, 4.8754 |
| Product 3 integer-optimal L, cost/day | 39 (unconstrained infimum approaches 40, not attained), 11.4419 |
| Q4 joint L*, cost/day | 8.7288, 8.0483 (simulated CI [8.0447, 8.0555]) |
| Q4 baseline cost/day | 10.7979 |
| Q5 static vs adaptive cost/day | 13.3559 vs 12.8835 |
| Q5 paired difference | -0.4724, CI [-0.6207, -0.3241] (`CLEAR_POLICY_ADVANTAGE`) |

Roughly: joints beat the static baseline by `-2.7434` (CI [-2.7627, -2.7240]).

## Evidence level

Every simulated figure carries a mean, a standard error and a 95% interval computed across
independent complete trajectories, never across individual periods. Horizon (512/1024 cycles)
and replication (128/256) refinements were run. Search draws were separated from evaluation
draws, and policy comparisons used common random numbers with paired differences. A circular
block-resampling sensitivity addressed serial dependence in product 3's leads. Every experiment
asserted per-interval conservation, capacity nonviolation and nonnegativity.

Status: `final_result_status: VALID`, with `distribution_provenance`, `state_transition_audit`,
`inventory_conservation`, `cost_accounting` and `monte_carlo_uncertainty` all PASS.

## Known limits frozen at this point

The source's `c4` unit conflict has no unique resolution. Q2's lead samples are short and their
population law is unknown. Q4's uniform interpretation is not pinned down by the source. Q5 is
entirely scenario-driven. Product 3's optimum sits on an open boundary.
