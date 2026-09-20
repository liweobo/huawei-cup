"""Prepare task-local scenario inputs and validate provenance before computation."""
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[4]
sys.path.insert(0, str(REPO))
from skill.scripts.runtime_provenance import apply_protocol_change, validate_experiment_record, validate_workspace_manifest


def save(path, data):
    (RUN / path).parent.mkdir(parents=True, exist_ok=True)
    (RUN / path).write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


created = datetime.now(timezone.utc).isoformat()
source = next((RUN / "source").glob("*.doc"))
manifest = {"schema_version": 2, "isolation_mode": "repository_scoped_blind_run", "run_id": "run-001",
            "benchmark_id": RUN.parent.name, "created_at": created, "active_run_id": "run-001",
            "immutable_inputs": [{"source_artifact_id": "SOURCE-DOC", "path": source.relative_to(RUN).as_posix(),
                                  "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}],
            "writable_root": str(RUN), "allowed_write_root": str(RUN), "prior_run_artifacts_visible": False,
            "developer_repository_visible": True, "evaluator_files_visible": True,
            "allowed_read_roots": ["skill", "input"],
            "scope_note": "Not a platform clean room. input aliases this run's source/inputs. Historical bytes hashed only for integrity; development tests are harness-only, never modeling evidence."}
assert not validate_workspace_manifest(manifest), validate_workspace_manifest(manifest)
save("workspace-manifest.yaml", manifest)
protocol = {"scope": "SYNTHETIC_CODE_VALIDATION_ONLY", "real_instance_status": "MISSING_REQUIRED_ATTACHMENTS",
            "stages": ["audit_synthetic_od", "manual_directed_path_oracle", "baseline_tree",
                       "enumerate_three_backbone_build_decisions", "flow_capacity_objective_audit",
                       "single_tunnel_removal", "directional_demand_surge", "annual_growth_bound"],
            "candidate_subsets": 8, "routing": "scipy.sparse.csgraph.dijkstra_positive_weights",
            "objective": "yuan_per_day_transport_plus_1_percent_annual_depreciation_over_365_days",
            "validation": ["node_edge_counts", "asymmetric_od", "connected_components", "own_primary_mediation",
                           "od_reachability", "per_commodity_conservation", "directional_capacity",
                           "node_dispatch", "objective_reconstruction", "manual_paths", "all_single_edge_failures"],
            "failure_model": "remove_one_physical_tunnel_both_directions",
            "sensitivity": {"surge_od": "P_A->sC", "factor": 1.5, "classification": "GENERIC_SENSITIVITY_SCENARIO"},
            "growth": {"rate": 0.05, "years": [0, 8, 30]}, "randomness": "NONE"}
record = {"schema_version": 1, "experiment_id": "EXP-2017F-ORACLE-001", "run_id": "run-001",
          "created_at": created, "problem": RUN.parent.name, "question": "Q1-Q4 input-boundary and synthetic algorithm verification",
          "status": "PLANNED", "updated_by_workflow": "design_model", "planned_protocol": protocol,
          "executed_protocol": {}, "change_reason": "Execution has not started", "comparable_to_original_plan": False,
          "protocol_change_disclosure": None, "input_artifacts": ["INPUT-ORACLE"], "code_artifacts": ["CODE-ORACLE"],
          "output_artifacts": [], "random_seed": None, "metrics": {}, "evidence_ids": []}
record = apply_protocol_change(record)
assert not validate_experiment_record(record), validate_experiment_record(record)
save("experiment-record-planned.yaml", record)
save("experiment-record.yaml", record)

node_specs = [("P_A", "PARK", -1, 0, "A"), ("P_B", "PARK", 5, 0, "B"),
              ("A", "PRIMARY", 0, 0, "A"), ("B", "PRIMARY", 4, 0, "B"), ("C", "PRIMARY", 2, 3, "C"),
              ("sA", "SECONDARY", 0, -.5, "A"), ("sB", "SECONDARY", 4, -.5, "B"), ("sC", "SECONDARY", 2, 3.5, "C")]
nodes = [{"node_id": n, "node_meaning": "Artificial " + n, "node_type": t, "coordinate_km": [x, y],
          "primary": p, "source": "SCENARIO_ASSUMED"} for n, t, x, y, p in node_specs]
edge_specs = [("PA-A", "P_A", "A", "PARK_PRIMARY", True), ("PB-B", "P_B", "B", "PARK_PRIMARY", True),
              ("A-sA", "A", "sA", "LOCAL", True), ("B-sB", "B", "sB", "LOCAL", True),
              ("C-sC", "C", "sC", "LOCAL", True), ("A-B", "A", "B", "BACKBONE", False),
              ("B-C", "B", "C", "BACKBONE", False), ("A-C", "A", "C", "BACKBONE", False)]
edges = [{"edge_id": eid, "u": u, "v": v, "edge_meaning": kind, "mandatory": req,
          "construction_rule": "Explicit artificial eligible corridor, not generated from a distance threshold",
          "direction": "paired_directed_arcs", "source": "SCENARIO_ASSUMED"} for eid, u, v, kind, req in edge_specs]
ods = [("P_A", "sC", 600), ("sC", "P_A", 100), ("P_B", "sA", 300), ("sA", "P_B", 40),
       ("sB", "sC", 200), ("sC", "sB", 50)]
data = {"scope": "SYNTHETIC_CODE_VALIDATION", "node_count": 8, "nodes": nodes, "candidate_edges": edges,
        "od": [{"origin": o, "destination": d, "demand": q, "unit": "tonne/day", "source": "SCENARIO_ASSUMED"} for o, d, q in ods],
        "geometry": "Artificial Cartesian plane in km; Euclidean length equals tunnel length by explicit test definition",
        "capacity_scope": "Static necessary throughput limits only; not daily operational clearing or empty-vehicle balance"}
(RUN / "inputs").mkdir(exist_ok=True)
(RUN / "inputs/oracle.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
with (RUN / "inputs/oracle-od.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["origin", "destination", "tonnes_per_day"])
    writer.writerows(ods)
print("PLANNED provenance validated; synthetic inputs written before computation")
