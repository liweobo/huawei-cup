# Independently Frozen Problem Facts

Source: newly read original DOC, SHA256 `7cd51bdf0c6a0392eef93fc84efaf16090262fe94e7bae97d385fee67be28719`, six-page local audit render. Page numbers refer to that render, not immutable Word pagination. All six pages and the separate original map were visually inspected. Renderer evaluation branding is excluded. No run-001 fact/model/result file was used to create this document.

## Given Tasks

| Question | Inputs | Required outputs | Dependencies |
|---|---|---|---|
| Q1 | Original area map, directed OD, centres, areas, congestion and parks | Primary/secondary counts, positions, service regions, actual freight and primary transfer ratios | Input audit -> allocation/location -> Q2 |
| Q2 | Q1 node group, permitted modest adjustments | Tunnel locations, actual node/channel flows, minimum daily transport plus depreciation | Q1 -> joint physical design and routing |
| Q3 | Real Q2 network and operating parameters | Evaluate/improve node count/location/level and routes; distance/time/cost; interruption and directional surge | Q2 -> operations and scenario tests -> possible Q1/Q2 revision |
| Q4 | Q3 network, growth and construction requirements | Eight-year build/evolution, differences, 30-year support, saturation and expansion | Commissioned partial network must be considered each year |

## GIVEN Constraints And Quantities

| ID | Fact | Unit / source |
|---|---|---|
| F01 | Xianlin, Nanjing freight-region division and processed data supplied | DOC p4; raw JPG/XLS |
| F02 | Four logistics parks; their freight should go underground as much as possible | Q1 item 6, p4 |
| F03 | Covering a region centre counts as covering the region | Q1 item 3, p4; not polygon-wide guarantee |
| F04 | Each service radius freely chosen within 3 km; inter-node distance unrestricted | Q1 item 4, p4; no tunnel-length cutoff |
| F05 | Primary nodes connect parks and primary nodes are connected | Basic characteristic 5, p3 |
| F06 | A secondary reaches nonlocal primaries only through its own primary | Basic characteristic 5, p3 |
| F07 | Both levels have ground interfaces; primary ground send+receive <=4000, secondary <=3000 | Tonnes, p3; per-day interpretation follows full-day source and daily operations |
| F08 | Park-primary channels use 10 t vehicles; all other channels use 5 t vehicles | Q2 opening p5 |
| F09 | A train normally comprises 4-8 vehicles | Reference parameters p3; vehicle payload is not train payload |
| F10 | Speed 20-60 km/h, reference 13.5 m/s; acceleration/deceleration 1 m/s^2; radius 70-80 m | p3; reference geometry, not surveyed corridors |
| F11 | Same-direction line headway at least 2 minutes | p3 |
| F12 | Each node one departure per 12 minutes, <=5/hour, 18 operating hours/day | p3; aggregate/per-port and park applicability are interpretation questions |
| F13 | Prefer bidirectional double-track (two bores), four-track available for heavy flows | p3 |
| F14 | OD considers origin/destination, not intermediate areas | p4 |
| F15 | Congestion bands width 2 from 0 to10; index proportional to regional inbound+outbound freight | Q1 item1; processed index may exceed10; not a reason to clip |
| F16 | Primary transfer ratio: a park's outgoing freight going through its nearest primary to other primaries / that park's total outgoing freight | Q1 item2 p4; undefined denominator association is not silently invented |
| F17 | Secondary local delivery by people/small vehicles may be treated as not affecting traffic | Q1 item5 p4; not zero monetary transport cost |
| F18 | All node/channel freight must clear each day | Q2 item1 p5; not implied by static capacity |
| F19 | Adjacent channel dimensions identical in both directions, designed for larger directional flow | Q2 item2 p5 |
| F20 | Average transport cost 1 yuan/(tonne km), including vehicles/equipment depreciation, independent of tunnel type | Q2 item3 p5 |
| F21 | 10t four-track: 5e8; 10t double-track:4e8; 5t four-track:3.5e8; 5t double-track:3e8 | Yuan/km of physical facility, Q2 item3 |
| F22 | Primary station1.5e8, secondary1e8 | Yuan/node, Q2 item3 |
| F23 | Design life100 years, annual comprehensive depreciation1% | Q2 item3; daily conversion needs stated convention |
| F24 | Exclude park and its internal underground-node construction; include outgoing park channels | Q2 item4 p5 |
| F25 | Q3 explicitly asks about a channel interruption and surge in one direction | p5; no probabilities or magnitudes supplied |
| F26 | Demand annual growth5%, approximately30-year horizon; eight years of roughly equal construction length | Q4 p5-6 |
| F27 | OD unit tonnes; horizontal-axis labels send to vertical-axis labels; coordinates metres | Final attachment paragraph p6 |
| F28 | Figure5 illustrates possible evolution, not a surveyed instance network | p6; its schematic IDs/geometry are not model inputs |

## Independently Verified Attachment Facts

`inputs/directed-demand.csv` preserves all 12,996 entries with exact XLS source cells; columns explicitly identify origin and destination. Source sheet `现状全天OD` establishes full-day basis. IDs are 1-4 and 791-900; the OD is asymmetric. Source sheet `各区域中心点及面积` supplies coordinate columns D:E in metres, B:C area in km^2/m^2 and F congestion. Park area/index blanks remain blank. Numerical audit counts and totals come only from `results/input-audit.json`.

Park identity 1-4 is SOURCE_CROSS_REFERENCE_INFERENCE, not EXPLICIT_MAP_LEGEND. Four blue markers are distinct from the numbered red region points. The map has no printed scale/CRS/semantic legend identified. No metric coordinate is extracted from image pixels. Map labels were inspected at original image resolution; unclear pixel engineering geometry remains EXTRACTION_UNVERIFIED and is not used. Native DOC table count is zero; the matrix is the separate XLS.

## Ambiguities And Boundaries

Continuous siting space, exact permitted corridors, obstacles, construction intersections, precise equality tolerance, goods arrival times, train fleet circulation, transfer handling concurrency, park dispatch scope and rules for primary nodes that are not nearest to any park are not fully specified. Assumptions are frozen separately in assumptions.md. None is rewritten as GIVEN. Supply completeness does not make operational closure automatic.
