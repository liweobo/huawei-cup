# 2005D Sixth-Problem Blind Run

Benchmark ID: `historical_2005_d_stochastic_inventory`
Problem: 2005 年中国研究生数学建模竞赛 D 题《仓库容量有限条件下的随机存贮模型》
Family: `STOCHASTIC_SIMULATION_AND_POLICY_EVALUATION`
Run: `run-001`

## 1. Source Provenance

Only the authorized source tree `zhanwen/MathModel`, path `国赛试题/2005年研究生数学建模竞赛试题`, was accessed. One target file:

- file: `仓库容量有限条件下的随机存贮模型（D）.doc`
- git blob SHA: `cc7540cbfa71e42d5a8809e933a3856e3c924197` (matches the declared blob)
- SHA256: `164ec41eb17115f9ae7c64a0f0c7244759353c82e29e498f98f091c0ce88565d`
- size: 110080 bytes
- URL recorded in `source-provenance/source.json`
- original file retained at `source-provenance/仓库容量有限条件下的随机存贮模型（D）.doc`

Extraction. The legacy `.doc` was decoded through its OLE piece table (`body-piece-table.txt`), which recovered the running text without interpreting the binary format as text. All 76 equation objects were rendered to independent previews and visually inspected, then bound to their in-text positions through the Word CHPX/PICF offsets rather than assumed ordering (`equation-mapping.json`), and transcribed (`equations.json`, `problem-transcription.txt`).

Extraction quality. Body text, equations and tables are `RELIABLE`. The only `EXTRACTION_UNVERIFIED` item is document page layout, which carries no modeling content. No external attachment references exist and no numeric table was left unmapped. The three Q2 delivery-time lists were independently recounted as 36, 43 and 61 rows, matching the transcription. A Word COM conversion was attempted and failed with `REGDB_E_CLASSNOTREG (0x80040154)`; that is an environment limitation, and the piece-table route is not dependent on it.

## 2. Problem Facts

`problem-facts.md` separates `PROBLEM_GIVEN_FACT` from `MODELING_ASSUMPTION`, with each fact anchored to EQ locators.

Stochastic object: delivery lead time X, random and given no distribution in Q1; given only as 140 ordered observations across three products in Q2; given as uniform on [1,3] in Q4; unspecified for Q5.

Inventory objects: on-hand stock, own-storage quantity capped at Q0, rented overflow, an arrival that tops on-hand back up to the fixed target Q. Q1 is one item; Q2 is three separate single-item problems; Q3 and Q4 order jointly with a common arrival.

Warehouse capacity: own capacity Q0 and the arrival target Q with Q0 < Q. Overflow is explicitly held in rented space at c3, which makes capacity a cost boundary rather than a truncation.

Time unit: days. Demand/arrival mechanism: continuous depletion at a constant known rate with a random replenishment delay. Replenishment rule: order when stock falls to the reorder point L, arrival restores on-hand to Q. Costs: fixed order fee c1, own holding c2, rented holding c3, shortage loss c4. Service requirement: none stated; the objective is cost minimization. Decision variables: reorder point L (Q1, Q2), plus own-storage allocation and arrival targets (Q3, Q4). Initial condition: not specified. Subproblems are Q1-Q5 exactly as enumerated in `problem-facts.md`.

Every probability distribution the source actually states is recorded there; nothing beyond the source is promoted into a given fact.

## 3. Stochastic Primitive Ledger

`stochastic-ledger.md` records, for each random quantity: name, meaning, support, distribution, parameters, source, iid-or-dependent, time dependence, correlation, observed-or-assumed, and sampling method.

The two primitives are the lead time X for each product (Q1: unspecified law; Q2: 140 observed durations with support {0..7}, {1..5}, {1..6}; Q4: uniform on [1,3]) and the Q5 demand process (unspecified in-source, supplied only as declared scenario inputs).

The ledger does not upgrade a mean, a range or an empirical description into a full parametric distribution. Where the source states only an interval, the ledger records an interval; where it states an empirical sample, the ledger records the sample. No Normal, Poisson or Exponential law was attached to any quantity.

## 4. Distribution Provenance

Every law used in a formal result is tagged `GIVEN`, `DERIVED`, `ESTIMATED`, `ASSUMED` or `SCENARIO` in `stochastic-ledger.md` and `mechanism-closure.yaml`.

