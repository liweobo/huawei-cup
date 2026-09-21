# Q3 Results

Status: PARTIAL; real-network operations and scenarios executed, not a complete
validated improvement of all node counts, levels, routes and interruptions.
The initial consolidation reduced150+150 to118+118 stations. Eight subsequent
physical park-link deletions strictly reduced the realized static daily cost.
See search-trace.json for all proposals, feasibility and incumbent history.

| Transfer handling min | Delivered t | Queued t | Transit/handling t | Delivered fraction | Mean time of delivered freight min |
| --- | --- | --- | --- | --- | --- |
| 0 | 163200.725638 | 27.362390 | 0.115711 | 0.999831658 | 292.235530 |
| 12 | 163084.682007 | 89.160897 | 54.360836 | 0.999120730 | 304.112068 |

Both greedy policies fail full18-hour clearing. Train legs were independently
replayed: payload, station12-minute spacing, directional2-minute spacing,
precedence and freight conservation pass. These are optimistic constant-speed
scenarios with unlimited fleet/queues and all freight available at t=0.
They do not include acceleration, empty returns, final unloading or finite
switch resources. Mean time is conditional on delivered freight, not all demand.
A failed greedy policy is not a certificate that every possible timetable fails.

Exhaustive single physical-tunnel removal: 1120 scenarios.
Each removes both directed arcs. Worst reachable routed-demand fraction is
0.988972493976; disconnected
scenarios: 118. No failure probability is assumed.
Reachability does not imply capacity-feasible rerouting or finite-fleet service.
Own-primary secondary feeders are single points of service failure.

Park1 outgoing-only surges+10%/+25% keep retained-route static capacity feasible
(max85 station departures). Four-car trains require160 departures at the worst
station, exceeding90 by70; this scenario is rejected, not absorbed by penalty.
Applying a90-departure limit to each park would cap outbound service at7200t/day
per park and make full park diversion impossible under that interpretation.

Position offsets125/500m are cost-only sensitivities, not adopted designs.
Deleting S117 without reallocation loses132.773t/day exchange and is rejected.
Demoting a primary while retaining park links violates the modeled hierarchy.
An additional independent same-parent feeder is only a proposed repair, not
constructed or validated. No generic random-failure probability model is added.
