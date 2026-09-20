# Problem Facts

Source: retained original .doc, SHA256 `7cd51bdf0c6a0392eef93fc84efaf16090262fe94e7bae97d385fee67be28719`. Page locators below refer to the independently rendered six-page audit copy, not an asserted invariant Word pagination. All F rows are PROBLEM_GIVEN_FACT; derived expressions and policies are in assumptions/model.

## Subproblems

| ID | Required output | Inputs and dependency | Current scope |
|---|---|---|---|
| Q1 | Select first/second-level node counts and locations, service regions, actual freight volumes, each primary's transfer ratio | Area centres/areas/map, directed OD, congestion indices, four parks; p4 | Facts and parametric design only; essential attachments absent |
| Q2 | Tunnel positions, node freight volumes, directed channel flows; minimum daily transport plus depreciation cost | Q1 nodes/assignments; modest location adjustment allowed if transfer ratio changes little; p4-5 | Conditional formulation; no real network or objective |
| Q3 | Simulate operation; assess node count/location/level and route changes; reduce freight distance/time/cost; address interruption/directional surge | Q2 network, routing and operating assumptions; p5 | Code oracle and generic failure scenarios only |
| Q4 | Eight-year roughly equal-length construction sequence, 30-year demand support, evolution versus Q3, saturation and expansion | Q3 design, annual 5% growth, annual feasible operation; p5-6 | Growth/capacity formula verified; no city schedule or saturation year |

Dependency: source audit -> Q1 allocation/node design -> Q2 joint corridors/flows -> Q3 operational improvement/failure assessment -> Q4 annual construction and expansion; Q3 may feed back to Q1/Q2. Every propagated numerical result is currently blocked by the missing original instance.

## Given Facts