- Q4 common lead time `Uniform(1,3)`: `GIVEN` for the family; the continuous reading is `ASSUMED` because the source does not say continuous or integer-valued, and the discrete alternative `{1,2,3}` is run separately.
- Q2 per-product lead time law: `ESTIMATED` as the empirical PMF, the minimally parametric choice. The ledger records that short consecutive samples do not prove iid or stationarity.
- Q1 lead time law: no value is available. The Q1 analysis is therefore reported as a parametric function of the lead time, and the single-item numbers use the Q2 empirical laws where the products match.
- Q5 demand: `SCENARIO`, a fully declared two-point multiplier law, explicitly not an empirical estimate.

For each `ASSUMED` law the ledger names the chosen family, the reason, the alternative that was tried, and whether the conclusion moved. `results/sensitivity.json` and `validation/dependent-lead-sensitivity.json` show the main policy conclusions are stable under the checked alternatives. No distribution was selected merely to enable Monte Carlo.

## 5. State / Event Model

`model.md` fixes the state, decision, randomness, transition, cost, constraint and terminal objects.

State: on-hand inventory I, the own/rented split at Q0, whether an order is outstanding, and the elapsed time since the last review. Because the source fixes the arrival quantity at receipt to reach Q, there is no pending-quantity state to track beyond the outstanding flag. There is no backorder state, because shortages are lost in the primary reading.

Decision / policy: the reorder point L (threshold on on-hand stock), and for the joint problems the reserved own volumes `a_i` and arrival targets `b_i`.

Random input: the lead time of the outstanding order.

Transition: stock depletes continuously at rate r; on crossing L an order is placed; at the arrival instant on-hand is raised to Q with the excess held in rented space.

Cost / reward: order fee, own and rented holding, and shortage loss, integrated between events.

Constraint: nonnegative inventory, own occupancy at most Q0, total at most Q, one outstanding order.

Terminal / horizon: Q1-Q4 have no terminal date and use long-run expected cost per day; Q5 uses a declared finite 120-day scenario.

## 6. Event Timing

Within one cycle the implemented order is: integrate demand and holding over the open interval since the last event, then receive and top up at the arrival instant, then review and place an order. A receipt at a shared timestamp precedes the policy review at that timestamp.

This ordering is stated as a `MODELING_ASSUMPTION` in `assumptions.md`, because the source does not spell out the intra-instant sequence.

The choice matters. `validation/ordered-protocol-probe.json` contains a one-unit counterexample: with initial inventory 0, one unit of demand during the interval and a one-unit receipt at the interval end, integrating demand before the receipt gives `fulfilled=0, lost=1, end_inventory=1`, while moving the receipt before the interval gives `fulfilled=1, lost=0, end_inventory=0`. The two protocols are causally different, and the implemented order is the one that keeps demand and holding on the same open interval as the transition it belongs to.

## 7. Inventory Conservation

`simulation-code/inventory.py` carries a per-period conservation identity, and every reported experiment asserts it. For each interval the code accounts for beginning inventory, any receipt, fulfilled demand, lost demand and ending inventory, and it must reconcile to floating-point tolerance.

Observed maxima: `7.1e-15` for the Q1-Q4 single-product simulation, `3.6e-13` for the Q5 simulation, and `0.0` for the circular-block dependent-lead scenario. No run shows inventory appearing or disappearing. The `audit` blocks in `results/single.json`, `results/joint.json` and `results/q5.json` also report `capacity_violations: 0`, `nonnegative_violations: 0` and exactly one order and arrival per cycle. `validation/final-model-audit.json` confirms the total cost reconstructs from its components with a maximum component error of `1.8e-15`.

## 8. Capacity / Shortage Semantics

Capacity is a real, hard constraint. Own storage holds at most Q0, and any excess is placed in rented storage at c3 rather than being clipped, discarded or rejected. No code path silently truncates inventory to the warehouse size. The joint problems reserve static own volumes `a_i` with `sum a_i = Q0` and arrival targets `b_i` with `sum b_i = Q`, with no cross-item transfers. This allocation scheme is an explicit assumption, not a source fact.

Shortage semantics. The primary reading is lost sales: demand arriving with zero stock is lost and never served later, and no backorder state exists, so the model never writes `max(inventory - demand, 0)` without saying where the unmet demand went. The source contains a unit conflict for c4 (Q1 "per item lost", Q2 "元/盒.天", Q3 per volume per day). Rather than silently choosing one, `cost-ledger.md` labels this `SOURCE_UNIT_CONFLICT` and runs both an item-loss reading and a duration-exposure reading. Neither reading converts lost demand into a delayed delivery.

