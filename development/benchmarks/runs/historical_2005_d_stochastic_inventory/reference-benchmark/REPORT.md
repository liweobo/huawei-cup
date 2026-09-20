# 2005D Post-hoc Excellent-Solution Benchmark

Benchmark: `historical_2005_d_stochastic_inventory`
Blind run under comparison: `../run-001/` (frozen, unmodified)
Protocol regression: `../run-002-protocol-order/` (frozen, unmodified)
Reference set: [2005 excellent papers, D](https://github.com/zhanwen/MathModel/tree/master/国赛论文/2005年优秀论文/D), 3 papers

## 1. Purpose and separation

This stage compares the frozen blind run against three excellent papers for 2005D and asks whether
any genuine generalizable stochastic modeling gap remains. `skill/` was not modified. The blind
run and its protocol regression were read only. Reference assumptions were never written back
into the problem facts, and no paper's answer was treated as ground truth.

`current-skill-solution.md` was written and frozen before any reference text was opened.

## 2. Source provenance

All three PDFs were downloaded from the authorized directory only:

| id | title | pages | Git blob SHA | SHA256 (first 16) | extraction | award |
|---|---|---:|---|---|---|---|
| R1 | 仓库容量有限条件下的随机存贮管理 | 19 | `5a8eb88d…` | `ae14eee4ff98f1b8` | full, 19/19 non-empty | UNKNOWN |
| R2 | 仓库容量有限条件下的随机存贮管理问题 | 29 | `a0637430…` | `68e9c590bf040956` | full, 29/29 non-empty | UNKNOWN |
| R3 | 仓库容量有限条件下的随机存贮管理 | 9 | `1ff6fd39…` | `fc8fe7f8f2f4da7a` | full, 9/9 non-empty | UNKNOWN |

No PDF carries author metadata and no author is named in the body text, so authorship is
`NOT_STATED`. Directory membership in the "excellent papers" collection does not establish a
prize level, so `award_level: UNKNOWN` and `award_verified: false` for all three. Details in
`source-ledger.md`. Titles, abstracts and reported values were visually verified against rendered
page images.

## 3. Comparison chain

Eleven dimensions were compared, each in its own file:

`problem-interpretation-comparison.md`, `distribution-comparison.md`,
`state-event-comparison.md`, `cost-comparison.md`, `q1-q2-comparison.md`,
`q3-q4-comparison.md`, `q5-comparison.md`, `simulation-protocol-comparison.md`,
`uncertainty-comparison.md`, `policy-evaluation-comparison.md`, plus
`reference-consensus.md` and `reference-weaknesses.md`.

## 4. Lead-time modeling (Q1-Q2)

R1 fits a **Normal** to all three products. R2 runs **K-S tests** against Normal, Uniform and
Exponential, rejects all three at p <= 0.001, and adopts the **empirical frequency table**. R3 fits
a **Lorentzian** for product 1 and uses empirical probabilities elsewhere.

The blind run uses the empirical PMF and refuses to invent a family, which matches R2's conclusion
reached independently and with an explicit test. Re-running the frozen run-001 cost function with
only the law swapped shows the choice is not cosmetic: product 1's optimum moves from `L = 36`
under the empirical law to `L = 48` under a discretized Normal, and the Normal-optimal point
costs more under the empirical law than the empirical optimum does (3.5312 versus 3.4797 per day).

Classification: `REFERENCE_CONSENSUS` with R2, `SKILL_STRENGTH` against R1 and R3.

## 5. Renewal and long-run cost

The blind run states the renewal-reward structure and reports `E[cycle cost] / E[cycle days]`.
None of the references establishes a long-run rate. R1 additionally reduces the expectation to
`X = E[X]`, which is invalid for a nonlinear cost, though it happens to return the same integer
optimum on this data (verified). R2 computes `E[f(L,X)]` correctly and is therefore right for a
reason it does not give. R3 minimises an expected per-cycle average without justification.

Classification: `SKILL_STRENGTH`; the reference gaps are recorded as weaknesses.

## 6. Is simulation necessary?

None of the three references simulates; all use closed-form or deterministic-search methods. That
is the correct choice for this problem. The blind run also treats the analytic renewal-reward
result as primary and uses its simulator only as an independent cross-check. Simulating was not
assumed to be required merely because the problem is stochastic.

Classification: `SKILL_STRENGTH` for analytic-before-simulation and for the independent
cross-check; the decision to simulate at all is consistent with reference practice and is not
scored as a difference.

## 7. State definition

All four analyses carry the same essential state: on-hand inventory, the own/rented split at
`Q0`, an outstanding-order notion, the lead time, and the rented overflow. No reference omits a
state the blind run needed, and none carries a backorder state. Classification:
`REFERENCE_CONSENSUS`.

## 8. Event timing

All three references are `EVENT_ORDER_UNSPECIFIED`: none states whether the delivery-instant
receipt precedes or follows demand and cost accumulation. The blind run states the order
explicitly and demonstrates with a one-unit example that reversing it changes fulfilled, lost and
ending-inventory values, then verifies its own implementation follows the stated order.
Classification: `SKILL_STRENGTH`.

## 9. Capacity semantics

Full agreement and agreement with the source: `Q0` is a hard own-storage cap, all excess goes to
rented storage at `c3`, and nothing is truncated, rejected or discarded. No analysis clips
inventory silently. Classification: `REFERENCE_CONSENSUS`.

## 10. Shortage semantics

All four read shortages as lost sales. R2 and R3 include a duration term in the cost; R1 charges a
per-unit amount. The blind run is the only analysis that preserves the source's `c4` unit conflict
explicitly and runs both readings. Under the frozen cost function the readings give different
optima, product 1 moving between `L = 36` and `L = 45`. Classification:
`REFERENCE_CONSENSUS` on lost sales, `SKILL_STRENGTH` on the unit conflict.

## 11. Cost accounting

All four aggregate a fixed order fee, own holding, rented holding and a shortage charge, and all
are algebraically reconstructable. Only the blind run reports a component-level audit (max
component error `1.8e-15`) and checks unit homogeneity before adding. No reference provides a cost
ledger or notes the `c4` discrepancy. Classification: `REFERENCE_CONSENSUS` on structure,
`SKILL_STRENGTH` on the audit.

## 12. Q3-Q4 joint inventory

All four order jointly with a shared own volume and arrival target and no cross-item transfers.
Solution methods differ (Lingo NLP, staged exhaustive search, 6^m state enumeration, bounded
multistart), which is a `REFERENCE_DIFFERENCE_ONLY` and not a capability gap. Reported Q4 numbers
are `NOT_DIRECTLY_COMPARABLE` because the allocation conventions differ: R2's per-item targets sum
to roughly 100 against a 10 m3 total, so its 17.494 objective is not on the same basis as the
blind run's 8.0483. The blind run's own allocations sum to exactly 6.0 and 10.0 and are audited.
Classification: `REFERENCE_CONSENSUS` on structure, `SKILL_STRENGTH` on optimality qualification.

## 13. Uniform(1,3) interpretation

R1 uses the continuous uniform. R2 states that arrival times are integers and uses a discrete
uniform on {1,2,3}. R3 uses six arrival-time state intervals. The references split, so the honest
label is `MIXED_REFERENCES`, and the blind run's decision to carry both readings is the
appropriate response.

## 14. Q5 interpretation

Q5 supplies no data. R1 introduces a continuous demand law and derives EOQ-style formulas without
labelling the law as an author choice. R2 explicitly cautions that the framework needs real
problem data and claims no numeric optimum. R3 writes a joint density and stops at the framework.
The blind run fully declares its scenario numbers, labels the demand law `SCENARIO`, fixes a
finite horizon and reports a scenario comparison rather than an optimum. Classification:
`SKILL_STRENGTH`, with `REFERENCE_CONSENSUS` on R2's caution.

## 15. Replication unit

The blind run's independent unit is one complete regenerative trajectory, never a single period.
No reference simulates, so no reference can commit a period-as-iid error in an interval. R2's K-S
test does assume exchangeability of the 61 delivery observations; product 3's lag-1
autocorrelation is near 0.47, so that premise is doubtful, but R2 uses the empirical table anyway
and the effect is bounded by the blind run's block-resampling sensitivity. Classification:
`SKILL_STRENGTH`, with a recorded `REFERENCE_UNCERTAINTY_WEAKNESS` in R2's test.

## 16. Monte Carlo uncertainty

The blind run reports replications, standard errors, intervals and seeds for every simulated
estimate, and checks horizon (512/1024) and replication (128/256) convergence. No reference
reports any uncertainty on any estimate. Classification: `SKILL_STRENGTH`.

## 17. Serial dependence

The blind run addresses within-path dependence through the replication unit and lead-sample
dependence through a circular block-resampling sensitivity (product 3, block length 4, 256
replications: 11.3586, CI [11.3321, 11.3852], overlapping the iid and analytic values). No
reference addresses either. Classification: `SKILL_STRENGTH`; the standard was not lowered
because the references omitted it.

## 18. Warm-up and steady state

The blind run needs no arbitrary burn-in for Q1-Q4 because each arrival regenerates the same
post-arrival state, and it keeps Q5 as a finite horizon with no period deleted. No reference
claims steady state, and none uses burn-in. Classification: consistent and correct; not a
difference.

## 19. Horizon and replication convergence

The blind run reports both. No reference reports either. Classification: `SKILL_STRENGTH`.

## 20. Policy search versus evaluation

None of the references searches stochastically, because each optimisation is deterministic given a
fixed law, so the search/evaluation reuse risk does not arise for them and no reference weakness is
charged. The blind run also solves Q1-Q4 deterministically; for Q5, where it does simulate, it
separates search draws from evaluation draws and uses common random numbers. Classification:
`SKILL_STRENGTH`.

## 21. Common random numbers and difference uncertainty

The blind run pairs policies on common random numbers and reports difference intervals (joint
primary minus baseline `-2.7434`, CI [-2.7627, -2.7240]; Q5 adaptive minus static `-0.4724`,
CI [-0.6207, -0.3241]). No reference reports a policy difference at all. Classification:
`SKILL_STRENGTH`.

## 22. Service metrics

The blind run defines stockout probability and fill rate separately and never merges them. No
reference defines any service metric. Classification: `SKILL_STRENGTH`; the absence is a
`REFERENCE_WEAKNESS`.

## 23. Boundary optimum

The blind run distinguishes product 3's unconstrained cost infimum approaching `L = 40` from the
admissible integer optimum `L = 39`, and warns against rounding `L` to `Q` while preserving the
same stockout probability. All three references report rounded integers without distinguishing an
attained optimum from an infimum. Classification: `SKILL_STRENGTH`.

## 24. Analytical small-case validation

The blind run uses hand-computed single-cycle costs, zero-lead and long-lead cases, exact
enumeration and a finite-day oracle. No reference reports any small-case check. Classification:
`SKILL_STRENGTH`.

## 25. Distribution-assumption sensitivity

The blind run carries both the continuous and discrete Q4 uniform readings and a lead-dependence
sensitivity. No reference varies its distribution family or checks empirical-versus-parametric
sensitivity; each commits to one law. The absence is a `REFERENCE_WEAKNESS`.

## 26. Numerical comparability

Direct numeric comparison requires the same shortage semantics, `c4` unit interpretation,
lead-time distribution, joint-allocation convention and objective. No reference satisfies all five
against the blind run simultaneously, so the product-level values are
`NOT_DIRECTLY_COMPARABLE`. The one defensible agreement is that the blind run and R2 match exactly
on products 1 and 2, both using the empirical law.

## 27. Reference weaknesses found

Recorded in `reference-weaknesses.md`: hidden parametric assumptions (R1, R3); a mean-field
reduction of a nonlinear expectation (R1); no event timing (all three); no uncertainty (all
three); an iid premise in the K-S test (R2); no convergence checks (all three); no cost-unit audit
and silent resolution of the `c4` conflict (all three); shortage semantics left partly implicit
(all three); unsupported optimality claims (R1, R3); and no boundary-versus-interior distinction
(all three). The absence of Monte Carlo is explicitly not counted as a weakness.

## 28. Skill strengths confirmed

Distribution provenance; no invented parametric law; explicit state and event semantics;
conservation; hard capacity; cost reconstruction; analytic before simulation; independent
simulator cross-check; independent-trajectory uncertainty; CRN paired comparison; search and
evaluation separation; horizon and replication convergence; sensitivity; source-ambiguity
preservation; and no unsupported global optimum.

## 29. Gap classification

Every candidate considered (`STOCHASTIC_INPUT_PROVENANCE_GATE`,
`SERVICE_METRIC_DEFINITION_GATE`, `STOCHASTIC_SIMULATION_EVIDENCE_CONTRACT`,
`RANDOM_STREAM_AND_POLICY_COMPARISON_CONTRACT`, `STEADY_STATE_AND_REGENERATIVE_VALIDATION`) fails
the first G1 condition, because the blind run already performed each of these correctly without
any Skill change or run-local workaround. None receives reference support either, since the
references are deterministic and omit uncertainty entirely. The one real runtime defect this
problem exposed, `ORDERED_PROTOCOL_NORMALIZATION_FALSE_NEGATIVE`, was not a stochastic modeling
gap and is already fixed and verified.

TOP-1 generalizable gap: `NONE`.

## 30. Skill level

| dimension | level | basis |
|---|---|---|
| STOCHASTIC_FORMULATION | STRONG | renewal-reward with exact ratio-of-expectations, verified against a simulator |
| DISTRIBUTION_PROVENANCE | STRONG | five-way provenance tags, no invented family, preserves the c4 conflict |
| STATE_TRANSITION_DISCIPLINE | STRONG | explicit state, explicit event order, conservation to 1e-15 |
| ANALYTIC_VS_SIMULATION_SELECTION | STRONG | analytic primary, simulation as cross-check, matching reference practice |
| MONTE_CARLO_UNCERTAINTY | STRONG | mean, SE, CI, seed, replication unit and convergence all reported |
| DEPENDENCE_HANDLING | ADEQUATE | block resampling on product 3 and trajectory-level SE, but no general dependence contract |
| POLICY_EVALUATION | STRONG | CRN paired differences with intervals, search/evaluation separation |
| SOLUTION_QUALITY | STRONG | results consistent with the best reference under the same empirical law |
| OVERALL | STRONG | no material generalizable gap found for this problem family |

`DEPENDENCE_HANDLING` is marked `ADEQUATE` rather than `STRONG` because this run addressed
serial dependence with a targeted, run-local block-resampling check rather than through a
declared general mechanism. That observation does not meet the G1 bar, since condition 1 requires
the Skill to lack the capability and the blind run demonstrably had it available, but it is the
closest thing to a future improvement and is recorded here for honesty.

## 31. Final decision

`A. NO_MAJOR_GENERALIZABLE_GAP`.

The 2005D blind run handled stochastic simulation and policy evaluation well, the excellent papers
did not expose any major general capability worth adding immediately, and the comparison instead
confirms the blind run's choices on distributions, timing, cost units, uncertainty and policy
comparison.

## 32. Historical integrity

`skill/` unmodified. `../run-001/` unmodified. `../run-002-protocol-order/` unmodified. The 2020A,
2011B, 2022C, 2023E and 2024C frozen assets unmodified. Reference PDFs, extracted text and rendered
images are untracked. Known pre-existing repository issues were left untouched:
`DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING` with `.tmp/github-publish-checkout`, the frozen 2020A
smoke duplicate, and the existing untracked historical artifacts.