| ID | Fact | Unit / semantic limit | Source |
|---|---|---|---|
| F01 | Geography is Nanjing Xianlin freight regions | Number/boundaries/names not present in this .doc | p4, p6 |
| F02 | Four logistics parks; their freight should go underground as much as possible | Four parks does not mean exactly four primary nodes | Q1 note 6, p4 |
| F03 | Region centre coverage suffices to cover the region | Area aggregation is explicitly allowed; centres themselves missing | Q1 note 3 |
| F04 | Each service radius can be chosen within 3 km; inter-node distance unrestricted | Radius is a coverage rule, NOT a tunnel-edge threshold | Q1 note 4 |
| F05 | Primary nodes connect to logistics parks and other primary nodes are connected | 'Connected' does not require a complete graph | basic characteristic 5, p3 |
| F06 | Secondary nodes reach nonlocal primary nodes only through their own region's primary | Membership, primary cut-vertex condition; regions need explicit definition | basic characteristic 5 |
| F07 | Both node levels interface to the surface for multimodal transport | Transfer connections differ from tunnels and surface road routes | basic characteristics 2,5 |
| F08 | Primary ground send+receive limit 4000; secondary 3000 | Tonnes; time basis not explicitly printed on this sentence. Daily interpretation A01 needs attachment confirmation | p3 |
| F09 | Park-primary tunnels use 10-tonne vehicles; every other tunnel uses 5-tonne vehicles | Q2 resolves generic wording about large vehicles at primaries | p3 and Q2, p5 |
| F10 | A train generally contains 4-8 vehicles/carriages | 10 or 5 tonnes is per vehicle, not per train | vehicle reference, p3 |
| F11 | Operating speeds 20-60 km/hour; reference 13.5 m/s (about 49 km/hour) | 13.5 m/s is 48.6 km/hour exactly; not an additional constraint at 49 | p3 |
| F12 | Same direction on one line: train spacing at least 2 minutes | Separate from station dispatch interval | p3 |
| F13 | Each node dispatches one train per 12 minutes including handling, starting and waiting; at most 5/hour; 18 operating hours/day | Aggregate/per-direction scope not clarified; daily clearing still needs travel/timing verification | p3 |
| F14 | Reference acceleration/deceleration 1 m/s^2; turn radius 70-80 m | Reference engineering values, not verified corridor geometry | p3 |
| F15 | Reference power: three-phase 380 V, 50 Hz, 460 A per motor plate | No power cost or motor count; do not infer energy cost from these alone | p3 |
| F16 | Prefer bidirectional double-track (two bores); high-volume links may use four-track (two bores) | Capacity multiplier depends on train/station scheduling; dimensions are shared between directions | p3, Q2 note 2 |
| F17 | OD considers origins and destinations, not intermediate regions | Directed tonnes; horizontal-axis label sends to vertical-axis label | p4 and final attachment description p6 |
| F18 | Coordinate units metres; region areas and congestion coefficients supplied in referenced attachments | CRS, origin, projection, area unit and coordinates absent here | p6 |
| F19 | Congestion levels 0-2,2-4,4-6,6-8,8-10; congestion proportional to region inbound+outbound freight | Given approximation may yield values >10; denominator and coefficients require OD/data | Q1 note 1 |
| F20 | Secondary-node last-mile movement uses people/small vehicles and may be assumed not to affect traffic | Does not assert zero transport cost or that every primary access trip is traffic-free | Q1 note 5 |
| F21 | Primary transfer ratio: park goods through nearest primary to other primaries / that park's total outgoing freight | Percentage; not degree, betweenness or total node throughput; zero denominator undefined | Q1 note 2 |
| F22 | Nodes and channels must clear daily | A static capacity solution alone does not prove this | Q2 note 1 |
| F23 | Both directions of adjacent tunnel have identical dimensions, designed for larger single-direction flow | Use max(F_uv,F_vu), not their mean; do not pool capacity without evidence | Q2 note 2 |
| F24 | Daily total = transport + tunnel/node depreciation | No arbitrary weighted score | Q2 note 3 |
| F25 | Average transport rate always about 1 yuan/(tonne km), including vehicles/equipment depreciation, independent of tunnel size | Freight-distance, not unweighted sum of shortest paths | Q2 note 3 |
| F26 | 10 t tunnel: four-track 5e8 yuan/km, double-track 4e8 yuan/km | Given bidirectional facility prices counted once per physical tunnel | Q2 note 3 |
| F27 | 5 t tunnel: four-track 3.5e8 yuan/km, double-track 3e8 yuan/km | Per physical km, not lane-km without conversion | Q2 note 3 |
| F28 | Primary node 1.5e8 yuan; secondary 1e8 yuan | Per constructed node | Q2 note 3 |
| F29 | Design life 100 years; annual depreciation 1% | Do not divide by both 100 and another 100 | Q2 note 3 |
| F30 | Exclude park construction and underground nodes inside parks; include outgoing park tunnel length | Cost boundary explicit | Q2 note 4 |
| F31 | Q3 calls out channel interruption and demand surge in a direction | No specified probabilities, surge factors or risk weighting | p5 |
| F32 | Annual demand growth 5%, horizon near 30 years; construction over 8 years at roughly equal annual lengths | No exact annual length tolerance or discount rate | Q4, p5-6 |
| F33 | Figure 5 is a possible network evolution illustration | Not the actual region map, node list, coordinates or existing network | Q4 note 1 and caption p6 |
| F34 | The exercise explicitly sets aside feasibility/engineering technology questions in background | Still respect explicit hierarchy, service radius and operating constraints; no real constructability claim | p3 |

## Input Availability Freeze

Original doc present and byte-verified. Five source raster objects and two text boxes were inventoried; the renderer additionally inserts its own evaluation logo, which is excluded from source evidence. No native Word tables or ObjectPool embedded data files were found. Four content images depict technology/concepts; the evolution composite provides no usable coordinate/node table.

Required missing inputs: original numbered freight-region map, directed OD matrix, region centre coordinate/area table, region congestion coefficients, park identifiers/locations and their OD correspondence. Number of regions, real nodes, candidate corridors and OD pairs: UNKNOWN, not zero. Existing ULS links: NOT GIVEN, not an inferred empty city network. Budget: NOT GIVEN. Forbidden tunnel corridors/obstacles: NOT GIVEN. Scale/projection/origin: NOT GIVEN.

EXTRACTION_UNVERIFIED applies to schematic node IDs, legends, map geometry and any attempted coordinates. No formula or table value is reconstructed from pixels. The stated verbal ratio and all printed numeric constraints above were compared with rendered text. No original attachment is silently replaced by a scenario.
