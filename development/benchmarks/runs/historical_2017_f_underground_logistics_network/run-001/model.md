# Conditional Model And Executed Oracle

Claim level: PARAMETRIC for the original problem; SYNTHETIC_CODE_VALIDATION for executed networks. Missing essential input stops formal model confirmation under `analyze-problem` and `design-model`. The formulation below is reviewable but is not a solved Nanjing plan.

## Q1 Node Choice And Demand Allocation

Let Z be original freight regions with centres c_i, congestion I_i and directed demand D_ij; P the four parks; J eligible possible station sites. None of these numeric sets is available. Selecting only centres as sites would be an additional discretization with location error, so no such restriction is silently imposed.

DESIGN VARIABLES: y_j^H,y_j^S in {0,1}, y_j^H+y_j^S<=1; site locations x_j if continuous; radii 0<=r_j<=3 km; region assignment a_ij; secondary-primary membership b_jh; park-nearest-primary assignment n_ph. Assignment is possible only when a station is selected and the audited coverage distance is within r_j. Nearest ties need an explicit deterministic or optimized rule. Four parks need not imply four primaries.

FLOW/ALLOCATION VARIABLES: u_od^ij>=0 is the portion of zone OD o->d assigned to station i->j; surface remainder s_od>=0; sum_ij u_od^ij+s_od=D_od. Assignments restrict valid endpoint stations. Ground exchange at a station is the sum of origin and destination transfers, not transit freight. Impose the 4000/3000 limits only after matching the OD time basis. Each region is either explicitly uncovered or assigned within coverage; no fractional hidden region deletion.

For baseline freight incidence T_i=sum_j(D_ij+D_ji), calculate I'_i=I_i*G_i/T_i, where G_i is remaining traffic-generating surface freight after the actual access/last-mile assignment. T_i=0 requires explicit treatment, not division by zero. F20 exempts secondary last-mile traffic only; primary ground access cannot be assumed traffic-free. A04 interprets 'basically unobstructed' as I'_i<=4. Among these feasible allocations maximize underground park freight, then compare cost and primary transfer ratios; this is a disclosed policy ordering, not a given 0.5/0.5 score.

