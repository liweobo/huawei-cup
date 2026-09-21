"""Bind planned stages to this run before any experiment outputs."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

RUN=Path(__file__).resolve().parents[1]
REPO=RUN.parents[4]
sys.path.insert(0,str(REPO/"skill/scripts"))
from runtime_provenance import apply_protocol_change, validate_experiment_record

source=json.loads((RUN/"source-manifest.json").read_text(encoding="utf-8"))
manifest={"schema_version":2,"isolation_mode":"repository_visible_logical_read_boundary","run_id":RUN.name,
 "benchmark_id":"historical_2017_f_underground_logistics_network","created_at":datetime.now(timezone.utc).isoformat(),
 "active_run_id":RUN.name,"immutable_inputs":[{"source_artifact_id":f["artifact_id"],"path":f["path"],"sha256":f["sha256"]} for f in source["files"]],
 "writable_root":".","allowed_write_root":str(RUN),"prior_run_artifacts_visible":True,"developer_repository_visible":True,
 "evaluator_files_visible":True,"allowed_read_roots":[str(RUN),str(REPO/"skill"),"source-recovery original bytes/provenance only","repository test tooling for required regression","historical bytes for hashing only"],
 "prohibited_content":"All run-001 solution/model/results/code and all 2017F solution sources; visibility is not permission"}
(RUN/"workspace-manifest.yaml").write_text(yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False),encoding="utf-8")
protocol={"stages":["independent_original_input_audit","problem_facts_and_semantic_contracts","real_data_q1_baseline","q1_primary","q2_design_flow_realization","q3_failure_surge_improvement","q4_phasing_growth","independent_audit","reviewer"],
 "data_scope":"complete original 114-ID directed OD, no train/test prediction split", "validation":["source_hashes","dual_xls_readers","coverage_and_exchange","directed_demand_accounting","physical_graph_connectivity","commodity_flow_balance","capacity_by_resource","physical_cost_reconstruction","small_graph_oracle","single_physical_tunnel_failures","yearly_build_dependencies"],
 "claim_gate":"Partial if daily time-feasibility or any required hard constraint remains unverified; no global optimum claim without proof",
 "search_policy":"deterministic baseline plus bounded feasibility-preserving design improvement; exact subproblem status separately reported"}
record={"schema_version":1,"experiment_id":"EXP-2017F-SC-001","run_id":RUN.name,"created_at":datetime.now(timezone.utc).isoformat(),
 "problem":"historical_2017_f_underground_logistics_network","question":"Q1-Q4","status":"PLANNED","updated_by_workflow":"design_model",
 "planned_protocol":protocol,"executed_protocol":protocol,"change_reason":"","comparable_to_original_plan":True,"protocol_change_disclosure":None,
 "input_artifacts":[f["artifact_id"] for f in source["files"]],"code_artifacts":[],"output_artifacts":[],"random_seed":None,"metrics":{},"evidence_ids":[]}
record=apply_protocol_change(record)
assert not validate_experiment_record(record)
for name in ["experiment-record-planned.yaml","experiment-record.yaml"]:
    path=RUN/name
    assert not path.exists(),name
    path.write_text(yaml.safe_dump(record,allow_unicode=True,sort_keys=False),encoding="utf-8")
print("PLANNED experiment and logical workspace created; frozen Skill validator PASS")
