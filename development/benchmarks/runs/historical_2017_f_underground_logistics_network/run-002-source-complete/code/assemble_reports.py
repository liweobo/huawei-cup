"""Build numeric report tables directly from saved result components."""
import csv
import json
import platform
import sys
from importlib.metadata import version,PackageNotFoundError
from pathlib import Path

RUN=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(RUN/"work/deps"))


def read(name):
    return json.loads((RUN/name).read_text(encoding="utf-8"))


def write(name,text):
    (RUN/name).write_text(text.strip()+"\n",encoding="utf-8")


def table(headers,rows):
    return "\n".join(["| "+" | ".join(headers)+" |","| "+" | ".join(["---"]*len(headers))+" |"]+
        ["| "+" | ".join(str(x) for x in r)+" |" for r in rows])


audit=read("results/input-audit.json"); d=read("results/primary/design.json"); nodes=read("results/primary/node-results.json")
cost=d["cost"]; base=read("results/baseline/design.json"); consolidated=read("results/q1-primary/design.json")
ind=read("results/independent-audit.json")[-1]; op=read("results/q3-operations.json")
phase=read("results/q4-annual.json"); build=read("results/q4-build-plan.json"); sat=read("results/q4-saturation.json")
failure=read("results/q3-failures.json"); ratios=read("results/primary/transfer-ratios.json")
solver=read("results/primary/solver.json")
comparisons=table(["Design","Primary","Secondary","Physical tunnels","Daily yuan (conditional static objective)"],
    [[label,x["n_primary"],x["n_secondary"],len(x["edges"]),f'{x["cost"]["total_daily_yuan"]:,.6f}'] for label,x in
     [("Real-data baseline",base),("Consolidated",consolidated),("Eight deletions",d)]])
write("baseline.md",f"""# Real-Data Baseline

Per-region allocations with2000t constructive fill target, one primary per
secondary, four park spokes and a connected sparse primary backbone. Every
original directed off-diagonal OD is preserved. This is a real-data static
baseline, not a synthetic oracle or certified operating timetable.

{comparisons}

The3000/2400t attempts were rejected as LP-INFEASIBLE. Changing source station
capacity was not allowed. The diagnostic900-departure relaxation is excluded.
The baseline and primary have identical source bytes, service policy, resource
limits, train configuration and objective boundary. Consolidation changes only
design/assignments; accepted tunnel deletions reroute all commodities.
The baseline is a valid static relaxation comparator, not a fully legal
daily-clearing solution to all of Q2.
""")
write("input-audit.md",f"""# Independent Original Input Audit

Status: PASS for the recovered essential source set. Native XLS cell equality
between xlrd and python-calamine is exact; no missing or negative/nonfinite OD.
DOC and JPG were separately rendered/viewed, not inferred from prior solutions.

{table(["Item","Observed"],[
    ["OD", "114 x 114; IDs1-4 and791-900"],
    ["Convention","Column origin, row destination"],
    ["Asymmetric unordered pairs",audit["asymmetric_pairs"]],
    ["Total tonne/day",audit["daily_tonnes"]],
    ["Park-related tonne/day",audit["park_related_tonnes"]],
    ["Diagonal","895:2.92;896:0.52 tonne/day, preserved"],
    ["Region congestion range",audit["congestion_min_max"]],
    ["Blank park attributes","12 cells across two area units and congestion; no imputation"],
    ["Coordinates","metres; CRS/origin/projection not given"]])}

Region areas are retained but not required for the explicit centre-coverage
approximation. Covering a centre does not assert whole-polygon coverage.
Uncalibrated map pixels are not metric inputs. Original sheets, IDs, source
cells and units remain in source-manifest.json, node-ledger.md, demand-ledger.md
and inputs/*.csv. See results/input-audit.json for machine checks.
""")
write("q1-results.md",f"""# Q1 Results

Status: PARTIAL at whole-question level; valid conditional allocation/count/
location/throughput outputs. All110 centres are served within3km. The restricted
layout has118 primary and118 secondary stations; primaries have zero ground
exchange, while secondaries handle the allocated regional exchange.
This expensive one-to-one hierarchy is not a recommended optimal facility plan.

{comparisons}

Every station's actual coordinates, source seed, parent, region allocation,
radius, ground exchange and underground inbound/outbound are saved in
results/primary/node-results.json. A readable complete table is node-results.md.
Regions may split across stations; assignment fractions sum to one.
B=M.T D_offdiag M preserves all off-diagonal demand.

Park transfer ratios use Euclidean nearest-primary distance:

{table(["Park","Nearest primary","Numerator t/day","Denominator t/day","Ratio"],[
    [r["park"],r["nearest_primary"],f'{r["numerator_t_day"]:.6f}',f'{r["denominator_t_day"]:.6f}',f'{r["ratio"]:.9f}'] for r in ratios["by_park"]])}

For primary stations nearest to no park the source denominator is undefined.
All are explicitly listed as NOT_APPLICABLE_NO_ASSOCIATED_PARK_DENOMINATOR,
not assigned a fictitious0 ratio. This unresolved meaning of the requested
per-primary ratio prevents claiming all Q1 outputs unconditionally complete.
Known region diagonal3.44t/day remains local surface freight. Co-assigned
station-local{d["station_local_t_day"]:.9f}t/day has no tunnel movement but
remains accounted as station ground handling.
""")
write("node-results.md","# Complete Primary-Design Node Table\n\nCoordinates km; freight tonnes/day. Pxxx is parent of Sxxx. Detailed region fractions/radii are in results/primary/node-results.json.\n\n"+
    table(["ID","Type","X km","Y km","Ground exchange","Underground out","Underground in","Static departures"],
          [[n["id"],n["type"],f'{n["x_km"]:.6f}',f'{n["y_km"]:.6f}',n.get("ground_exchange_t_day","N/A"),
            f'{n["underground_out_t_day"]:.6f}',f'{n["underground_in_t_day"]:.6f}',n["rounded_departures_day"]] for n in nodes]))
