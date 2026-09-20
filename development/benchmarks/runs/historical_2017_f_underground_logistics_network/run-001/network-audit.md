# Network Audit

Two scopes are kept separate. ORIGINAL_INSTANCE has no graph because essential attachments are unavailable. SYNTHETIC_CODE_VALIDATION has a deliberately small, fully specified graph. PASS in the latter never fills a missing original result.

| Check | Original instance | Executed oracle evidence |
|---|---|---|
| Node/edge count and IDs | UNKNOWN, not 0 | 8 nodes; 8 candidate physical corridors; baseline/primary 7 built; redundant 8; no duplicate corridors or self-loops |
| Edge provenance | PARTIAL symbolic rules only | Explicit corridor list/reason/source on every edge; no radius graph or all-pairs generator |
| Node/edge semantics and layers | Symbolic layers frozen | Park, primary, secondary types checked; no surface-road graph invented |
| Directionality | OD direction given; original values missing | 6 asymmetric OD entries; two directed arcs per symmetric physical corridor |
| Weights/units | Length/CRS/time basis unresolved | Positive km; tonnes/day; yuan/(tonne km); capital yuan; objective yuan/day |
| Geometry | EXTRACTION_UNVERIFIED map/IDs/scale | Artificial Cartesian points; explicit straight-tunnel test assumption |
| Connectivity | NOT CHECKED on absent graph | Independent component traversal reconstructs saved component labels; connected baseline and primary |
| OD reachability | NOT CHECKED | 6/6 normal OD pairs; unreachable failure OD listed with no fictional routes |
| Hierarchy | F06 retained | Removing each own primary leaves its secondary unable to reach foreign primaries |
| Flow conservation | NOT_APPLICABLE without flow | 48 commodity-node equations for each full-demand solution; zero residual; saved detailed report |
| Capacity | NOT_APPLICABLE without instance | Directional line limits and integer aggregate station departure bounds pass in normal solutions; ground exchange separate from transit |
| Objective | PARTIAL formula only | Independently rebuild physical capital, route tonne-km, arc tonne-km, daily depreciation and total |
| Small graph | Code evidence only | Manual directed 4-node oracle, unequal reverse path, disconnected node; Dijkstra and Floyd match known answers |
| Edge removal | No original network tested | 22 physical-tunnel removals: 7 baseline, 7 primary, 8 redundant; both directed arcs removed each time |
| Engineering geometry | NOT VERIFIED | Not an engineering instance; no surveyed construction/crossing/curvature certification |
| Daily clearing | NOT VERIFIED | Static necessary conditions only; no timetable or terminal-inventory proof |

`results/independent-audit.json` independently reconstructs 33 saved networks without importing the experiment generator. `results/primary.json#/flow_conservation` is the machine-readable source/sink/intermediate residual ledger. `results/single-edge-removal.json` preserves components, isolated nodes, routes, losses and component costs per failure.

Robustness result is bounded: the redundant triangle preserves all oracle OD after any one backbone tunnel outage, while secondary/park branches remain vulnerable. Across all physical-tunnel failures its worst reachable-demand fraction is 0.2635658915, not 1.0. The primary tree's worst fraction is 0.1937984496. Neither is globally robust under arbitrary single-tunnel removal. These fractions measure demand reachability, not expected reliability or maximum delivered throughput under a new timetable.

No centrality metric, normalization score, aggregate capacity-as-path-weight, implied existing network, inferred edge crossing or hidden spatial aggregation is used.
