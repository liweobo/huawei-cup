"""Eight-node verification instance, not a substitute for the missing 2017F data."""
import copy
import itertools
import json
import math
import platform
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, dijkstra, shortest_path
import yaml

RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[4]
sys.path.insert(0, str(REPO))
from skill.scripts.data_audit import audit_file
from skill.scripts.robustness import run_robustness
from skill.scripts.runtime_provenance import apply_protocol_change, validate_experiment_record

OUT = RUN / "results"
OUT.mkdir(exist_ok=True)
DATA = json.loads((RUN / "inputs/oracle.json").read_text(encoding="utf-8"))
NODES = {n["node_id"]: n for n in DATA["nodes"]}
IDS = list(NODES)
INDEX = {name: i for i, name in enumerate(IDS)}
EDGES = {e["edge_id"]: e for e in DATA["candidate_edges"]}


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def graph(edge_ids):
    mat = np.zeros((len(IDS), len(IDS)))
    for eid in edge_ids:
        e = EDGES[eid]
        i, j = INDEX[e["u"]], INDEX[e["v"]]
        length = math.dist(NODES[e["u"]]["coordinate_km"], NODES[e["v"]]["coordinate_km"])
        if not math.isfinite(length) or length <= 0 or i == j:
            raise ValueError("Invalid positive tunnel length or self-loop")
        if mat[i, j] != 0:
            raise ValueError("Duplicate corridor in simple graph")
        mat[i, j] = mat[j, i] = length
    return mat


