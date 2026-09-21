# Q2 Network Design And Routing

| Reference | Candidate / constructed edge semantics | Design versus routing | Status and limits |
|---|---|---|---|
| F10256001 pp17-25 |Hierarchical park/core/local links; geometric PSO candidates |Bilevel formulation; PSO then flow/cost evaluation |HEURISTIC, not certified global; edge eligibility and candidate trace incomplete |
| F10294003 pp18-26 |Main/subnetwork geometry, track choices using larger direction |Sequential construction then aggregate transport |Approximate; authors qualify optimum p34; adjusted OD |
| F10486024 pp17-22 |Fixed four-primary ring; complete local geometric candidate sets for MST |Flow splits and track types jointly optimized **inside ring**, local design separate |Restricted MIP plus MST, not global network optimum |
| F10703002 pp18-24 |Manual star/grid and GA route encoding |Network structure chosen then distance/time optimization |HEURISTIC; physical capacity/cost certificate incomplete |
| F10710008 pp11-14,23 |Four park links, complete four-primary core, direct own-parent feeders |Locations then fixed topology and aggregate routing |Topology explicitly not optimized; not joint global design |
| F90005027 pp18-34 |2^21 local adjacency choices in fixed seven-node groups; fixed primary core |Adjacency enumeration with inverse-length route split and feasibility rejection |Exhaustive only within restricted groups and fixed flow-assignment rule |
| FK0263 pp21-33 |Park-to-associated primary; local complete geometric candidates; six possible core links |MST then tracks; core chain cost comparison; Q3 expands primary candidates |3^4/5^4 site combinations;66 retained Q3 cases; finite restricted enumeration |
| run-002 |Separate candidate/built edges;464 park-primary,538 core,118 feeders |Heuristic facilities/topology; fixed-design continuous multicommodity LP |1120 physical tunnels/2240 arcs; LP OPTIMAL only for fixed design; eight accepted deletions |

## Why Edges May Exist

Original rules admit new underground construction, unrestricted inter-node
distance and specific layer connections. This permits an **assumed candidate
corridor** between eligible endpoints, not an already existing tunnel or a
surveyed engineering guarantee. Within-layer all-pairs may be a useful design
superset if labeled as candidates; it is not justified as existing topology
merely by available distances. None of these papers supplies a complete GIS
obstacle, geotechnical, intersection and minimum-radius eligibility audit.
Run-002 explicitly retains this engineering uncertainty. The reference set
does not remove it.

Run-002's neighbor/connecting-tree/high-demand-peer sparsification is an
assumed candidate design, with graph data, provenance and built flags. It is
not derived from a source3km tunnel threshold. Reference candidate rules are
mostly implicit geometric supersets or explicitly restricted topologies;
there is no consensus proving a particular candidate-generation algorithm.

## Geometry And Weights

All seven use supplied planar centre geometry or constructed coordinates as
Euclidean proxies, not verified road or curved-tunnel paths. Source coordinates
are metres; cost uses kilometres. CRS/projection and underground obstacles
remain unspecified. Coverage radius, physical tunnel length, shortest network
path, travel time and monetary cost must stay distinct. F10703002's combined
time/money objective and uncalibrated network capacity are reference weaknesses;
they do not justify weakening run-002's unit audit.

Two arcs can represent a bidirectional physical tunnel. Their flow may differ;
shared physical construction cost is charged once. Track symmetry does not
symmetrize demand. No examined reference gives verified evidence that deleting
only a forward arc while retaining the failed tunnel's reverse arc is correct.
Where its removal representation is unspecified, this review says UNVERIFIED,
not that the mistake definitely occurred.

## Quality Versus Capability

References demonstrate useful search alternatives, especially hierarchical
sharing and FK0263's expanded primary choice. They do not prove that a specific
MST, GA, MILP or joint solver was mandatory. Network design and routing are
separate decisions even when solved by decomposition. Run-002 makes that
distinction explicitly, discloses its limitations, and re-routes accepted
deletions before cost comparison. Its incomplete operational result remains
conditional; static LP feasibility is not promoted to full solution feasibility.