write("q2-results.md",f"""# Q2 Results

Status: PARTIAL. Final design is STATIC_FEASIBLE_CONDITIONAL_DESIGN_NOT_TIMETABLE.
Joint facility/network optimality is not proved. Algorithm:
HEURISTIC_BEST_FOUND among the evaluated designs, with OPTIMAL_FIXED_DESIGN_LP
only for each accepted continuous routing subproblem.

{table(["Component","Value"],[
    ["Physical tunnels",len(d["edges"])],["Physical length km",f'{build["total_final_length_km"]:.9f}'],
    ["Directed arcs",solver["directed_arcs"]],["LP variables",solver["variables"]],
    ["LP equality rows",solver["equality_rows"]],["LP inequality rows",solver["inequality_rows"]],
    ["Origin commodities",solver["commodities"]],["Routed transport yuan/day",f'{cost["underground_transport_yuan_day"]:.9f}'],
    ["Access proxy yuan/day",f'{cost["access_proxy_yuan_day"]:.9f}'],
    ["Tunnel depreciation yuan/day",f'{cost["tunnel_depreciation_yuan_day"]:.9f}'],
    ["Station depreciation yuan/day",f'{cost["station_depreciation_yuan_day"]:.9f}'],
    ["Total yuan/day",f'{cost["total_daily_yuan"]:.9f}']])}

Double-track park-primary tunnels have10t vehicles, others5t. Eight cars/train
is an explicit chosen configuration. Construction is counted once per physical
tunnel, not once per arc. Depreciation is capital*0.01/365, with no extra division
by100-year life. Source transport price1yuan/(tonne km) is additive; local access
is a separately declared Euclidean proxy, not measured road cost.

All1120 physical corridors, lengths, types, costs and both directional flows
are in results/primary/tunnel-results.json. Detailed origin commodities and
paths are in compressed audit-friendly flow and route files. Station max84
rounded departures/day and line max32/direction/day pass aggregate limits.
Ground exchange and directed flow balance pass the independent audit.

The daily cost falls{100*(1-cost["total_daily_yuan"]/base["cost"]["total_daily_yuan"]):.4f}% relative to baseline.
This comparison does not establish the unrestricted minimum or feasibility of
full daily clearance. The operating queue tests leave freight unfinished.
""")
write("q3-results.md",f"""# Q3 Results

Status: PARTIAL; real-network operations and scenarios executed, not a complete
validated improvement of all node counts, levels, routes and interruptions.
The initial consolidation reduced150+150 to118+118 stations. Eight subsequent
physical park-link deletions strictly reduced the realized static daily cost.
See search-trace.json for all proposals, feasibility and incumbent history.

{table(["Transfer handling min","Delivered t","Queued t","Transit/handling t","Delivered fraction","Mean time of delivered freight min"],
    [[r["handling_min"],f'{r["delivered_t"]:.6f}',f'{r["queued_t"]:.6f}',f'{r["in_transit_or_handling_t"]:.6f}',
      f'{r["delivered_fraction"]:.9f}',f'{r["mean_delivery_time_delivered_min"]:.6f}'] for r in op])}

Both greedy policies fail full18-hour clearing. Train legs were independently
replayed: payload, station12-minute spacing, directional2-minute spacing,
precedence and freight conservation pass. These are optimistic constant-speed
scenarios with unlimited fleet/queues and all freight available at t=0.
They do not include acceleration, empty returns, final unloading or finite
switch resources. Mean time is conditional on delivered freight, not all demand.
A failed greedy policy is not a certificate that every possible timetable fails.

Exhaustive single physical-tunnel removal: {failure["count"]} scenarios.
Each removes both directed arcs. Worst reachable routed-demand fraction is
{failure["worst"]["reachable_routed_endpoint_fraction"]:.12f}; disconnected
scenarios: {failure["disconnected_scenarios"]}. No failure probability is assumed.
Reachability does not imply capacity-feasible rerouting or finite-fleet service.
Own-primary secondary feeders are single points of service failure.

Park1 outgoing-only surges+10%/+25% keep retained-route static capacity feasible
(max85 station departures). Four-car trains require160 departures at the worst
station, exceeding90 by70; this scenario is rejected, not absorbed by penalty.
Applying a90-departure limit to each park would cap outbound service at7200t/day
per park and make full park diversion impossible under that interpretation.

Position offsets125/500m are cost-only sensitivities, not adopted designs.
Deleting S117 without reallocation loses132.773t/day exchange and is rejected.
Demoting a primary while retaining park links violates the modeled hierarchy.
An additional independent same-parent feeder is only a proposed repair, not
constructed or validated. No generic random-failure probability model is added.
""")
write("q4-results.md",f"""# Q4 Results

Status: PARTIAL. Source day is t=0; construction year y demand multiplier1.05^y.
Q2 design stays frozen. Equal annual construction work is
{build["annual_target_km"]:.9f}km/year. Divisible work may span years, but tunnels
remain unusable until fully completed. All tunnels depend on commissioned
endpoints; station commissioning years are independently reconstructed.

{table(["Year","Demand multiplier","Completed tunnels","Underground share","Regions above congestion4","Full target"],
    [[r["year"],f'{r["demand_multiplier"]:.9f}',r["completed_tunnels"],f'{r["underground_fraction"]:.6f}',
      r["regions_above_basic_freeflow"],r["full_target_pass"]] for r in phase])}

Commissioned primary backbones are connected. Usable saved routes are uniformly
throttled until ground/station/line capacity passes, and all remaining freight
is explicitly surface fallback. This is service accounting, not a full-target
construction recommendation. Every year fails the full target; no partial
network is called capable of clearing its total original demand underground.
Timed annual operations, station build durations and annual budgets are not
established by this static phasing model.

Unchanged full-design retained-routing first static saturation:
year{sat["first_saturation_year"]}. This is not a reoptimized-routing upper bound.
Thirty-year multiplier={1.05**30:.9f}; status SATURATES_BEFORE_30_YEARS.
At least{sat["expansion"]["additional_modules_lower_bound"]} additional parallel-equivalent
station modules would be needed under retained per-node loads. This is a
resource lower-bound scenario, not a feasible expansion layout or timetable.
Four tracks alone cannot cure a station-dispatch bottleneck. Any further design
must explicitly add locations/corridors, reallocate OD and validate yearly
operations; no such future expansion is silently inserted into Q2.
""")
write("network-audit.md",f"""# Network Audit

Independent checker code/independent_audit.py imports no solver/model helper.
It reloads source CSVs, allocation, physical edges, commodity flows and routes.
All three evaluated complete static designs pass their declared static audits.

{table(["Final primary audit","Result"],[
    ["Nodes / physical edges / arcs",f'{ind["node_count"]} / {ind["physical_edge_count"]} / {ind["directed_arc_count"]}'],
    ["Graph / primary components","1 / 1; no isolates"],
    ["OD reachability",ind["od_reachability"]],
    ["All110 centre coverage",ind["allocation_coverage"]],
    ["Max commodity balance residual t/day",ind["maximum_flow_conservation_residual_t_day"]],
    ["Max path OD residual t/day",ind["maximum_path_od_residual_t_day"]],
    ["Ground / station / line violation","0 / 0 / 0 (static)"],
    ["Rebuilt objective discrepancy yuan/day",ind["objective_difference_yuan_day"]],
    ["Physical costing","one charge per physical tunnel"],
    ["Daily clearing","FAIL for both tested queue policies; static result not upgraded"]])}

Graph symmetry concerns physical directions only: two legal arcs per tunnel.
OD and directional flows remain asymmetric. Candidate corridors are explicitly
assumed, not existing infrastructure. Positive finite Euclidean lengths permit
the small-graph and decomposition path algorithms; capacities are not additive
weights. No engineering crossing/curve-radius feasibility is claimed.

Independent operation/phase replay additionally verifies train payloads,
headway, route precedence, terminal mass accounting, annual construction work,
endpoint commissioning, active-primary connectivity, original-OD disaggregation
and capacity with surface fallback. This passes accounting but all annual full
targets fail. Failure scenarios are topological sensitivity, not restoration
proof. No hidden demand is deleted.

Both generated figures were visually inspected after rendering. Their graph
and yearly data come solely from this run. Dense station IDs are provided in
node-results.md rather than overlapping labels on the overview plot.
""")
packages={}
for name in ["numpy","scipy","networkx","xlrd","python-calamine","matplotlib","pytest","PyYAML"]:
    try: packages[name]=version(name)
    except PackageNotFoundError: packages[name]="not discoverable in active metadata"
write("environment.json",json.dumps(dict(python=sys.version,platform=platform.platform(),packages=packages,
    randomness="deterministic; no random seed used; HiGHS tie solutions may differ across versions"),indent=2))
print("Generated source-bound numeric tables and per-question reports")
