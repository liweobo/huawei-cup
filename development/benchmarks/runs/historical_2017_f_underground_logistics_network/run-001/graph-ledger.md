# Graph Construction Ledger

Status: PARTIAL for the real instance. The graph has not been instantiated. UNKNOWN is not an empty graph and cannot pass connectivity by vacuity.

## Node Register

| node_id | node_meaning | node_type | coordinate / location | source |
|---|---|---|---|---|
| P_p, p=1..4 (symbolic, not original IDs) | Logistics park underground interface | PARK | Missing park/map attachment | F02,F09,F30 |
| H_j (uninstantiated) | Selected primary transfer/service station | PRIMARY | Design variable at an eligible location | F05,F07,F08 |
| S_j (uninstantiated) | Selected secondary service station | SECONDARY | Design variable at an eligible location | F06-F08 |
| Z_i (uninstantiated) | Original freight region centre | SURFACE_DEMAND_ZONE | Missing coordinates in metres | F01,F03,F18 |

An original region and its representative centre remain an aggregation, not a physical station. Centre coverage is permitted by F03; fine-scale intra-region routes/costs are unresolved. No merging, clustering, low-demand deletion or graph sparsification is performed.

## Edge Register

| edge_definition | edge_direction | edge_weight | weight_unit | capacity | construction_rule | source |
|---|---|---|---|---|---|---|
| PARK_PRIMARY_TUNNEL | Physical undirected facility; two separate directed operating arcs | Validated corridor length; directional travel time/transport rate kept separately | km; min; yuan/(t km) | 10 t vehicles, train/track/station limits | Authorized park to its nearest primary under a declared distance measure; cost includes park leg | F05,F09,F21,F30 |
| PRIMARY_BACKBONE_TUNNEL | Same paired-arc representation | Same distinct fields | same | 5 t vehicles | Eligible primary corridor; selected backbone must connect all selected primaries | F05,F09 |
| LOCAL_UNDERGROUND_TUNNEL | Same paired-arc representation | same | same | 5 t vehicles | Within primary service territory; remove own primary and no secondary may reach a different primary | F06,F09 |
| SURFACE_ACCESS | Directional transfer/access relation, NOT a tunnel | Actual access length/time/cost if known | separate fields | Station ground send+receive bound | Covered centre within selected radius <=3 km; last-mile assumption limited by F20 | F03,F04,F07,F20 |
| SURFACE_ROAD_ROUTE | Separate road layer, not inferred from centre distances | Validated road distance/time | km/min | Unknown | Data not supplied; no fictitious road arcs | F07,F17 |

Why an edge exists: a documented eligible corridor connecting the stated types plus a positive build decision. Coordinates alone do not create that corridor. In the synthetic oracle, eligibility is the explicit artificial list in `inputs/oracle.json`, with a reason per edge; it has no Nanjing interpretation.

Existing network E_existing: unknown/not supplied. Candidate corridors E_candidate: uninstantiated. Built tunnels E_built subset E_candidate: decision. Forbidden links E_forbidden: cross-region secondary bypasses are prohibited by F06; other engineering exclusions need input. These sets are never conflated.

directed_or_undirected: undirected physical investment with directed operations; unequal OD does not change paired construction dimensions. simple_or_multi_graph: simple physical corridor register, parallel tracks represented by discrete track option, not duplicate chargeable edges; if actual parallel corridors exist use separate corridor IDs. self_loops_allowed: false for tunnels; intrazonal demand stays in the demand ledger. connectivity_requirement: connected primary backbone and own-primary mediation for every served secondary; every assigned positive OD must be reachable.

## Geometry, Weights And Algorithm Gate

CRS/origin/projection/scale: unavailable. Map-pixel lengths are not engineering distances. Euclidean centre distance, geographic distance, surface road distance, surveyed tunnel length, selected-network shortest-path length, travel time and generalized cost are separate quantities. No conversion between them is implicit.

Length is additive along a route. Transport cost is additive after multiplication by directional tonnes and the given rate. Travel time requires acceleration, speed, stops and transfers. Capacity is a bound in tonnes per declared period, never an additive shortest-path weight. Construction cost is counted once per built physical facility, not once per shipment.

Positive static length justifies Dijkstra in the oracle; inputs reject negative/nonfinite weights. Disconnected pairs have no route and their loss is reported. Multi-criteria paths need a declared policy, not arbitrary sum. The real network has not passed these gates because its inputs are missing.

Physical crossings: the source sets engineering feasibility aside; no obstacle, elevation, crossing junction, turning arc or construction zone is inferred. Lines crossing on a plot would not automatically create a graph junction. No formal city-network picture is produced.
