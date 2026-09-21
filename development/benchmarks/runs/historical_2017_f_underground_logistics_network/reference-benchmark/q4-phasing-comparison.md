# Q4 Phasing, Saturation And Expansion

Source: approximately30years,5% annual freight growth, eight years of roughly
equal tunnel construction length. Construction work, commissioned links,
available stations, service and terminal clearance are separate objects.

| Reference | Construction phases | Annual feasibility evidence | Growth / saturation | Expansion output and limits |
|---|---|---|---|---|
| F10256001 pp34-44 |Eight annual maps; DP-style priority; initial four disconnected spokes |p44 admits plan not validated; no annual flow/clearing |Utilization/nominal line capacity; no common frozen-routing year |Named upgrades/additions pp42-43, but no verified yearly service |
| F10294003 pp31-32 |3years primary core,2years park links,3years feeders |Incomplete intermediate service; no annual capacity replay |5% growth; proposes all10t and longer daily operation |Extra primary stations discussed without final located/routed/timed plan |
| F10486024 pp26-40 |AHP/entropy/TOPSIS priority and eight-year diagrams |No yearly flow/commissioned OD certificate; p40 admits limited validation |30year top-level design; changed10t legends |Additional nodes and drawn connections, not complete source-constrained expansion |
| F10703002 pp29-32 |Greedy/ACO evolution discussion |No auditable8year schedule |76240.97346->313818.1846 is approximately29 growth steps (rounding difference0.0001t) |Extra primary+six secondary asserted; no yearly costed operational proof |
| F10710008 pp20-28 |Three10year phases, not8annual phases |No intermediate-year flow/clearing |5% growth with fuzzy alternatives |Located B1/A2/B3 options and new capacities; source8year contract not established |
| F90005027 pp43-52 |Eight-year lists; nodes explicitly before incident links |Served-fraction/length plots; no yearly capacity-feasible route replay |Base year1,1.05^(n-1); narrative18 vs table17; all-four-track upgraded criterion |Adds links and five groups; annual tolerance0.1L is loose; no timed proof |
| FK0263 pp38-41 |Priority by connectedness, hierarchy and demand;7sites/year |Equal site count does not imply equal length; no annual commissioned-flow certificate |1.05^30, surface capacity also grows;20% reserve saturated at4 growth steps |55sites/fifth relay, doubled6000/8000 ground caps, cycles; changed assumptions |
| run-002 |Exactly equal work1086.520217084km/year, unfinished tunnels unusable |Node commissioning and active backbone checked; routes throttled, unmet freight explicit |Source year0,1.05^y; unchanged retained-routing static saturation year2 |No located/costed/routed30year design;432 modules are only a conditional bound |

All seven reference rows receive `PHASED_NETWORK_FEASIBILITY_UNVERIFIED` for the
**full source-target annual service/flow/capacity/clearance contract**. This does
not erase partial strengths: F90005027 explicitly respects node-before-link
dependency; several papers list actual annual links or new sites. Nor is a
temporarily disconnected construction network inherently illegal if only
partial service is claimed and accounted for. The missing step is showing what
the active network can actually serve each year.

## Frozen Annual Outcome

Run-002 preserves equal work across years and allows a project to cross a year
boundary, but a tunnel carries flow only after completion. Underground served
fractions are0.177277,0.471822,0.637780,0.686736,0.703482,0.731649,0.724938,
0.730981; source regions with residual congestion>4 number82,37,11,8,6,4,5,3.
The full target fails every year. These remain failed target checks, not a
successful8year plan. No reference evidence authorizes relabeling them.

## Saturation Is Criterion-Dependent

Year2 in run-002 refers to first violation under **unchanged design and retained
static routing**, with source atyear0 and aggregate station calls. It is not
the first year in which every possible routing/schedule is infeasible.
F90005027 assumes enlarged track capacity and10t primary capacity and changes
the base-year index; its reported18 is internally inconsistent with17 in its
table. FK0263's4 concerns a separately designed20% reserve margin. These are
`NOT_DIRECTLY_COMPARABLE`, not evidence of a16year performance gap.

## Capability Judgment

No reference demonstrates a generic stage-feasibility rule missing from the
current Skill and causing an unrecognized invalid run-002 claim. Existing
dependency, feasibility, transition and evidence rules can express commissioned
assets and per-stage service. Run-002 did so but did not solve the complete
expansion problem. Multistage solution quality remains WEAK; rigorous failure
disclosure must not be confused with a completed expansion.
