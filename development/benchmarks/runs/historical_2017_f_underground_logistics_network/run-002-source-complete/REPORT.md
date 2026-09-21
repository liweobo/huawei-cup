# 2017F Source-Complete Blind Run

Final decision: **BLIND_RUN_PARTIAL**.
Source attachments are complete. This run provides real-data conditional
network results, not a complete Q1-Q4 competition solution. No Skill change,
excellent-paper access or generalizable network gap is claimed.

## 1. Source Provenance
Trusted USST institutional mirror, not organizer-official:
https://lxy.usst.edu.cn/2017/0916/c6729a38056/page.htm .
Member URLs/hashes/bytes are in source-manifest.json and source-provenance.md.

## 2. Source Recovery Verification
All five retained original files are rehashed locally. DOC blob
c2dd56c208cf3c7f80f2e52ff1f58ee0a758166f is unchanged. Metadata-only raw retention
continues; run-001 and source-recovery are untouched.

## 3. Input Audit
Independent DOC rendering and XLS dual-reader equality;114x114 OD,110 regions
and4 parks. Native source cells, units and all diagonal entries are retained.
See input-audit.md and results/input-audit.json.

## 4. Problem Facts
problem-facts.md independently records Q1-Q4 and28 source facts. GIVEN is
separate from derived, assumed and scenario quantities. No missing attachment
excuse is used for remaining task limitations.

## 5. Graph Semantics
Simple undirected physical tunnels; two directed routing arcs per tunnel.
Park/primary/secondary layers and own-primary routing restrictions are explicit.
No observed existing ULS network is supplied.

## 6. Candidate Node / Edge Semantics
Centre/offset locations and straight candidate corridors are assumptions.
Selected construction is separate from potential links. Neighbour/tree/demand
shortcut rules are search restrictions, not source facts or existing roads.

## 7. Geometry And Coordinates
XLS metres converted to local planar kilometres; no CRS/origin/projection claim.
Map pixels supply no engineering distances. Service radius3km is not an edge
eligibility cutoff. Curves, crossings and subsurface constructability unverified.

## 8. Directed OD Audit
COLUMN=ORIGIN, ROW=DESTINATION;5,607 asymmetric unordered pairs.
Total163,406.46t/day, park-related128,865.538t/day. Diagonal3.44t/day retained
as surface-local service. No symmetrization or upper-triangle reduction.

## 9. Q1 Baseline
Real per-region2000t-fill construction:150 primary +150 secondary stations,
1452 tunnels, conditional daily cost118,950,629.848876yuan. Earlier infeasible
layouts are retained as rejected attempts, not formal incumbents.

## 10. Q1 Primary Model
Spatial consolidation with divisible allocation and1800t constructive fill,
one primary per secondary. This is a restricted heuristic location model,
not a continuous global facility optimizer. B=M.T D_offdiag M conserves freight.

## 11. Q1 Results
118 primary +118 secondary stations. Full node coordinates/volumes are in
node-results.md and results/primary/node-results.json; service fractions and
radii are also saved. Park-associated ratios are in q1-results.md.

## 12. Q1 Validation
All110 centres meet3km and station ground limits. Actual node freight and OD
are independently reconstructed. Per-primary transfer ratios without an
associated park have undefined source denominators; Q1 is PARTIAL.

## 13. Q2 Network Design
Consolidated1128-link design improved by eight accepted park-link deletions.
Final1120 physical tunnels:464 park-primary,538 primary-primary,118 feeders.
The computed figure uses real source coordinates and actual selected links.

## 14. Q2 Routing / Flow
Capacity-coupled origin-commodity LP on the built graph; parks cannot be transit
nodes for other origins. Positive-weight path decomposition follows the LP;
shortest paths on all potential edges are not substituted for network design.

## 15. Q2 Capacity
Declared8-car trains:80t on park links and40t elsewhere. Station max84
rounded departures/day; directional line max32. Static resource violations
are zero. Daily clearance remains unproved and both tested policies fail it.

## 16. Q2 Objective
Routed transport + declared local access proxy + tunnel/station depreciation.
Daily depreciation uses0.01/365 and counts each physical tunnel exactly once.
Source units and exclusions are detailed in cost-ledger.md.

## 17. Q2 Results
Conditional cost93,223,150.212486yuan/day:
transport1,997,272.066880; access47,318.678926;
tunnel depreciation90,370,340.288598; station depreciation808,219.178082.
This is not the unrestricted minimum or a fully operationally feasible answer.

## 18. Q2 Independent Audit
Reloads saved data without solver helpers. One graph/primary component,
no isolates, all nominal OD reachable; max flow residual1.0914e-11t/day.
Objective independently reconstructs within7.45e-8yuan/day. Q2 is PARTIAL.

