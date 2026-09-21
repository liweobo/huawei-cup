# Frozen Current-Skill Solution (Before Reference Methods)

This summary was written only from the committed source-complete blind run,
before downloading or reading the seven reference papers. It is immutable
throughout this post-hoc comparison. Its exact hash and source-file hashes are
recorded in pre-reference-freeze.json.

Repository HEAD:33548fd4a53ec3b05d4fc0d19cb9cdc319e8a8bc.
Skill tree:2b29e8ffa7c15d33bf81e675e8f1dcb240c226a6.
Source: sibling run-002-source-complete/{assumptions.md,completion.json,
q1-results.md,q2-results.md,q3-results.md,q4-results.md,REPORT.md}.

## Q1

118 primary +118 secondary stations; all110 original region centres satisfy
3km coverage. Region freight may be split among nearby secondary stations.
Candidates are original centres, with150m east overflow offsets; paired primary
stations start250m north. One primary per secondary is an explicit restrictive
construction, not a source requirement. Primary local ground exchange is zero;
secondary exchange has a3000t/day hard bound. This excludes most continuous
placements, shared multi-secondary primary hubs and alternative service scopes.
The real-data baseline used150+150 stations; feasible fill targets were2000t
(baseline) and1800t (consolidated), after infeasible3000/2400t attempts.

Original OD is114x114, column-origin/row-destination, with IDs1-4 and791-900.
It remains directed. Total163406.46t/day; diagonal895=2.92 and896=0.52 remain
surface-local demand. Off-diagonal OD is fully served in the static model.
Mapping B=M.T D_offdiag M preserves demand. Station-local174.816260543t/day
is retained without tunnel movement. Park area/congestion blanks are not
imputed; congestion11.54 is not clipped. Areas are retained but not needed by
the permitted centre-coverage approximation.

Euclidean-nearest park gateways are K1:P060, K2:P088, K3:P076, K4:P091.
Each reported park transfer numerator/ratio is zero under the routed solution;
denominators are each park's original outbound freight. Primaries nearest to no
park receive N/A because no source-defined park denominator is associated.
This unresolved per-primary output interpretation contributes to Q1 PARTIAL.

## Q2

1120 physical tunnels,2240 routing arcs,8692.161736672km.
464 park-primary,538 primary-primary and118 own-primary feeders.
No park-secondary or cross-parent-secondary links; parks cannot be unrelated
transit nodes. Straight corridors are hypothetical engineering approximations,
not surveyed construction eligibility. Sparse primary candidates use neighbour/
connecting-tree rules and two high-demand peers.3km is a coverage radius,
not a tunnel adjacency threshold. No map pixel distances are used; XLS metres
are converted to local planar kilometres with unspecified CRS/projection/origin.

Design heuristic is followed by fixed-design multicommodity continuous LP.
Eight park-link deletions are accepted only after feasible rerouting and lower
realized total cost. No unrestricted joint optimum is claimed.
Final LP has273280 variables,29280 equality rows,2476 inequality rows and122
origin commodities. OPTIMAL refers only to fixed-design LP; design quality is
HEURISTIC_BEST_FOUND within the bounded search.

Chosen8-car trains carry80t on10t-vehicle park links and40t on5t-vehicle links.
Each constructed station has at most90 departures/day in aggregate; line
headway is separately2min in each direction. Parks have no aggregate90-call
limit in the nominal interpretation; an alternative park-scope test is saved.
Static max station calls84 and directional line calls32; ground, line and
station capacities PASS. Independent flow residual1.0914e-11t/day and objective
reconstruction difference7.45e-8yuan/day. Graph connected, no isolates, all
nominal demanded endpoint pairs reachable.

Conditional daily cost93223150.212486yuan:
underground transport1997272.066880; Euclidean local-access proxy47318.678926;
tunnel depreciation90370340.288598; station depreciation808219.178082.
Capital depreciation is1%/365; each physical tunnel is charged once, not twice
for directed arcs. Unknown internal-region road distance is outside this
evaluable cost boundary. This is not a full operationally feasible minimum.

## Q3

Actual real-network stateful queue scenarios use all freight ready at t=0,
constant13.5m/s speed, unlimited trains and buffers, and transfer handling0/12min.
Legal departures obey12min station slots and2min directional park-arc slots.
Route precedence, payload, headway and conservation are independently replayed.
At18h unfinished freight is27.478101/143.521733t. These tested greedy policies
fail; this does not prove that all timetables are infeasible. Acceleration,
empty circulation, switch resources, access time and final unloading are omitted.

1120 single physical-tunnel removal scenarios remove both arcs;118 disconnect
service. Worst reachable routed-demand fraction0.988972493976. Topological
reachability is not a certificate of capacity-feasible restoration. Park1
outgoing-only+10%/+25% are assumed surge scenarios, not measured probabilities.
Both pass static retained-route capacity (max85 calls). Four-car trains require
up to160 station calls and are rejected.125/500m position sensitivities, one
unreallocated station deletion and an invalid demotion are diagnostics only.

## Q4

Eight construction years, source day t=0, annual demand1.05^y.
Equal construction work1086.520217084km/year may span years; incomplete tunnels
cannot carry freight. Stations commission before incident links are used;
active primary backbones remain connected. Retained usable routes are throttled
to static capacity; all remaining demand is explicitly surface fallback.

Underground fractions by year:
0.177277,0.471822,0.637780,0.686736,0.703482,0.731649,0.724938,0.730981.
Regions above congestion4:82,37,11,8,6,4,5,3. Full target fails every year.
Unchanged full-design retained-routing first static saturation is year2.
Thirty-year expansion is unproved.432 extra equivalent station modules are a
conditional retained-load lower bound, not located/costed/routed expansion.

## Frozen Disposition And Process Limits

Q1-Q4 all PARTIAL; final decision BLIND_RUN_PARTIAL.
first_meaningful_failure=DAILY_CLEARING_NOT_ESTABLISHED.
failure_level=NONE means no demonstrated missing Skill rule, not complete task.
generalizable_gap_candidate=NONE; Skill and all prior histories unchanged;
excellent_solutions_accessed=false in the blind run.

Isolation was logical in a repository-visible process, not OS-enforced.
The legacy strict-isolation manifest gate rejected that visibility.
Structured-improvement full-schema normalization was retrospective.
Tests:304 development passes,1 enclosing-path guard failure,6 local passes,
and requested static harnesses pass. Existing default pytest collection and
frozen smoke/path issues were not repaired. These limits are preserved rather
than rewritten in response to reference methods.
