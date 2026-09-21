# Q2 Results

Status: PARTIAL. Final design is STATIC_FEASIBLE_CONDITIONAL_DESIGN_NOT_TIMETABLE.
Joint facility/network optimality is not proved. Algorithm:
HEURISTIC_BEST_FOUND among the evaluated designs, with OPTIMAL_FIXED_DESIGN_LP
only for each accepted continuous routing subproblem.

| Component | Value |
| --- | --- |
| Physical tunnels | 1120 |
| Physical length km | 8692.161736672 |
| Directed arcs | 2240 |
| LP variables | 273280 |
| LP equality rows | 29280 |
| LP inequality rows | 2476 |
| Origin commodities | 122 |
| Routed transport yuan/day | 1997272.066879748 |
| Access proxy yuan/day | 47318.678926238 |
| Tunnel depreciation yuan/day | 90370340.288597509 |
| Station depreciation yuan/day | 808219.178082192 |
| Total yuan/day | 93223150.212485686 |

Double-track park-primary tunnels have10t vehicles, others5t. Eight cars/train
is an explicit chosen configuration. Construction is counted once per physical
tunnel, not once per arc. Depreciation is capital*0.01/365, with no extra division
by100-year life. Source transport price1yuan/(tonne km) is additive; local access
is a separately declared Euclidean proxy, not measured road cost.

All1120 physical corridors, lengths, types, costs and both directional flows
are in results/primary/tunnel-results.json. Detailed origin commodities and
paths are in compressed audit-friendly flow and route files. Station max84
rounded departures/day and line max32/direction/day pass aggregate limits.
Ground exchange and directed flow balance pass the independent audit.

The daily cost falls21.6287% relative to baseline.
This comparison does not establish the unrestricted minimum or feasibility of
full daily clearance. The operating queue tests leave freight unfinished.