## 19. Q3 Operational Model
Deterministic stateful queues, fixed legal resource slots, explicit arrivals
and transfers. Optimistic constant-speed/unlimited-fleet scenarios use0/12min
transfer handling. Closure=SCENARIO_ASSUMED, not full physical validation.

## 20. Q3 Interruption Scenarios
1120 single physical-tunnel removals, both arcs removed, no invented
probabilities. Worst reachable routed-demand fraction0.988972493976.
This metric does not certify capacity-feasible rerouting after failure.

## 21. Q3 Demand-Surge Scenarios
Park1 outbound-only+10%/+25% passes retained-route static limits, max85 calls.
Four-car configuration fails station capacity. Alternative park-wide90-call
interpretation cannot support the nominal full-diversion policy.

## 22. Q3 Results
At18h,0/12min handling policies leave27.478101/143.521733t unfinished.
Independent leg replay passes legal-action and conservation checks.
Node count/level and position diagnostics are explicitly limited; Q3 PARTIAL.

## 23. Q4 Growth Model
Source day t=0; year y freight1.05^y. No time-index shift.
Retained-route static saturation is evaluated from station/line/ground limits,
not just a demand curve. Future expansion is separate from the Q2 design.

## 24. Q4 Construction Phasing
Eight equal annual amounts of construction work. A tunnel may span years
but is not used until completed; endpoints commission no later than use.
Connected primary commissioning is independently checked.

## 25. Q4 Annual Feasibility
All eight scenarios retain static capacity by throttling usable routes and
accounting for remaining surface fallback. Full targets fail in every year;
this is not a full feasible service plan. Detailed annual tables: q4-results.md.

## 26. Q4 Saturation / Expansion
Unchanged full-demand retained routing first saturates at year2.
SATURATES_BEFORE_30_YEARS. Proposed extra station modules are only load-based
lower bounds, not a located/costed/operated expansion network. Q4 PARTIAL.

## 27. Numerical / Solver Status
Final LP:273,280 variables,29,280 equality rows,2,476 inequality rows,
122 origin commodities. OPTIMAL applies only to fixed-design continuous
routing. Joint result is HEURISTIC_BEST_FOUND in a bounded search, no global gap.

## 28. Small-Graph Validation
Six new tests pass: four network-component tests and two exact six-node queue
precedence cases. These validate code, not2017F solutions. No run-001 reuse.

## 29. Network Robustness
Sensitivity is real-graph, source-demand based with declared failure/surge
objects. Feeder failures expose service loss. No blanket robust-network claim,
invented failure probability or reliability estimate is made.

## 30. Skill Strengths
Frozen workflows supported facts/assumptions, baseline comparison, hard
feasibility, real objective reconstruction, stateful closure and cautious
reviewer claims. All required task stages were actually performed.

## 31. Skill Weaknesses
This run does not isolate autonomous network-specific guidance because the
user supplied detailed checks. Search quality, operational closure and full
expansion remain limited. Strict clean-room manifest gate is not satisfied by
the declared repository-visible process; no isolation success is fabricated.

## 32. First Meaningful Failure
DAILY_CLEARING_NOT_ESTABLISHED is the first unresolved substantive
task-completion gate after the source-complete static design. Earlier rejected
layouts are ordinary feasibility-search outcomes, not Skill failures.

## 33. Failure Classification
failure_level=NONE for demonstrated Skill gap. Partial task blockers are
material, not cosmetic. Claiming a complete feasible solution would be P0;
that claim is explicitly prohibited. Export/path bugs are not network gaps.

## 34. Generalizable Gap Candidate
NONE. Existing optimization/stateful/mechanism rules already require
executable feasibility and bounded claims. No candidate satisfies all eight
G1 conditions. No NETWORK_MODELING_READY declaration is supported either.

## 35. Remaining Uncertainty
Facility restrictions, park dispatch scope, transfer-ratio association,
constant-speed operations, finite fleet, route restoration, geometry and
30-year expansion. Regression:304 development tests pass,1 path-guard failure
remains;6 local tests and all requested static harnesses pass.

## 36. Historical Integrity
Starting HEAD492d414b542b4cf4567ea7204ef1f146f63bbefd;
Skill tree2b29e8ffa7c15d33bf81e675e8f1dcb240c226a6.
Hash-only checks in integrity-after.json preserve all prior covered files.
Only run-002 artifacts are staged. Raw/extraction/test caches remain ignored.

## 37. Final Decision
**BLIND_RUN_PARTIAL**. Real conditional results are preserved with explicit
limits. Recommended action: human review of assumptions, incomplete operating/
expansion evidence and benchmark validity before authorizing further work.
Stop here: no Skill edits, excellent papers, automatic gap fix or eighth problem.