## 9. Cost Model

`cost-ledger.md` lists each cost with its formula, unit, timing and source, and the totals reconstruct from components.

Components: ordering (fixed c1 per order, charged at order placement), own holding (`c2 * I_own * dt`), rented holding (`c3 * I_rented * dt`), shortage loss (primary: c4 per lost item; alternative: cumulative exposure penalty), and no purchase price or disposal cost because the source gives none. All monetary values are yuan, all rates are per day, and inventory units are per item or per m³ with the volume conversion applied only where the source supplies unit volumes. Units are never added across incompatible bases; the Q2 and Q3 volume-based shortage units are handled as their own scenario rather than mixed into the per-item ledger.

The Q1-Q4 objective is long-run expected cost per day computed as `E[cycle cost] / E[cycle days]`; Q5 reports a finite-horizon mean. `E[cost] / E[days]` is never substituted for `E[cost/days]`.

## 10. Baseline

The baseline is the simplest legal policy, a static myopic rule that uses the expected lead time in a deterministic-demand approximation to place L, with a fixed own/rented split at the stated capacities. It is genuinely executed, not sketched: `results/single.json` and `results/joint.json` hold its exact cost per day and its simulated cost per day.

For product 1 the baseline gives L = 35.67 and cost/day 3.5047; for product 2, L = 38.02 and cost/day 5.4294; for product 3, L = 39.02 and cost/day 11.4406. The joint baseline gives cost/day 10.7979. Each baseline satisfies the capacity and nonnegativity checks.

## 11. Primary Stochastic Model

The primary object is a regenerative renewal-reward inventory process, evaluated in closed form for Q1-Q4, with an independent event-path simulation as the cross-check rather than as the primary source of numbers. For Q5, where the environment changes over time, the primary analysis is a finite-horizon simulation.

Analytic construction. Between arrivals the process is deterministic given the lead draw, so cycle cost and cycle length can be integrated exactly for a given lead time, and the cycle expectation is a finite sum over the empirical lead PMF. The long-run cost is the ratio of expected cycle cost to expected cycle days. The joint problems additionally search the reserved own volumes and arrival targets under the volume constraints.

Because a closed form exists for Q1-Q4, Monte Carlo is not the default. The simulator's role is to reproduce the analytic values through an independent path mechanism, and it does: see the convergence blocks, where the simulated cost/day converges to the analytic value as the replication count rises, with residual bias shrinking from roughly `-0.006` to `-0.0003`.

Primary policies found: product 1 L* = 36 with cost/day 3.4797; product 2 L* = 45 with cost/day 4.8754; product 3 integer-optimal L* = 39 with cost/day 11.4419 (the unconstrained infimum approaches L = 40 from below without attaining it, discussed in §18); joint policy with L* = 8.7288 and cost/day 8.0483.

## 12. Simulation Protocol

A replication is one complete regenerative inventory trajectory over a declared number of cycles N, and the reported estimator is that path's cost per day. A replication is never a single period: the T periods inside a path are not treated as independent samples.

The simulator advances event to event using exact interval integration for demand and holding, so there is no fixed-step discretization error in the state transition. At each arrival it tops on-hand to Q, holds overflow in rented space, and asserts the conservation and capacity identities before recording the path. The Q1-Q4 paths are regenerative because each receipt returns the system to the same post-arrival state with no outstanding order, so no warm-up deletion is used and none is needed. The Q5 simulation runs a finite horizon with every day retained.

## 13. RNG / Replications

Random-number provenance is recorded in `results/environment.json`: Python 3.12.10, NumPy 2.5.2, SciPy 1.18.1, RNG `numpy.Generator(PCG64)`, master seed `20260920`.

Stream policy: independent streams are drawn from a `SeedSequence` so that different policies and different experiments do not share a raw sequential stream. Within a policy comparison, the same scenario draws are bound across policies by common random numbers, so a paired difference is computed on identical lead-time realizations.

Replication counts: 128 and 256 independent replications for the presented single- and joint-product tables, with 512 and 1024 cycles per path used to separate the path-length effect from the replication-count effect. The Q5 comparison uses 256 replications of a 120-day horizon per policy.

## 14. Monte Carlo Uncertainty

Every simulation number is reported with a mean, a standard error and a 95% interval; a bare mean is never presented. For example, the joint primary policy reports mean 8.0501 with SE 0.0028 and CI [8.0447, 8.0555], and the analytic value 8.0483 sits inside that interval.

