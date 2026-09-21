# Full-Set Review Notes

Read together with [source-ledger.md](source-ledger.md). `REFERENCE_WEAKNESS`
means either an identified inconsistency or missing evidence, as specified.
It does not imply that every unreported check failed. No appendix program was
executed and no reference's tables were substituted for original source data.

## F10256001 (pp1-68)

Q1 (pp6-16) maps regions to centre sites, with shared primary-secondary groups:
8 primary and22 secondary, rather than one primary for every secondary. The
91.71% result is map-area coverage (269.40/293.76 km2, p14), not run-002's full
centre-coverage contract. Return freight equality is assumed (p6). Distance and
freight are combined at0.5/0.5 (p9). Appendix pp51-52 **does** normalize each by
its maximum and symmetrizes freight for clustering. Thus arbitrary weight
preference and OD symmetrization are review issues, but alleging an entirely
unnormalized clustering objective would be wrong. Congestion/DEA results do not
establish directed OD conservation. Only four nearest-park primaries receive
park transfer ratios (p15); additional primaries exist without separate park
denominators, relevant to run-002's N/A fields.

Q2 (pp17-25) is bilevel in exposition, solved by PSO, with heuristic search
rather than a certified global optimum. p20 eq34 uses daily inflow=outflow as
daily clearing; it lacks release, transit completion, queues and transfer
precedence. Static balance is necessary but not sufficient. The triangular
capital sum does not establish physical tunnel double counting. Transport has
a separate /2 convention whose freight aggregation needs reconciliation.

Confirmed displayed contradictions: Table7 pp23-24 labels primary ground
in/out. Node817 totals4146.554t,870 totals6313.291t,832 totals4139.420t and853
totals4762.069t, above4000. Table9 p24 row894-898 gives1708.511+3201.405 but
prints4099.405, not4909.916. These are visual-verified table issues, not parser
errors. The annual5,756,533,247-yuan statement (p25) is not safely comparable to
run-002's daily cost boundary.

Q3 (pp26-33) optimizes risk/satisfaction and distance with SA, not actual
dispatch. Some primary-primary links are labeled10t (p32), unlike source5t
vehicle semantics. Q4 (pp34-44) supplies annual drawings and named future
upgrades. Year1 has four separate park spokes (p36), so a plotted construction
stage is not full OD service. p44 explicitly acknowledges unvalidated eight-year
planning. Appendices pp45-68 include clustering/DEA/drawing programs, not a
timed clearance proof; stale37/67 counts (p56) are not silently reconciled.

Disposition: useful G5 search/hierarchy contrast; G4 capacity/claim weaknesses;
no evidence of a missing generalizable rule in the current Skill.

## F10294003 (pp1-50)

Q1 (pp7-17) uses movable circles and centroids, nearest-neighbor operations and
K-means to choose4 primaries and25 secondary stations. It does not impose the
original centres as the only possible sites. Congestion4 is used to estimate
relief demand; the500t/km2 threshold is an author choice. Three low-congestion
regions are initially exempted from underground need, although the final
service table includes866. Coverage, candidate generation and service-demand
selection must not be conflated. Table5-1 p16 assigns3576.821117t to a secondary
serving886/890, exceeding3000; the value also occurs in appendix p43.

Q2 (pp17-26) changes/rebalances OD and redistributes park residuals. It therefore
does not demonstrate preservation of the original directed OD. The direction
description in the body and row-origin-looking appendix p49 need reconciliation
with the source column-origin convention. A nominal5/hour *18hours *8vehicles
calculation gives90 trains/day,7200t for10t vehicles and3600t for5t vehicles per
track/direction. Four-track doubling has no shared station-dispatch certificate.
p25 correctly selects track size using the larger directional demand, but the
printed5t four-track formula contains a10 multiplier and reports7200. p26 also
says8 departures/hour, inconsistent with the preceding5/hour premise.

Cost uses transport1,124,925.52yuan/day, capital597.04 yi-yuan and depreciation
1%/360, giving a claimed2,783,300yuan/day; internal rounding/accounting deserves
reconciliation. The4.5 versus4 yi-yuan unit price references are inconsistent
(pp19,26). These are not a basis for asserting proven double physical costing.

