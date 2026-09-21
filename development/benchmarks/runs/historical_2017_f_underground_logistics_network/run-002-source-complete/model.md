# Model Selected Before Execution

## Q1

Read the original OD as D[o,d] = XLS[d+1,o+1], with headers removed. Preserve diagonal local surface demand L_i=D_ii and use D'=D-diag(L) underground. For region i define exchange w_i=sum_j(D'_ij+D'_ji).

Allocation a_is >=0 sums to one for each region, is zero beyond 3 km, and satisfies sum_i w_i a_is <=3000 for each secondary. Parks remain separate source/sink nodes. At every primary local ground exchange is zero, <=4000. A region's residual congestion index is original_index times remaining surface endpoint freight divided by original total endpoint freight. No clipping at 10.

Baseline: each region served independently by enough <=3000 t/day secondary stations. Primary: spatial greedy consolidation up to 2400 t/day per station to leave routing headroom; 2400 is a constructive target, not a source capacity. Sites/offsets and hierarchy follow A05-A06. This is not a global facility-location optimizer. All coverage and actual exchange are reconstructed from the allocation matrix.

Let M map original endpoints to parks/secondaries. Network OD is B=M^T D' M. Fractions at both ends preserve every original commodity; co-assigned endpoint demand needs no tunnel and is retained as local station handling, not deleted. Access cost sums endpoint freight times actual centre-to-station distance. Transfer ratios are evaluated from routed park commodities: for each park, identify its Euclidean-nearest primary, count that park's goods passing through that primary to another primary, and divide by the park's original outbound total. A primary nearest to no park has no source-defined denominator and is explicitly NOT_APPLICABLE, not assigned a fabricated zero ratio.

## Q2

Design variables: secondary/primary locations and allocations, selected physical tunnel IDs and types. Routing variables: nonnegative origin-commodity flows f[k,u,v] on directed arcs of the selected design. Every park or secondary is a commodity origin; its sinks are B[k,v]. Primaries are transshipment nodes. Parks cannot be intermediates for unrelated commodities.

Flow conservation: sum_out f - sum_in f = B[k,:].sum at origin k, -B[k,v] at sink v, and 0 otherwise. Station-local diagonal B[k,k] is excluded from both RHS terms. Every arc has a nonnegative additive kilometre weight. Directional flow <= (18*60/2)*train_payload, and each constructed station has sum_out(total_flow/train_payload) <=90-outdegree. This conservative linear reservation implies sum_out ceil(flow/train_payload) <=90; validate actual rounded counts afterward. It does not prove arrivals and transfers fit within 18 hours.

For a fixed physical design, use SciPy HiGHS LP to minimize routed tonne-km. If infeasible, reject the design before objective comparison. Daily cost = routed tonne-km + local access proxy + 0.01/365*(sum_physical length_km*type_price + 1.5e8*n_primary + 1e8*n_secondary). Solver OPTIMAL refers only to this fixed-design LP, never to the joint location/network problem.

Baseline design: four park spokes per primary, own secondary feeder, and a sparse connected primary backbone (nearest-neighbour candidates plus Euclidean connecting tree). Primary is the consolidated Q1 layout followed by bounded tunnel-deletion/rerouting improvement, with the same service policy, costs and hard constraints. Potential removal is ordered by depreciation savings, but acceptance uses re-solved feasible total cost. No penalty can admit an infeasible neighbour.

## Q3

Compare real routed distance, travel-time lower bound at 13.5 m/s, and deterministic queue simulation with legal departures/arrivals. Full physical-edge removal and directional park-1 surge scenarios report reachable demand, capacity overload and performance. Actual stochastic failure probabilities are not modeled. No centrality score substitutes for flow or cost. Reconnection options and node-level/placement changes are separately labeled conditional diagnostics unless fully audited.

## Q4

Grow original directed demand by 1.05^y. Construct a connected commissioning sequence, allowing fractional construction progress but no use of incomplete links. Yearly tables track completed links/nodes, service, original demand accounting, capacity and remaining surface fallback. Define unchanged-network saturation as the first integer y with a station/line/ground-exchange violation under the retained routing/allocation. Reoptimized-route sensitivity is separate. Any expansion is a new scenario with explicit additional resources, not a silent replacement of Q2.

## Verification And Limits

New small-graph oracle; original OD orientation witness; independent aggregate reconstruction; per-commodity residuals; graph components/reachability; per-resource capacity; physical tunnel accounting; original-data-derived figures; independent audit without calling the modeling helper. No claim of unrestricted global minimum, surveyed constructability, timetabled daily clearance, or 30-year feasibility without corresponding evidence.

## Executed Refinements

The preceding design narrative is the initial proposal, not a claim that all
initial fill targets worked. Actual baseline/consolidated fill targets are
2000/1800t per station after rejecting3000/2400t attempts; see assumptions.md and
attempt records. Eight physical park-tunnel deletions were evaluated and accepted
using feasible rerouting and full daily objective, not depreciation alone.
The complete planned-to-executed disclosure is in experiment-record.yaml.
Operation scenarios additionally follow A15 and operation-contract.json.