Standard errors are computed across independent replications, one scalar per complete trajectory, which is the correct unit given the within-path serial dependence. The number of independent replications is stated next to each estimate, and the seed policy is fixed and recorded so the reported intervals are reproducible.

## 15. Horizon / Warm-up

The finite-horizon versus steady-state question was resolved before simulating. Q1-Q4 ask for a repeated ordering policy with no terminal date, so the target is the long-run cost rate. That target motivates the renewal-reward formulation, which averages over regenerative cycles rather than over an arbitrary window.

Q5 is stated as an environment that changes after some time, so it is modeled as an explicitly finite 120-day scenario. No early periods are deleted from Q5. The report never labels a long simulation as steady state; the long-run claim for Q1-Q4 rests on the regenerative structure, not on run length.

## 16. Convergence

Two convergence checks are recorded. Horizon refinement: for each policy the path length was run at N = 512 and N = 1024 cycles, and the deviation from the analytic value is small and consistent at both lengths, with no material change to the reported decision variables. Replication refinement: the estimate and its standard error are reported at R = 128 and R = 256, and both the single-product and joint results hold their value within the stated interval, with SE scaling down as expected when R doubles.

No claimed steady-state average is supported only by runtime. The residual ratio bias from estimating `E[cost]/E[days]` by a ratio of path means is visible as the small negative bias at R = 128 and shrinks at R = 256, which is reported rather than hidden.

## 17. Policy Comparison

Policy searches used separate draws from the evaluation draws, and each comparison reports a paired difference with its own interval.

Single- and joint-product comparisons: the primary policy beats the baseline and the paired intervals exclude zero. The joint comparison gives a paired difference of `-2.7434` with SE `0.0098` and CI `[-2.7627, -2.7240]`, which is large relative to its uncertainty, so the advantage is real within the model.

Q5 comparison: static versus an adaptive threshold. The paired difference is `-0.4724` with SE `0.0753` and CI `[-0.6207, -0.3241]`, reported as `CLEAR_POLICY_ADVANTAGE`. The interval excludes zero, so this is not a case of a tiny mean difference hiding inside noise.

Common random numbers were used for the pairwise differences, and the report states how the same random scenario is bound across policies. No policy is called best from a single seed; every advantage is stated with its replication count and interval, and where the difference is not resolvable the report is prepared to return `NO_CLEAR_POLICY_ADVANTAGE` instead of a winner.

## 18. Sensitivity

Only the parameters that drive the decision were perturbed.

- Shortage unit conflict: both the per-item and duration-exposure readings were computed, since the printed units disagree. This is the single largest source of result ambiguity and is kept visible rather than resolved silently.
- Lead-time dependence: `validation/dependent-lead-sensitivity.json` runs a circular-block resampling with block length 4 at R = 256, fixed at the empirical marginal. It gives cost 11.3586 with CI [11.3321, 11.3852], overlapping the iid result 11.3657 and the analytic 11.3647, so the main cost conclusion does not depend on the iid assumption. Product 3 shows lag-1 correlation near 0.47, which is exactly why this check exists.
- Q4 lead-time family: the discrete alternative `{1,2,3}` was run against the continuous reading. Service probability under the discrete case sits at a numerical support boundary and is labeled `ESTIMATE_UNSTABLE`; the tiny positive stockout value there is not interpreted as a reliable service probability.
- Capacity boundary: `validation/boundary-sensitivity.json` shows product 3's unconstrained optimum approaching L = 40 without attaining it, i.e. a cost infimum on an open boundary rather than an attained optimum. The admissible integer optimum is L = 39. The file explicitly warns against rounding L to Q and keeping the same stockout probability.

Scenario analysis and probabilistic expectation are kept separate: the three hand-chosen Q5 settings are scenario inputs and are never averaged into a number called expected cost. Only the Monte Carlo means over declared scenario laws are labeled as expectations.

## 19. Final Results

Single product (empirical Q2 lead laws, primary per-item shortage reading):

| Product | L* | cost/day | stockout prob | fill rate |
|---|---:|---:|---:|---:|
| 1 | 36 | 3.4797 | 0.2778 | 0.8994 |
| 2 | 45 | 4.8754 | 0.1395 | 0.9539 |
| 3 | 39 (integer-optimal; infimum at 40) | 11.4419 | 0.5574 | 0.7894 |