def analyze(edge_ids, od=None, degraded=False):
    od = copy.deepcopy(DATA["od"] if od is None else od)
    mat = graph(edge_ids)
    sparse = csr_matrix(mat)
    components, labels = connected_components(sparse, directed=False)
    dist, prev = dijkstra(sparse, directed=True, return_predecessors=True)
    routes, unreachable, conservation = [], [], []
    flows = defaultdict(float)
    for commodity, demand in enumerate(od):
        o, d, q = demand["origin"], demand["destination"], demand["demand"]
        assert q >= 0 and math.isfinite(q)
        if not math.isfinite(dist[INDEX[o], INDEX[d]]):
            unreachable.append({"commodity": commodity, **demand})
            continue
        cursor, route = INDEX[d], [d]
        while cursor != INDEX[o]:
            cursor = int(prev[INDEX[o], cursor])
            assert cursor >= 0
            route.append(IDS[cursor])
            assert len(route) <= len(IDS)
        route.reverse()
        balance = {v: 0.0 for v in IDS}
        for u, v in zip(route, route[1:]):
            flows[u, v] += q
            balance[u] += q
            balance[v] -= q
        for v in IDS:
            rhs = q if v == o else -q if v == d else 0.0
            conservation.append({"commodity": commodity, "node_id": v, "out_minus_in": balance[v],
                                 "source_sink_rhs": rhs, "residual": balance[v] - rhs})
        routes.append({"commodity": commodity, "origin": o, "destination": d, "tonnes_per_day": q,
                       "nodes": route, "km": float(dist[INDEX[o], INDEX[d]]),
                       "tonne_km_per_day": q * float(dist[INDEX[o], INDEX[d]])})

    edge_components, departures = [], defaultdict(int)
    for eid in edge_ids:
        e = EDGES[eid]
        u, v = e["u"], e["v"]
        length = mat[INDEX[u], INDEX[v]]
        vehicle_tonnes = 10 if e["edge_meaning"] == "PARK_PRIMARY" else 5
        train_tonnes = 8 * vehicle_tonnes
        running_capacity = (18 * 60 // 2) * train_tonnes
        cost_per_km = 4e8 if vehicle_tonnes == 10 else 3e8
        for a, b in ((u, v), (v, u)):
            departures[a] += math.ceil(flows[a, b] / train_tonnes)
        edge_components.append({"edge_id": eid, "u": u, "v": v, "meaning": e["edge_meaning"],
                                "length_km": float(length), "flow_u_v_tonnes_day": flows[u, v],
                                "flow_v_u_tonnes_day": flows[v, u], "design_directional_flow": max(flows[u, v], flows[v, u]),
                                "directional_running_capacity_tonnes_day": running_capacity,
                                "capital_yuan": float(length * cost_per_km),
                                "daily_transport_yuan": float(length * (flows[u, v] + flows[v, u])),
                                "hard_capacity_pass": max(flows[u, v], flows[v, u]) <= running_capacity})
    node_components = []
    for v, node in NODES.items():
        kind = node["node_type"]
        ground = sum(item["demand"] for item in od if v in (item["origin"], item["destination"])) if kind != "PARK" else 0
        ground_limit = 4000 if kind == "PRIMARY" else 3000 if kind == "SECONDARY" else None
        node_components.append({"node_id": v, "node_type": kind,
                                "ground_exchange_tonnes_day": ground, "ground_limit_tonnes_day": ground_limit,
                                "ground_capacity_pass": ground_limit is None or ground <= ground_limit,
                                "departures": departures[v], "dispatch_limit": 90,
                                "dispatch_capacity_pass": departures[v] <= 90,
                                "capital_yuan": 1.5e8 if kind == "PRIMARY" else 1e8 if kind == "SECONDARY" else 0})
    # Removing a secondary's own primary must eliminate all paths to other primaries.
    hierarchy = []
    for v, node in NODES.items():
        if node["node_type"] != "SECONDARY":
            continue
        cut = mat.copy()
        parent = INDEX[node["primary"]]
        cut[parent, :] = cut[:, parent] = 0
        from_secondary = dijkstra(csr_matrix(cut), directed=True, indices=INDEX[v])
        bypass = [p for p in IDS if NODES[p]["node_type"] == "PRIMARY" and p != node["primary"] and math.isfinite(from_secondary[INDEX[p]])]
        hierarchy.append({"node_id": v, "own_primary": node["primary"], "foreign_primary_bypasses": bypass})
    capital = sum(e["capital_yuan"] for e in edge_components) + sum(n["capital_yuan"] for n in node_components)
    transport = sum(e["daily_transport_yuan"] for e in edge_components)
    route_cost = sum(r["tonne_km_per_day"] for r in routes)
    capacities_pass = all(e["hard_capacity_pass"] for e in edge_components) and all(n["ground_capacity_pass"] and n["dispatch_capacity_pass"] for n in node_components)
    feasible = components == 1 and not unreachable and capacities_pass and all(not h["foreign_primary_bypasses"] for h in hierarchy)
    total_demand = sum(d["demand"] for d in od)
    lost = sum(d["demand"] for d in unreachable)
    result = {"scope": "SYNTHETIC_CODE_VALIDATION", "selected_edges": list(edge_ids),
              "node_count": len(IDS), "physical_edge_count": len(edge_ids), "directed_arc_count": int(np.count_nonzero(mat)),
              "components": int(components), "component_members": [[IDS[i] for i in range(len(IDS)) if labels[i] == label] for label in range(components)],
              "isolated_nodes": [IDS[i] for i in range(len(IDS)) if not mat[i].any()],
              "weight_symmetry_pass": bool(np.array_equal(mat, mat.T)), "directed_od_symmetry": False,
              "routes": routes, "unreachable_od": unreachable, "flow_conservation": conservation,
              "max_conservation_residual": max([abs(c["residual"]) for c in conservation] or [0]),
              "edges": edge_components, "nodes": node_components, "hierarchy_audit": hierarchy,
              "capacity_feasibility": capacities_pass, "static_feasible": feasible,
              "daily_operational_clearing": "NOT_VERIFIED", "engineering_constructability": "NOT_APPLICABLE_SYNTHETIC",
              "capital_yuan": capital, "depreciation_yuan_day": capital * .01 / 365,
              "transport_yuan_day": transport, "objective_yuan_day": capital * .01 / 365 + transport if feasible else None,
              "route_vs_arc_cost_residual": transport - route_cost,
              "od_reachable_fraction": (len(od) - len(unreachable)) / len(od),
              "demand_reachable_fraction": (total_demand - lost) / total_demand,
              "unreachable_demand_tonnes_day": lost,
              "failure_scope": "DEGRADED_SCENARIO" if degraded else "NORMAL"}
    assert result["max_conservation_residual"] < 1e-9
    assert abs(result["route_vs_arc_cost_residual"]) < 1e-8
    return result


def manual_oracle():
    matrix = csr_matrix(([2., 3., 9., 8.], ([0, 1, 0, 2], [1, 2, 2, 0])), shape=(4, 4))
    d = dijkstra(matrix, directed=True)
    expected = np.array([[0., 2., 5., np.inf], [11., 0., 3., np.inf], [8., 10., 0., np.inf], [np.inf, np.inf, np.inf, 0.]])
    assert np.array_equal(d, expected)
    assert np.array_equal(shortest_path(matrix, method="FW", directed=True), expected)
    cc, _ = connected_components(matrix, directed=True, connection="weak")
    assert cc == 2
    return {"status": "PASS", "nodes": 4, "arcs": [[0, 1, 2], [1, 2, 3], [0, 2, 9], [2, 0, 8]],
            "manual_expected_0_to_2": 5, "manual_expected_2_to_0": 8,
            "isolated_node": 3, "weak_components": int(cc), "independent_floyd_check": "PASS"}


record = yaml.safe_load((RUN / "experiment-record.yaml").read_text(encoding="utf-8"))
assert record["status"] == "PLANNED", "Do not overwrite an observed experiment silently"
assert not validate_experiment_record(record)
record["status"] = "RUNNING"
(RUN / "experiment-record.yaml").write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
save("input-audit-synthetic.json", audit_file(RUN / "inputs/oracle-od.csv"))
save("small-graph-oracle.json", manual_oracle())
mandatory = [e for e, spec in EDGES.items() if spec["mandatory"]]
optional = [e for e, spec in EDGES.items() if not spec["mandatory"]]
baseline = analyze(mandatory + ["A-B", "B-C"])
assert baseline["static_feasible"]
save("baseline.json", baseline)
candidates = []
for bits in itertools.product((0, 1), repeat=3):
    result = analyze(mandatory + [eid for eid, keep in zip(optional, bits) if keep])
    candidates.append({"build_bits": list(bits), **result})
feasible = [r for r in candidates if r["static_feasible"]]
best = min(feasible, key=lambda r: r["objective_yuan_day"])
save("candidate-enumeration.json", candidates)
save("primary.json", best)
triangle = analyze(list(EDGES))
save("redundant-backbone.json", triangle)
failures = []
for name, nominal in (("baseline", baseline), ("primary", best), ("redundant_backbone", triangle)):
    for removed in nominal["selected_edges"]:
        failed = analyze([eid for eid in nominal["selected_edges"] if eid != removed], degraded=True)
        failures.append({"design": name, "removed_physical_tunnel": removed,
                         "removed_directions": "BOTH", "classification": "GENERIC_SENSITIVITY_SCENARIO",
                         **failed})
save("single-edge-removal.json", failures)
scenarios = [("normal", DATA["od"])]
surge_od = copy.deepcopy(DATA["od"])
surge_od[0]["demand"] *= 1.5
scenarios.append(("P_A_to_sC_50_percent_surge", surge_od))
surge_results = {name: analyze(best["selected_edges"], od) for name, od in scenarios}
save("directional-demand-surge.json", surge_results)
save("robustness-runner.json", run_robustness(lambda ods: analyze(best["selected_edges"], ods), scenarios,
                                           lambda r: r["transport_yuan_day"]))
growth = {"scope": "SOURCE_DERIVED_CAPACITY_DIAGNOSTIC", "assumption": "t=0 base, constant capacity, same demand growth everywhere",
          "demand_multipliers": {str(t): 1.05 ** t for t in (0, 8, 30)},
          "station_departures_per_day_upper_bound": 5 * 18,
          "five_t_vehicle_tonnes_day_4_to_8_carriages": [5 * 18 * 4 * 5, 5 * 18 * 8 * 5],
          "ten_t_vehicle_tonnes_day_4_to_8_carriages": [5 * 18 * 4 * 10, 5 * 18 * 8 * 10],
          "saturation_formula": "first integer t>=0 with D0*(1.05**t)>C; enumerate at equality to avoid floating rounding",
          "real_network_saturation_year": None, "daily_clearing_verified": False}
save("growth-capacity.json", growth)
summary = {"scope": "SYNTHETIC_CODE_VALIDATION_ONLY", "solver_status": "OPTIMAL_WITHIN_ENUMERATED_SYNTHETIC_STATIC_MODEL",
           "proof": "All 8 backbone subsets enumerated; every connected subset's independent shortest routes satisfies static capacities, hence its shortest-route lower bound is feasible. All physical node positions/types/local links fixed. No operational optimum claimed.",
           "node_count": len(IDS), "candidate_physical_edges": len(EDGES), "od_pairs": len(DATA["od"]),
           "build_binary_variables": 3, "subsets_enumerated": len(candidates), "feasible_subsets": len(feasible),
           "disconnected_subsets": sum(r["components"] != 1 for r in candidates),
           "capacity_rejected_connected_subsets": sum(r["components"] == 1 and not r["capacity_feasibility"] for r in candidates),
           "baseline_objective_yuan_day": baseline["objective_yuan_day"], "primary_objective_yuan_day": best["objective_yuan_day"],
           "absolute_improvement_yuan_day": baseline["objective_yuan_day"] - best["objective_yuan_day"],
           "primary_backbone": [e for e in best["selected_edges"] if e in optional],
           "manual_oracle": "PASS", "all_conservation_audits": "PASS", "all_objective_reconstructions": "PASS",
           "failure_cases": len(failures), "real_instance_completed": False,
           "python": platform.python_version(), "scipy": scipy.__version__, "numpy": np.__version__}
assert summary["capacity_rejected_connected_subsets"] == 0, "Shortest-route enumeration proof no longer valid"
save("summary.json", summary)
record.update({"status": "OBSERVED", "updated_by_workflow": "validate_model", "executed_protocol": record["planned_protocol"],
               "change_reason": "", "comparable_to_original_plan": True,
               "output_artifacts": ["RESULT-SUMMARY", "RESULT-BASELINE", "RESULT-PRIMARY", "RESULT-ORACLE"],
               "evidence_ids": ["EVIDENCE-SYNTHETIC-001"], "metrics": summary})
record = apply_protocol_change(record)
assert not validate_experiment_record(record), validate_experiment_record(record)
(RUN / "experiment-record.yaml").write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
print(json.dumps(summary, indent=2))
