# Network Audit

Independent checker code/independent_audit.py imports no solver/model helper.
It reloads source CSVs, allocation, physical edges, commodity flows and routes.
All three evaluated complete static designs pass their declared static audits.

| Final primary audit | Result |
| --- | --- |
| Nodes / physical edges / arcs | 240 / 1120 / 2240 |
| Graph / primary components | 1 / 1; no isolates |
| OD reachability | PASS_ALL_REQUESTED_ROUTED_ENDPOINT_DEMAND |
| All110 centre coverage | PASS_ALL_110_REGIONS_CENTRE_COVERED |
| Max commodity balance residual t/day | 1.0913936421275139e-11 |
| Max path OD residual t/day | 5.9685589803848416e-12 |
| Ground / station / line violation | 0 / 0 / 0 (static) |
| Rebuilt objective discrepancy yuan/day | 7.450580596923828e-08 |
| Physical costing | one charge per physical tunnel |
| Daily clearing | FAIL for both tested queue policies; static result not upgraded |

Graph symmetry concerns physical directions only: two legal arcs per tunnel.
OD and directional flows remain asymmetric. Candidate corridors are explicitly
assumed, not existing infrastructure. Positive finite Euclidean lengths permit
the small-graph and decomposition path algorithms; capacities are not additive
weights. No engineering crossing/curve-radius feasibility is claimed.

Independent operation/phase replay additionally verifies train payloads,
headway, route precedence, terminal mass accounting, annual construction work,
endpoint commissioning, active-primary connectivity, original-OD disaggregation
and capacity with surface fallback. This passes accounting but all annual full
targets fail. Failure scenarios are topological sensitivity, not restoration
proof. No hidden demand is deleted.

Both generated figures were visually inspected after rendering. Their graph
and yearly data come solely from this run. Dense station IDs are provided in
node-results.md rather than overlapping labels on the overview plot.