For park p assigned to nearest primary h, phi_p = 100 * [p's outgoing tonnes transferred through h to other primaries] / [all p outgoing tonnes]. Preserve per-park numerators and denominators; any aggregation at a shared primary must be explicit. Undefined when denominator=0. Transfer rates cannot be obtained from centrality.

## Q2 Joint Tunnel Design And Flow

For each documented eligible corridor e={u,v}, choose x_eq in {0,1} among permitted track/vehicle options q; sum_q x_eq<=1. Investment is undirected; operating arcs u->v and v->u have independent flows and may have distinct travel times. Two bores/track counts are facility choices, not extra copies of the same construction cost.

For commodity k with station origin o_k, destination d_k and assigned tonnes U_k, choose directed arc flow f_k,uv>=0:

`sum_out f_k,vw - sum_in f_k,wv = U_k * (1[v=o_k]-1[v=d_k])`.

`F_uv = sum_k f_k,uv`; `F_uv <= sum_q C_eq,uv*x_eq`, separately for reverse flow. Dimensioning uses max(F_uv,F_vu) when directional capacities for the same symmetric physical option are equal. Capacity does not enter shortest-path additive weights.

Require selected primaries to be connected; secondary-to-foreign-primary paths must traverse the assigned own primary. A cut/separation check after removal of that primary verifies this semantic condition. Connectivity only for positive OD is insufficient because selected primary nodes have their own connectivity requirement. Infeasible disconnected solutions have no objective eligible for selection.

Train variables z_uv are integer departures, with 4-8 carriages per train, 10 tonnes per carriage on park links and 5 elsewhere. A conservative necessary bound is `sum_v z_uv<=90` departures/day per node (A05). Link headway imposes another bound. Four-track doubling of a running-line bound alone does not double a station's capacity. Transit is counted in train departures; it is not confused with ground-exchange limits.

Daily terminal inventory must be zero. To certify that, a future actual instance needs a feasible timetable or verified time-expanded flow with handling, travel, departure availability and transfers. Speeds, acceleration and minimum turn radius do not make static tonnage capacity sufficient. Empty-vehicle balancing and infrastructure resources remain operational assumptions to resolve.

Objective, yuan/day:

`J = sum_(directed arcs) F_uv * L_uv * 1 + surface/transfer transport components + (0.01/365)*(sum_e,q L_e*c_q*x_eq + 1.5e8*sum_j y_j^H + 1e8*sum_j y_j^S)`.

F is tonnes/day, L kilometres, 1 yuan/(tonne km). c_q is 4e8/5e8 yuan/km for 10t double/four track and 3e8/3.5e8 for 5t. The 365-day conversion is A02. Exclude park/node-in-park capital, include park tunnels. Do not double-count vehicle/equipment depreciation already included in the transport rate. Missing surface path lengths prevent reporting full multimodal total cost; a tunnel-only cost must carry that qualifier. No extra 1/100 after the given 1% depreciation.

## Baseline And Candidate Choice

Real baseline after input closure: a legal staged node/service allocation followed by a simple connected eligible tunnel structure, with explicit hierarchy and rerouted flows checked against capacity and timing. This is NOT RUN on original data. A fixed-network shortest-path assignment is only a routing baseline, not completed network design.

Candidate families compared conceptually: staged feasible construction (simple, may miss joint tradeoffs); joint discrete facility/corridor/flow optimization (aligned with objective, input dependent); few decision-semantic local changes after a feasible incumbent (conditional structured improvement, not yet activated on real data). Exact variable/constraint counts are unknown because real n,m,K are unknown. A fixed-node formulation uses roughly 2mK flow variables plus node, assignment, corridor-option and train variables; multi-period copies grow with the horizon. No claim that exact optimization is infeasible is made without actual scale.

Executed oracle: all sites, levels, five local/park corridors and six directional demands fixed by artificial inputs. Three possible backbone corridors are explicitly eligible. Baseline builds A-B and B-C. Enumerate 2^3 construction subsets; reject disconnected subsets. In each connected subset nonnegative shortest routes minimize unconstrained transport, and all resulting static capacity checks pass. Thus those lower bounds are attainable under the oracle's static constraints, and the lowest enumerated design is exactly optimal in that restricted model. This proof does not extend to binding-capacity instances, free locations, timetable feasibility or the original problem. No heuristic or commercial solver is required here.

Oracle geometry is explicitly Cartesian kilometres and tunnel lengths equal Euclidean lengths by test definition. Physical capital: 3 primary, 3 secondary, two uncharged parks. Ground limit/dispatch and running-capacity calculations are diagnostic necessary conditions. Oracle has 8 nodes, 8 candidate physical edges/16 candidate directed arcs, 6 OD pairs, 3 independent binary choices and 8 enumerated combinations. At most 96 commodity-arc entries, 48 node-commodity balance checks, 16 directional running bounds, 8 station dispatch bounds, 6 station ground bounds and 3 own-primary mediation checks. Route variables are computed for each design, not optimized independently of design selection.

## Q3 Improvement And Risk

For an actual feasible Q2 incumbent, permissible moves would open/close a station, move/reclassify a station with reassignment, or add/remove/replace an eligible corridor and reroute flow. Every proposal must rerun service, hierarchy, connectivity, capacity, timing and objective reconstruction before selection. These moves are a plan, not executed real-instance search. The tiny oracle exhausts its design space, so it does not need a heuristic structured-improvement contract.

Executed failure model removes one built physical tunnel in both directions; positive OD is rerouted if reachable. Record components, isolated nodes, OD fraction and demand-weighted reachable fraction; infeasible/lost OD never receives a finite all-demand cost. Report surviving-demand cost only as a conditional diagnostic. The comparison includes a redundant primary triangle. It protects the primary backbone against one backbone-edge outage, but leaves park and secondary branches vulnerable, so it is not a globally single-failure-tolerant network.

A +50% P_A->sC demand scenario changes one actual oracle OD direction, not random edges. It is GENERIC_SENSITIVITY_SCENARIO / SIMULATED_PERTURBATION; no observed surge frequency or risk probability. No scalar robustness-cost weight is invented. No centrality metric is used as a construction decision.

## Q4 Construction And Growth

Given base-year convention t=0, D_k(t)=D_k(0)*1.05^t. With fixed assignment/routes/capacity, the first overload year is the first integer t for which any demand-induced resource load exceeds its capacity. Equality and integer train rounding must be checked. This diagnostic cannot infer a city saturation year without base demands and design.

Conditional planning variables: x_e,t commissioned by year t (monotone); node openings y_j,t; added capacity q_e,t; annual routing f_k,e,t. Construction length in each of years 1..8 lies within `(1 +/- epsilon)*L_total/8`; epsilon must be agreed because 'roughly equal' has no numeric tolerance. Uncommissioned edges/nodes cannot carry freight. Flow/service/capacity constraints apply to every operational year, with final design tested through year 30. Intermediate service goals and treatment of unfinished corridors require assumptions. Compare Q3 and phased plans by annual feasible demand, congestion, expansion need, construction and operating cost separately unless discounting/preference is supplied.

This multi-period formulation is not an implemented action-sequence search. Stateful scheduling is not activated merely because routes are sequences; if future construction/operational actions depend on evolving available resources, use the existing stateful contract. No new scheduling or stochastic module is introduced.
