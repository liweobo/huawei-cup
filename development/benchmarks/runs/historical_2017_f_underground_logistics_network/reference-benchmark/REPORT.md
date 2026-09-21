# 2017F Excellent-Solution Post-hoc Benchmark

## 1. Reference Set

All seven authorized PDFs were enumerated and fully reviewed: F10256001,
F10294003, F10486024, F10703002, F10710008, F90005027 and FK0263. All 354 pages
including appendices were read, with 33 targeted visual page checks. Full review
is not full numerical replication. [Source ledger](source-ledger.md) and
[paper notes](paper-reviews.md) preserve per-paper evidence.

## 2. Source Reliability

Pinned repository commit `cd5be91735ebf11d5ee52eb170e86a6d07131977`; all seven
PDFs match Git blobs and SHA256. They are reference-set members, not ground
truth. All award levels remain UNKNOWN;0 official award levels verified.
PDFs/extraction/renders are ignored and excluded from the commit.

## 3. Frozen Source-Complete Blind Run

HEAD before reference reading was
`33548fd4a53ec3b05d4fc0d19cb9cdc319e8a8bc`; Skill tree
`2b29e8ffa7c15d33bf81e675e8f1dcb240c226a6`.
[Current solution](current-skill-solution.md) was written before reference
methods and retains SHA256
`a31cbd4e4618c53eec75798bea32ab39c3c0c1eaf673c7f172c19236398535f1`.
Q1-Q4 remain PARTIAL; this post-hoc phase changes neither results nor assumptions.

## 4. Problem Interpretation

**MIXED_REFERENCES**:114 original endpoints are four parks and110 regions, not
pre-existing stations. Papers differ in underground share, OD direction,
diagonal freight, spatial aggregation and node-role counting. Source facts
remain authoritative. [Interpretation comparison](problem-interpretation-comparison.md).

## 5. Q1 Facility / Coverage Models

References use centre-based cover, moving circles, continuous weighted centres,
clustering and restricted candidate sets. Centre coverage is source-permitted;
centre-only siting is not source-mandated. No3km tunnel adjacency rule follows.
Run-002's110-centre coverage PASS remains valid within its assumptions.

## 6. Q1 Node Count / Hierarchy

Reference primary counts are4 in five papers,5 in one and8 in one; secondary
counts are mostly in the twenties, with two count/role ambiguities. All share
multiple secondary stations per primary. Run-002's118+118 and one-to-one pairing
are restrictive and expensive, not a minimal solution. This is predominantly
G5 model/search scope, not proof of a missing generic contract.
[Q1 comparison](q1-facility-comparison.md).

## 7. Freight Aggregation / Congestion

Run-002 conserves directed column-origin OD and3.44t diagonal freight.
References use relief quotas, balanced service, adjusted OD or area-average
congestion; none provides the same complete directed-source audit. Congestion
preference weights and density cutoffs are assumptions, not original facts.

## 8. Transfer Ratio

The source ratio belongs to a park's outgoing freight through its nearest
primary, not every primary's arbitrary throughput. F10256001 has eight
primaries but only four park ratios. Run-002's numerous N/A fields reflect
both overproduction of primaries and real denominator-association ambiguity.
Other papers change denominators or direction conventions; they do not settle it.

## 9. Q2 Candidate Network Construction

Eligible new physical corridors are assumed geometric candidates, not an
existing all-pairs network. Papers mostly use restricted local/core candidates
without surveyed engineering proof. Run-002 separates candidate/built edges
and graph layers; physical construction eligibility remains conditional.

## 10. Q2 Network Design / Routing

Run-002 has1120 physical tunnels and a fixed-design LP after construction
heuristics; eight park-link deletions were accepted with rerouting. References
offer shared hierarchy, local MSTs, ring MIPs and restricted enumeration.
These are meaningful search alternatives, not proof of unrestricted optimality.
[Q2 comparison](q2-network-comparison.md).

## 11. Capacity Interpretation

Train and vehicle capacities differ;2min line headway does not replace12min
node dispatch. Four-track capacity does not automatically enlarge a shared
station dispatch resource. References contain actual capacity/table
contradictions as well as ambiguous per-track assumptions. Static run-002
capacities PASS, but overall capacity feasibility stays PARTIAL.

## 12. Cost Accounting

Frozen conditional cost is93,223,150.212486yuan/day, reconstructed from physical
tunnel depreciation90,370,340.288598, station depreciation808,219.178082,
underground transport1,997,272.066880 and surface proxy47,318.678926. Physical
tunnels are charged once. No same-service cost ranking is justified.
[Cost comparison](cost-comparison.md).

## 13. Static vs Timed Daily Clearing

References:5 STATIC_ONLY,2 PARTIAL_OPERATION_MODEL,0 full-network clearing
certificates. FK0263 credits travel time and89/90 last-arrival calls; F10703002
contains timing fragments. Neither proves integrated transfer/dispatch
completion. Run-002's27.478101/143.521733t unfinished prove tested policies
fail, not all timetables infeasible. Its refusal to claim clearing is a strength.
[Capacity/operation comparison](capacity-operation-comparison.md).

## 14. Q3 Operational Modeling

Most paper evaluations use distance, utilization or risk indices. Run-002
actually replays state-dependent queues under0/12min handling but omits some
engineering resources and fails terminal clearance. This is partial operational
evidence, not a solved timetable or a reason to accept weaker static claims.