Q3 (pp27-30) reports utilization/load metrics and location improvement, not a
timetable or capacity-certified failure replay. Q4 (pp31-32) proposes all10t
vehicles, extra primary capacity and longer than18h operation, changing source
constraints. A3+2+3 construction split does not certify yearly OD feasibility.
The authors themselves say the design is approximate rather than fully optimal
(p34). Appendices pp35-50 do not add timed clearing evidence.

Disposition: G5 sequential design/search differences and G4 audit weaknesses;
no valid direct cost or timetable superiority comparison.

## F10486024 (pp1-49)

Q1 (pp8-14) explicitly restricts110 candidates to region centres. It finds28
lower-level sites then chooses4 primary sites from them (pp12-13); Table2-5
p17 retains28 secondary-layer rows. Record the physical/functional counting
ambiguity. Four primaries plus24 remaining unpromoted sites is a possible
deduplicated interpretation, not a certified separate-station bill of materials.
Coverage uses centres for density<2000 and image inspection for denser regions
(p11); this mixed approximation is author-selected. Transfer-rate denominator
in eq1-12 p14 is park incoming+outgoing, unlike the source outgoing definition.

Q2 (pp15-22) fixes a primary ring and optimizes clockwise/counterclockwise
splits plus track classes inside it. Local MSTs are justified by asserted
construction-cost dominance, not by a proof of full objective equivalence.
There is genuine design/flow coupling inside the restricted ring; calling the
whole system a joint global optimum is not supported. The model max(B,C)
<=(A+1)*3600 (p19) and the same page's four-track **10t** table with roughly
12,800-14,000t/direction do not match source interprimary5t vehicle semantics.
This is a confirmed displayed model/table inconsistency.

Capital is annualized with a capital-recovery annuity (p17), not simply1%/365.
The published217340yuan/km sensitivity (p19) also cannot be treated as the
source's ordinary daily depreciation. Main component values must not be summed
across inconsistent accounting boundaries to fabricate a comparable total.

Q3 (pp23-25) proposes a relay at diagonal intersection and explicitly observes
that connected rerouting can overload remaining channels (p24). This is a
useful qualitative capacity-aware insight, not an actual restored-flow or timed
operation certificate. Q4 (pp26-39) uses AHP/entropy/TOPSIS and eight yearly
drawings, with all10t legends (p35); no yearly flow/capacity/clearance audit.
p40 admits Q3/Q4 evidence limits. Appendix pp41-49 includes interrupted-solver
status (p42), changed11000 station cap (p46), and34-candidate variants (p47)
whose mapping to a final expansion is incomplete.

Disposition: G2/G5 restricted mixed-integer design; G3 interpretation differences;
G4 capacity/accounting/expansion evidence issues.

## F10703002 (pp1-36)

Q1 (pp7-17) uses five geographic partitions, centre sites, AHP and manual
assignments. The abstract says5+27, whereas body/Q2 says5+24. Preserve
`CONFLICTING_COUNTS`. p7 mentions115 points and zero diagonal, while appendix
p33 processes110 regions; source actually has114 endpoints and3.44t diagonal
OD. Coordinate strings p13 and AHP weight ordering pp10-11 are inconsistent;
do not repair them by guessing. Table4.16 p14 gives secondary834=3200t against
the3000t ground service bound. Detailed rounded freight assignments do not
provide an exact directed aggregation audit. Five primaries have ratios, one
zero where a park is associated with more than one primary (pp16-17).

Q2 (pp17-24) uses GA route encoding and star/grid construction. A money+time
objective (p19) lacks a common unit or defended preference normalization. The
182 yi-yuan result has insufficient time-basis/accounting detail for comparison;
physical counting is unclear, not proven duplicated. Capacity is mostly symbolic.