Joint policy with volumes `.05/.04/.10`, Q0 = 6, Q = 10, Uniform(1,3) lead: L* = 8.7288, cost/day 8.0483 (analytic) with simulated CI [8.0447, 8.0555], stockout probability 0.1770 and fill rate 0.9911. Baseline cost/day is 10.7979.

Q5 (declared 120-day scenario): static cost/day 13.3559, CI [13.1855, 13.5263]; adaptive cost/day 12.8835, CI [12.7406, 13.0264]; paired difference `-0.4724`, CI `[-0.6207, -0.3241]`, `CLEAR_POLICY_ADVANTAGE`. Q5 fill rate improves from 0.9054 to 0.9192.

Service metrics are defined distinctly: stockout probability is the fraction of cycles in which stock hits zero, and fill rate is the fraction of demand met. They are never merged into one figure.

Rare events: the Q1-Q4 stockout probabilities are not rare (0.14 to 0.56) and carry large event counts, so they are labeled `ADEQUATE_EVENT_COUNT`. The only `ESTIMATE_UNSTABLE` label is the discrete-uniform Q4 service probability, whose value sits at a support boundary.

## 20. Skill Strengths

The Skill held up on the parts of this problem that most often go wrong. The provenance guard refused an experiment record whose `protocol_change_disclosure` was missing required fields, which is a correct rejection of an authoring mistake in this run (`validation/attempt-001-record-failure.json`). The workspace and run-scoping contracts kept generated artifacts inside the active run. The problem-facts and mechanism-closure contracts forced every random law to declare whether it was given, derived, estimated, assumed or scenario, and that discipline is what kept the source's c4 unit conflict visible instead of silently resolved. The capacity and nonnegative assertions fired correctly across all reported experiments.

## 21. Skill Weaknesses

One real defect surfaced, and it is in the protocol-change guard.

`skill/scripts/runtime_provenance.py` defines `normalize_protocol` at line 51, and for any list it sorts the normalized elements (line 57). `protocols_differ` at line 63 compares two protocols through that normalization. Sorting a list discards the one thing that matters for an ordered protocol: the sequence. Two event protocols that differ only in execution order normalize to the same value, so `protocols_differ` returns `False` and the record is treated as unchanged.

`validation/ordered-protocol-probe.json` demonstrates it. The planned order is "integrate demand and holding", then "receive and top up at arrival", then "review/order". The changed order moves the receipt before the interval integration. `expected_protocol_changed` is true, `observed_protocol_changed` is false, and `validator_errors` is empty: the guard produced a false negative and reported no problem. The same file carries a concrete counterexample where the two orders give different fulfilled/lost/inventory outcomes, so the normalization is hiding a genuinely different process.

The practical impact on this problem is limited, because the production event order in `simulation-code/inventory.py` was verified directly and is correct. The impact on the Skill is not limited: the guard is supposed to be the mechanism that catches event-order changes, and for ordered protocols it is a silent pass.

## 22. First Meaningful Failure

`ORDERED_PROTOCOL_NORMALIZATION_FALSE_NEGATIVE`. The first real, general defect in the frozen Skill is that the protocol-change guard normalizes every list as unordered, so an ordered event protocol can be changed and still compare equal. The evidence is `validation/ordered-protocol-probe.json`, and the code location is `skill/scripts/runtime_provenance.py:51-65`.

## 23. Failure Classification

Level `P1`. The results of this run remain usable: the primary implementation's event order is correct and directly verified, so no reported number is invalidated. The failure is in the audit layer. It does not meet `P0` because it did not corrupt this run's conclusions, and it is more than `P2` because it defeats a guard whose entire purpose is to detect exactly this class of change. It is a defect that lets a wrong modification pass unnoticed rather than one that produces a wrong answer by itself.

## 24. Generalizable Gap Candidate

Candidate name: `ORDERED_PROTOCOL_NORMALIZATION_FALSE_NEGATIVE`.

The gap satisfies every condition for a generalizable finding. The Skill genuinely lacks it: `normalize_protocol` sorts lists, so ordering is lost. It affects 2005D, since this problem's correctness depends on ordering demand integration, receipt and review within a cycle. It is not inventory-specific: ordered event protocols appear wherever a process has a defined sequence, including queue discipline, reliability event ordering, discrete-event simulation, risk propagation and finance settlement order. It transfers directly to those families, because in each of them swapping two steps at the same timestamp changes the result. It is expressible as a lightweight principle: a protocol's list elements are ordered, and normalization may canonicalize maps but must preserve sequence for sequences. And it needs no simulation platform: preserving list order in a normalization function is a one-line contract change.

