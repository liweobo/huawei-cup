# Graph Ledger

## Semantics

Physical graph: simple, undirected, no self loops. Each selected tunnel is a build decision with its own stable ID and one capital charge. Routing graph: two directed arcs per physical tunnel, with separately computed directed flows. Demand remains directed regardless of the symmetric physical corridor assumption. Primaries must form a connected backbone; every secondary has only its own primary neighbour; parks cannot be unrelated flow intermediates.

No existing ULS links are given. This does not establish an observed empty city network. Every built link here is an ASSUMED new design, not surveyed infrastructure. All candidate primary pairs are conceptually geometrically eligible under A07, while the numerical search uses a disclosed sparse subset. Neither zero OD nor nonzero OD proves physical edge existence.

| Edge class | Why edge may exist | Endpoints / rule | Weight | Capacity |
|---|---|---|---|---|
| park-primary | Explicit hierarchy permits park-primary connections; straight corridor is assumed | Four park IDs to constructed primaries; selected spokes separately stored | XLS-derived/assumed-site Euclidean km | 10t per vehicle, declared 8 vehicles, directional headway and station calls |
| primary-primary | Explicit primary connectivity requirement; straight corridor is assumed | Connecting tree and neighbour/search candidates; candidate design is not an existing network | Same additive length km | 5t per vehicle; 8 vehicles; direction-specific capacity |
| primary-secondary | Own-region hierarchy connection | Each secondary connects only its own primary | Assumed interchange offset length km | 5t per vehicle; 8 vehicles |
| region-secondary access | Endpoint allocation, not underground construction | Positive assignment only when centre within3km | Access-proxy km, separately costed | Counts ground exchange, not tunnel line capacity |

No park-secondary, secondary-secondary or self-loop tunnel is eligible. The 3km bound applies only to service coverage. Route distance is the sum of selected arc lengths; it is not direct Euclidean separation. Travel-time lower bound is routed km /48.6km/h, not a timetable or a heterogeneous additive score. Capacity is never a shortest-path weight.

## Saved Instance

For every candidate retained as a result, `results/<name>/design.json` has all node IDs, types, coordinates, assignment meanings and physical edge IDs/endpoints/lengths/types/prices/construction_rule. `tunnel-results.json` adds both directional flows and departure counts. `commodity-flows.csv.gz` binds each flow to a physical ID and directed endpoints. Source-type distinctions are explicit in assumptions and per-edge records.

The failed initial sparse candidate and any revised search rules are preserved in attempt records. Top-two demand-peer shortcuts, when used, are an explicit design heuristic among geometrically eligible primary links, not a declaration that an OD pair creates an existing tunnel. A fixed-design LP returns INFEASIBLE before any candidate can enter the incumbent set.

## Distance And Algorithm Preconditions

All numeric lengths are finite and strictly positive. Dijkstra is used only on positive remaining-flow arcs to decompose an already capacity-feasible LP; it does not design the physical network. Disconnected/no-path cases are errors or reported reachability losses. Design LP, not independent unconstrained shortest paths, handles shared capacity. Failure removes both arcs of the named physical tunnel. Abstract connectivity is not engineering constructability.