## 15. Failure / Surge Robustness

Run-002 removes both arcs for each of1120 physical tunnels;118 deletions
disconnect service. Worst reachable-demand fraction0.988972493976 is not
capacity-feasible restoration. References give selected failures/cycles and
some flow tables; calibrated exhaustive recovery remains absent. Surge sizes
are author scenarios, not source data. [Q3 comparison](q3-robustness-comparison.md).

## 16. Q4 Construction Phasing

Run-002 allows cross-year construction but prevents unfinished-tunnel use.
Several references give eight-year maps/lists; F10294003 gives3+2+3 stages,
FK0263 seven nodes/year, and F10710008 three10-year phases. Equal node count
is not equal tunnel length. F90005027 explicitly requires nodes before links.

## 17. Annual Feasibility

No reference supplies full annual OD/flow/capacity/clearance certification.
Run-002 checks commissioning and service, then correctly reports that the full
target fails all eight years. Partial construction connectivity alone is not
full service. [Q4 comparison](q4-phasing-comparison.md).

## 18. Saturation / Expansion

Run-002's first retained-routing static saturation is year2, source atyear0;
30year expansion remains unproved. F90005027's18 versus table17 and FK0263's
reserve-based4 use different criteria. Located reference additions exist but
do not constitute complete source-constrained operational expansion proofs.

## 19. Numerical Comparability

Counts, length, cost, Q3 time/distance and saturation are
**NOT_DIRECTLY_COMPARABLE** as performance rankings. Service share, hierarchy,
capacity interpretation, cost conversion and operational scope differ.
[Numerical comparability](numerical-comparability.md) records each blocker.

## 20. Reference Consensus

Seven papers share hierarchical aggregation and restricted/sequential design;
none establishes a unique correct solver or full operational certificate.
[Consensus](reference-consensus.md) includes membership, n/7 and confidence.
Frequency is not correctness.

## 21. Skill Strengths

Source/demand provenance, node/edge semantics, coverage, conservation, hard
capacity gates, physical-edge counting, independent objective reconstruction,
solver-scope discipline and honest operation/expansion limits are preserved.
These are observed Skill-assisted strengths, not an unaided-prompt ablation.

## 22. Skill Weaknesses

Network design/search and multistage solution quality are weak. A cautious
PARTIAL result does not substitute for a competitive solution. Broader legal
hierarchy and operation search remain untested. The short network reference
works in combination with other rules; brevity alone does not show a gap.

## 23. Reference Weaknesses

Confirmed examples include over-bound ground-flow tables, a wrong component
sum, conflicting interprimary vehicle capacity, availability probabilities>1
and17/18 saturation disagreement. Missing certificates are labeled UNVERIFIED,
not automatically failed. Physical tunnel double counting was not established.
[Reference weaknesses](reference-weaknesses.md).

## 24. Algorithm / Search Quality Limits

Run-002 is restricted by one-primary-per-secondary, zero primary ground service,
full offdiagonal underground service and few topology changes. Reference
improvements mainly support G5 model/search quality, sometimes G2 technique or
G3 protocol differences. No new solve was attempted to improve those numbers.

## 25. Generalizable Gaps

No candidate meets all ten G1 conditions. Current network, optimization,
stateful and evidence rules already cover construction semantics, dependencies,
resource feasibility, terminal states, perturbations and scoped claims.
Actual failed greedy policies do not establish missing-rule causation.
[G1 assessment](generalizable-gaps.md).

## 26. Problem-Specific Techniques

Centre cover variants, congestion-relief quotas, nearest-park primary
enumeration, MST/ring choices and track policies are useful problem-specific
or algorithmic alternatives. They are not added to Skill by this benchmark.
No graph platform, generic solver framework or stochastic module is developed.

## 27. Top-1 Candidate

**NONE**. Shared-hierarchy search is the strongest quality concern, but existing
dependency and decision-semantic improvement rules allow it. No structural
invalidity or missing-rule causal chain has been demonstrated in the accepted
conditional static result.

## 28. Current Skill Level

GRAPH_FORMULATION ADEQUATE; NODE_EDGE_SEMANTICS STRONG; DEMAND_AGGREGATION
STRONG; NETWORK_DESIGN WEAK; FLOW_CAPACITY_VALIDATION STRONG;
OPERATIONAL_FEASIBILITY ADEQUATE; ROBUSTNESS_EVIDENCE ADEQUATE;
MULTISTAGE_NETWORK_PLANNING WEAK; SOLUTION_QUALITY WEAK; OVERALL ADEQUATE.
Adequate operational discipline does not mean successful operation.

## 29. Final Decision

**NO_MAJOR_GENERALIZABLE_GAP**. `2017F_REFERENCE_BENCHMARK_COMPLETE` describes
completion of this comparison only. Run-002 remains BLIND_RUN_PARTIAL.

Historical protection, source bytes, frozen summary and artifact/index manifests
are checked in [verification.md](verification.md) and
[integrity-verification.json](integrity-verification.json). The inherited
304 development passes/one enclosing-path failure and
DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING remain recorded, not repaired or
reclassified as a network gap.

Recommended next action: human review. Stop without changing Skill, revising
historical runs, re-solving2017F or starting another problem.