Q3 (pp25-29) defines edge capacity from betweenness and degrees as
Cij=Bij*(ki*kj)^theta (p26), without a tonnes/time calibration. A selected
secondary failure and Dijkstra routes illustrate connectivity, not physical
capacity restoration. Surge is dismissed on assumed reserve, without a
quantified scenario. Main travel/wait formulas and appendix pp35-36 time/vehicle
fragments warrant `PARTIAL_OPERATION_MODEL`, but those fragments have no
demonstrated full-network state/dispatch/terminal correspondence.

Q4 (pp29-32) discusses greedy/ACO expansion, an extra primary and six secondary
stations; it does not produce a validated8year annual schedule. The displayed
76240.97346 to313818.1846 growth ratio corresponds to29 growth steps, so the
base-year convention matters. The appendix is not a full dispatch certificate.

Disposition: G4 semantic/consistency and operational evidence weaknesses;
G2 algorithm differences, not a reason to add GA or a network platform.

## F10710008 (pp1-34)

Q1 (pp6-11) has four park partitions, continuous freight-weighted primary
centres, greedy coverage and23 secondary sites, later recentered. p6 expressly
ignores intrazonal freight; p7 excludes low-congestion areas. Service tables
pp9-10 repeat806/848/899 without clear fractional allocation reconciliation.
The arithmetic weighted centre is not a demonstrated optimizer of the stated
weighted Euclidean max-distance objective (p8).

Q2 (pp11-14) fixes four park links, complete primary connectivity and star
feeders. p23 admits that connectivity itself was not optimized. Primary OD is
asymmetric (p12), but regional totals in Table9 are symmetric without a
documented directional reconciliation. Ninety departures/day are used as
nominal capacity, not a shared-resource timetable. The407wan-yuan/day claim
uses1%/365 but mixes printed component units (pp13-14). Physical links are
listed once; ambiguous transport factor2 is not proof of duplicated capital.

Q3 (pp14-19) calls residual-capacity fraction a probability, uses serial/parallel
probability products (p15), and reports15%/35% gains. Visual verification of
appendix p31 confirms availability values **1.003,1.087,1.045**, and OD
availability1.176. These contradict a probability interpretation. Shared edges
also prevent automatic independence. Surface fallback with a promoted station
does not demonstrate underground capacity-feasible restoration.

Q4 (pp20-23 and appendix pp24-28) uses three10-year phases rather than an8year
annual schedule; fuzzy weights(.30,.26,.17,.13,.14) are author assumptions.
Located expansion alternatives exist and B1/A2/B3 are selected, so it would be
wrong to say no locations are supplied. However routed, costed and timed annual
feasibility is absent. Remaining appendices pp29-34 provide metrics/code, not
a timetable.

Disposition: G5 restricted topology; G3 protocol differences; G4 metric and
evidence weaknesses. No transport-time superiority follows from availability.

## F90005027 (pp1-54)

Q1 (pp8-17) uses geometric circles and an area-sum<=9pi surrogate, selects
four nearest-park primaries and24 secondary stations, then assigns hierarchy.
p9 explicitly takes rows as outgoing; no source transpose is documented.
The area-weighted congestion average (p13) can conceal a region hotspot.
For secondary nodes eq18 p14 states Si=Wi*, where Wi* is ground-diverted
freight and eq16 bounds it by3000. Thus Table4.3 p16 valuesS3=3040.832,
S4=3064.49,S6=3354.1796,S15=3212.684 are inconsistent with the paper's own
ground-capacity definitions, not merely transit throughput above3000.

Q2 (pp18-34) enumerates2^21 adjacency patterns for fixed seven-node groups,
with a prescribed primary core. BFS enumerates paths, and inverse-length
allocation fixes routing. This exhausts only that restricted family, not joint
network-flow design. Candidate rejection before objective comparison (p30) is
a useful strength. Upper-triangular physical-edge costing is explicit; do not
allege automatic double counting. The displayed depreciation objective
pp23/28 omits a separately defined station term, requiring reconciliation.
p29 static balance and5(k+1)<=120 connect station and line rates, but do not
model within-day completion or transfers.

