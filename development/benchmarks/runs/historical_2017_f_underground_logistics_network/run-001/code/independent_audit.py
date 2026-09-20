"""Reconstruct saved results without importing the experiment implementation."""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
import yaml

RUN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN.parents[4]))
from skill.scripts.runtime_provenance import apply_protocol_change, validate_experiment_record

record = yaml.safe_load((RUN / "experiment-record.yaml").read_text())
assert record["status"] == "OBSERVED"
record["status"] = "RUNNING"
(RUN / "experiment-record.yaml").write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")


def read(path):
    return json.loads((RUN / path).read_text(encoding="utf-8"))


data = read("inputs/oracle.json")
nodes = {n["node_id"]: n for n in data["nodes"]}
candidates = {e["edge_id"]: e for e in data["candidate_edges"]}
assert len(nodes) == len(data["nodes"]) == 8
assert len(candidates) == len(data["candidate_edges"]) == 8
assert len({tuple(sorted((e["u"], e["v"]))) for e in candidates.values()}) == 8
demand = {(d["origin"], d["destination"]): d["demand"] for d in data["od"]}
asymmetric = [(o, d) for o, d in demand if demand[o, d] != demand.get((d, o), 0)]
assert asymmetric
rows = []
results = [("baseline", read("results/baseline.json")), ("primary", read("results/primary.json")),
           ("redundant", read("results/redundant-backbone.json"))]
results += [(f"candidate-{i}", r) for i, r in enumerate(read("results/candidate-enumeration.json"))]
results += [(f"failure-{i}", r) for i, r in enumerate(read("results/single-edge-removal.json"))]
for name, result in results:
    selected = set(result["selected_edges"])
    assert selected <= candidates.keys()
    arcs, adj = {}, defaultdict(set)
    capital = 3 * 1.5e8 + 3 * 1e8
    for eid in selected:
        e = candidates[eid]
        u, v = e["u"], e["v"]
        assert u != v and e["source"] == "SCENARIO_ASSUMED"
        length = math.dist(nodes[u]["coordinate_km"], nodes[v]["coordinate_km"])
        assert 0 < length < math.inf
        arcs[u, v] = arcs[v, u] = length
        adj[u].add(v)
        adj[v].add(u)
        capital += length * (4e8 if e["edge_meaning"] == "PARK_PRIMARY" else 3e8)
    visited, components = set(), []
    for start in nodes:
        if start in visited:
            continue
        group, pending = set(), [start]
        while pending:
            v = pending.pop()
            if v in group:
                continue
            group.add(v)
            pending.extend(adj[v] - group)
        visited |= group
        components.append(group)
    assert len(components) == result["components"]
    assert result["node_count"] == len(nodes)
    assert result["physical_edge_count"] == len(selected)
    assert result["directed_arc_count"] == len(arcs)
    assert sorted(v for v in nodes if not adj[v]) == sorted(result["isolated_nodes"])
    aggregate, transport, max_residual = defaultdict(float), 0.0, 0.0
    delivered = set()
    for route in result["routes"]:
        k = route["commodity"]
        delivered.add(k)
        od = data["od"][k]
        assert route["nodes"][0] == od["origin"] and route["nodes"][-1] == od["destination"]
        q = route["tonnes_per_day"]
        assert q == od["demand"]
        length, balance = 0.0, defaultdict(float)
        for u, v in zip(route["nodes"], route["nodes"][1:]):
            length += arcs[u, v]
            aggregate[u, v] += q
            balance[u] += q
            balance[v] -= q
        assert math.isclose(length, route["km"], abs_tol=1e-10)
        transport += q * length
        for v in nodes:
            expected = q if v == od["origin"] else -q if v == od["destination"] else 0
            max_residual = max(max_residual, abs(balance[v] - expected))
    for k, od in enumerate(data["od"]):
        reachable = any(od["origin"] in group and od["destination"] in group for group in components)
        assert (k in delivered) == reachable
    departures = defaultdict(int)
    for e in result["edges"]:
        u, v = e["u"], e["v"]
        assert aggregate[u, v] == e["flow_u_v_tonnes_day"]
        assert aggregate[v, u] == e["flow_v_u_tonnes_day"]
        vehicle = 10 if e["meaning"] == "PARK_PRIMARY" else 5
        assert e["directional_running_capacity_tonnes_day"] == 540 * 8 * vehicle
        assert e["design_directional_flow"] == max(aggregate[u, v], aggregate[v, u])
        for a, b in ((u, v), (v, u)):
            departures[a] += math.ceil(aggregate[a, b] / (8 * vehicle))
    assert all(departures[n["node_id"]] == n["departures"] for n in result["nodes"])
    assert math.isclose(capital, result["capital_yuan"], rel_tol=1e-12)
    assert math.isclose(transport, result["transport_yuan_day"], rel_tol=1e-12)
    assert max_residual == 0
    if result["static_feasible"]:
        assert len(components) == 1 and len(delivered) == len(data["od"])
        assert all(d <= 90 for d in departures.values())
        assert math.isclose(capital * .01 / 365 + transport, result["objective_yuan_day"], rel_tol=1e-12)
    else:
        assert result["objective_yuan_day"] is None
    rows.append({"result": name, "counts_connectivity_reachability": "PASS", "conservation": "PASS",
                 "capacity_components": "PASS", "objective_reconstruction": "PASS", "max_flow_residual": max_residual})

summary = {"status": "PASS", "scope": "SYNTHETIC_CODE_VALIDATION_ONLY", "saved_network_results_reconstructed": len(rows),
           "source_od_pairs": len(data["od"]), "asymmetric_od_entries": len(asymmetric), "rows": rows,
           "official_network": "NOT_AVAILABLE", "daily_operational_feasibility": "NOT_VERIFIED"}
(RUN / "results/independent-audit.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
canonical = {"scope": "ORIGINAL_PROBLEM_INPUT_AUDIT", "source_documents": 1, "original_source_images": 5,
             "native_word_tables": 0, "embedded_data_files": 0,
             "original_od_table_received": False, "original_coordinate_table_received": False,
             "total_rows": None, "missing_cells": None, "invalid_rows": None, "duplicate_full_rows": None,
             "frequency_boundary_rows": None, "anomaly_rows": None,
             "unresolved_questions": ["missing numbered regional map", "missing directed OD and time basis", "missing coordinates/areas/CRS", "missing congestion coefficients", "missing park identifier/location mapping"],
             "graph_instantiated": False, "source_integrity": "PASS", "body_extraction": "PASS", "map_semantics": "EXTRACTION_UNVERIFIED"}
(RUN / "results/canonical-input-audit.json").write_text(json.dumps(canonical, indent=2), encoding="utf-8")
record.update({"status": "OBSERVED", "updated_by_workflow": "validate_model"})
record["code_artifacts"].append("CODE-INDEPENDENT-AUDIT")
record["output_artifacts"].append("RESULT-INDEPENDENT-AUDIT")
record["metrics"]["independent_saved_result_audit"] = "PASS"
record = apply_protocol_change(record)
assert not validate_experiment_record(record), validate_experiment_record(record)
(RUN / "experiment-record.yaml").write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))