Recommended form: declare that recorded protocols may contain ordered stages, and that normalization must sort only map keys, never the elements of a stage list. Optionally allow an explicit unordered-set marker for the rare case where a list truly is a set.

## 25. Remaining Uncertainty

- Whether the Q2 empirical samples are iid or stationary is not provable from 36, 43 and 61 consecutive observations. The dependent-lead scenario bounds the effect on cost but does not settle the population law.
- Q1's lead-time distribution is not given, so Q1 numbers are conditional on the substituted empirical laws.
- The source's c4 unit conflict has no unique resolution; the item-loss and exposure readings are both retained, and if a policy ranking ever differed between them, no unconditional numerical answer would exist.
- Q4's uniform lead time may be continuous or integer-valued; the discrete reading pushes service estimation to a numerical boundary, labeled `ESTIMATE_UNSTABLE`.
- Q5's demand law, change date and observation mechanism are entirely scenario-supplied, so Q5 results are scenario results, not empirical estimates.
- Document page layout remains `EXTRACTION_UNVERIFIED`, with no modeling content at stake.

## 26. Historical Integrity

This run modified no Skill file and read no excellent-solution or answer material.

- Skill tree hash before and after: `0bd3abdc8f2efd115bf1c92813acb8947aadfcd0` (unchanged)
- `git status --porcelain -- skill`: empty
- source file SHA256 after the run: `164ec41eb17115f9ae7c64a0f0c7244759353c82e29e498f98f091c0ce88565d` (identical to before)
- frozen assets for 2011B, 2020A, 2022C and 2024C: no tracked diff, `frozen_assets_unmodified: true`

Snapshots: `validation/skill-integrity-after.json`, `validation/source-integrity-after.json`, `validation/historical-integrity-after.json`.

Test status. All harness checks were run under `validation/repository-checks.json`. Every routing, trigger, behavior-contract, trajectory, historical-artifact, postmortem, problem-facts and run-integrity check passed. Three checks returned non-zero and all three are pre-existing or self-inflicted in a known way:

- `default_pytest` exits 2 with 44 collection errors, all `import file mismatch` from `.tmp/github-publish-checkout`. This is the recorded `DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING` and was not repaired, per instruction.
- `smoke_test` exits 1 on duplicate long paragraphs between the frozen 2020A reference-benchmark work tree and the 2020A run tree. That untracked frozen artifact was not touched.
- `development_tests` reports 296 passed and 9 errors, all from this run's `--basetemp` being pointed inside `development/benchmarks`, which the harness correctly rejects. The failure is a misuse of the test invocation in this run, not a repository defect.

## 27. Final Decision

The run completed all five subproblems, produced analytic and simulated stochastic results with independently verified state, conservation, capacity and cost accounting, and identified one genuine, reproducible, generalizable defect in the frozen Skill.

Decision: `B. GENERALIZABLE_STOCHASTIC_MODELING_GAP_FOUND`.

TOP 1 GAP: `ORDERED_PROTOCOL_NORMALIZATION_FALSE_NEGATIVE` (`skill/scripts/runtime_provenance.py:51-65`), evidence in `validation/ordered-protocol-probe.json`. The Skill was not modified. No excellent solution was accessed. The run stops here pending human review.

```
SIXTH_PROBLEM_BLIND_RUN_COMPLETE
problem:
2005D 仓库容量有限条件下的随机存贮模型
problem_family:
STOCHASTIC_SIMULATION_AND_POLICY_EVALUATION
skill_modified:
false
excellent_solutions_accessed:
false
subproblems_completed:
5/5 (Q1-Q5; Q5 as declared scenario)
distribution_provenance:
PASS
state_transition_audit:
PASS
inventory_conservation:
PASS
cost_accounting:
PASS
monte_carlo_uncertainty:
PASS
serial_dependence_handled:
YES
horizon_convergence_checked:
YES
replication_convergence_checked:
YES
policy_evaluation_independent:
YES
final_result_status:
VALID
first_meaningful_failure:
ORDERED_PROTOCOL_NORMALIZATION_FALSE_NEGATIVE
failure_level:
P1
generalizable_gap_candidate:
ORDERED_PROTOCOL_NORMALIZATION_FALSE_NEGATIVE
recommended_next_action:
preserve list order in protocol normalization; do not auto-fix in this run
```