Q3 (pp35-42) shows actual before/after rerouting tables for selected failure
(p40), suggests named backup links, and adds a fifth primary. This is stronger
than a connectivity drawing alone but not an exhaustive feasible recovery
certificate. The length-times-cumulative-multihop-tonnage deterioration factor
(p37) risks counting hops twice. About25% distance improvement concerns selected
paths, not a same-OD systemwide clearance/time gain.

Q4 (pp43-52) uses base year1 and1.05^(n-1), assumes all links four-track and
primary10t capacity; this is not run-002's retained-routing saturation criterion.
Table7.1 p44 gives F4 and S16 saturation17 while the narrative says first18.
This is a table/narrative conflict, **not** a maximum-of-years calculation.
Additional links and five groups are described. p50 explicitly commissions
nodes before links, which is a reference strength. Its annual tolerance0.1L is
80% of the annual targetL/8, not10% of that target. Lists and served-fraction
plots do not prove yearly capacity/flow/clearing. pp53-54 acknowledge modeling
limits and give references, not executable schedules.

Disposition: G5 restricted exhaustive search; useful partial design/validation
ideas already expressible under existing contracts; G4 arithmetic/OD/claim issues.

## FK0263 (pp1-63)

Q1 (pp6-20) explicitly assumes centre-only candidates; coverage of a centre is
not proof that centre-only siting is without loss of generality (p10).
Fractional Yij preserves assignment shares in the stated set-cover model.
Four primaries and23 secondary stations cover congestion-relief demand;866,
895,896 have no underground requirement in this model. Primary choices are
restricted to3 nearest candidates perpark (81 combinations), not global siting.
Park exchange is preferentially underground; total72307.06097t versus original
park two-way throughput128865.538t motivates a common56% allocation estimate.
Transfer denominator changes from total park output to underground output
(pp17-18). The resulting ratios are not automatically source-protocol ratios.

Q2 (pp21-32) correctly distinguishes vehicles from trains and uses acceleration
and travel time to reduce one park line from90 to89 daily departures (p22).
This is real partial operational reasoning, but no integrated dispatch,
transfer, shared station queue or train-precedence proof follows. The same page
chooses equal underground freight in both directions because track counts are
equal; symmetric infrastructure does not imply symmetric demand. This can be
a selected service policy with surface residual, but not preservation of all
original directed OD. Core OD uses approximate common fractions (pp26-27).
Appendix comments use5.63% (p44) while the body uses15.86% (p27), another
reconciliation issue.

Local MST then track sizing is explicit decomposition (p23). The primary
chain is chosen using construction versus detour cost (pp28-29), rather than
blindly equating MST with minimum total cost. The30 physical links and daily
248.13wan-yuan component sum are relatively transparent (pp31-32). This
supports a useful scoped comparison, not cost dominance over full-service
run-002. Table5.4.1 p30 swaps the primary3/4 subordinate lists relative to the
earlier regional maps/tables; preserve this inconsistency.

Q3 (pp33-38) expands primary choices to5^4=625, retains66 candidates under
stated capacity tests, obtains228.6081wan-yuan/day, and separately designs20%
reserve using2500/6000 limits with31 stations at211.48wan-yuan/day.20% is
`SCENARIO_ASSUMED`. Proposed five extra links create cycles; resilience is
inferred mainly from alternate paths, not solved capacity-feasible failures.

Q4 (pp38-41) assumes surface capacity growth5% and doubles ground station
limits to6000/8000;55 stations include a fifth relay. Candidate drawings and
new locations are real, but these changed assumptions cannot validate a
source-constrained30year expansion. Fleury names an Euler traversal, not a
proof of a shortest feasible physical cycle. Seven nodes/year does not enforce
equal tunnel length or annual service. Year4 saturation concerns the20% reserve
scenario:1.05^3<1.2<1.05^4. Appendices pp42-63 contain set-cover/MST/plotting
and bounded search code, not a complete timetable.

Disposition: strongest explicit restricted search contrast, G5; partial
single-link time reasoning does not reveal a missing terminal-state rule, since
current stateful scheduling already requires it.
