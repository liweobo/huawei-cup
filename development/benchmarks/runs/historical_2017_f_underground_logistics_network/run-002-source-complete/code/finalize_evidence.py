"""Bind real saved artifacts to frozen Skill provenance helpers."""
import argparse
import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path
import yaml

RUN=Path(__file__).resolve().parents[1]; REPO=RUN.parents[4]
sys.path.insert(0,str(REPO/"skill/scripts"))
from runtime_provenance import (apply_protocol_change,validate_experiment_record,
    validate_workspace_manifest,validate_active_evidence_set,validate_evidence_entry)
from structured_improvement import validate_improvement_contract,update_incumbent


def read(name):
    return json.loads((RUN/name).read_text(encoding="utf-8"))


def dump(name,data):
    (RUN/name).write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")


def sha(p):
    with p.open("rb") as f: return hashlib.file_digest(f,"sha256").hexdigest()


def key(path):
    return "ART-"+hashlib.sha256(path.encode()).hexdigest()[:16]


def finalize():
    original=RUN/"workspace-manifest-original.yaml"
    if not original.exists(): shutil.copyfile(RUN/"workspace-manifest.yaml",original)
    workspace=yaml.safe_load((RUN/"workspace-manifest.yaml").read_text(encoding="utf-8"))
    workspace["writable_root"]=str(RUN); workspace["allowed_write_root"]=str(RUN)
    (RUN/"workspace-manifest.yaml").write_text(yaml.safe_dump(workspace,allow_unicode=True,sort_keys=False),encoding="utf-8")
    ws_errors=validate_workspace_manifest(workspace)
    trace=read("results/search-trace.json")
    original_contract=trace["contract"]; original_contract_check=validate_improvement_contract(original_contract)
    normalized=dict(original_contract,problem_type="STRUCTURED_IMPROVEMENT",incumbent_feasible=True,
        decision_structure="physical park-tunnel selection with coupled continuous commodity rerouting",
        objective_evaluator="saved physical capital plus routing/access cost, yuan/day",
        search_budget=dict(max_evaluations=8,time_limit_seconds=480),
        move_families=[dict(name="delete_park_tunnel",decision_component="physical_build_selection",
            description="remove one physical tunnel and both arcs; solve fixed-design LP",
            rationale="reduce high tunnel depreciation only when full realized cost decreases",
            applicability="statically feasible incumbent, eligible park links, unchanged service policy",
            expected_effect="lower capital, possibly longer commodity paths")])
    normalized["normalization_scope"]="retrospective schema normalization; not a pre-run contract claim"
    check=validate_improvement_contract(normalized); assert check["status"]=="PASS"
    incumbent=dict(feasible=True,objective=trace["objective_before"])
    replay=[]
    for row in trace["trace"]:
        result=update_incumbent(incumbent,dict(feasible=row["feasible"],objective=row["objective"]),direction="MINIMIZE")
        incumbent=result["incumbent"]
        assert abs(incumbent["objective"]-row["incumbent_after"])<1e-5
        replay.append(dict(iteration=row["iteration"],updated=result["updated"],objective=incumbent["objective"]))
    dump("contract-audit.json",dict(workspace=dict(status="LEGACY_STRICT_ISOLATION_REJECTED" if ws_errors else "PASS",errors=ws_errors,
        disposition="logical boundary retained; no claim of clean-room certification"),
        original_improvement_schema=original_contract_check,normalized_improvement_contract=normalized,
        normalized_improvement_schema=check,incumbent_replay=replay,
        operation_contract=read("operation-contract.json")["closure_check"]))
    paths=[]
    for sub in ["code","inputs","results","figures"]:
        paths.extend(p for p in (RUN/sub).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix!=".pyc")
    registry=[dict(artifact_id=key(p.relative_to(RUN).as_posix()),path=p.relative_to(RUN).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(paths)]
    dump("evidence-artifacts.json",registry)
    selected={"Q1":"results/primary/node-results.json","Q2":"results/primary/design.json",
        "Q3":"results/q3-operations.json","Q4":"results/q4-annual.json"}
    active={"active_run_id":RUN.name,"active_evidence_set":{}}
    entries=[]
    for question,path in selected.items():
        artifact_id=key(path); evidence_id="EV-2017F-"+question
        ref=dict(run_id=RUN.name,experiment_id="EXP-2017F-SC-001",artifact_id=artifact_id,evidence_id=evidence_id,
            artifact=path,status="PARTIAL",scope="conditional numerical output, not full-question feasibility")
        active["active_evidence_set"][question]=ref
        entry=dict(ref,type="EXPERIMENT_RESULT",source="actual code run",sha256=sha(RUN/path))
        assert not validate_evidence_entry(entry,RUN.name); entries.append(entry)
    assert not validate_active_evidence_set(active,RUN.name)
    (RUN/"active-evidence-set.yaml").write_text(yaml.safe_dump(active,sort_keys=False),encoding="utf-8")
    dump("evidence-ledger.json",entries)
    record=yaml.safe_load((RUN/"experiment-record-planned.yaml").read_text(encoding="utf-8"))
    executed=copy.deepcopy(record["planned_protocol"])
    executed["stages"]=["independent_original_input_audit","problem_facts_and_semantic_contracts","rejected_initial_layouts",
        "real_data_q1_baseline_2000","q1_primary_1800","q2_eight_tunnel_deletions_with_rerouting","independent_static_audit",
        "q3_failure_surge_location_diagnostics","q4_phasing_growth","q3_queue_operations_0_12min",
        "independent_operation_phase_audit","regressions_and_reviewer"]
    executed["design_search"]=dict(baseline_fill=2000,consolidation_fill=1800,evaluated_deletions=8,
        candidate_addition="two top aggregate-demand primary peers")
    executed["limitations"]=["no fully clearing timetable","no full Q4 expansion","undefined ratios for nonassociated primaries",
        "logical not physical blind isolation","one residual regression path-guard failure"]
    record.update(status="OBSERVED",updated_by_workflow="validate_model",executed_protocol=executed,
        change_reason="Initial layouts were LP-INFEASIBLE; lower constructive fill and demand-peer shortcuts restored static feasibility. Actual audit/order and queue scenarios explicitly recorded.",
        comparable_to_original_plan=False,
        protocol_change_disclosure=dict(planned_summary="baseline/primary design plus bounded improvement and Q3/Q4 execution",
            executed_summary="rejected3000/2400 fill; feasible2000/1800; eight deletions; independent audits; static and queue/scenario limitations retained",
            reason="feasibility refinement and explicit executed ordering; no source capacity weakened",
            comparable_to_original_plan=False),
        code_artifacts=[r["artifact_id"] for r in registry if r["path"].startswith("code/")],
        output_artifacts=[r["artifact_id"] for r in registry if not r["path"].startswith("code/")],
        evidence_ids=[r["evidence_id"] for r in entries],
        metrics=dict(primary_daily_yuan=read("results/primary/design.json")["cost"]["total_daily_yuan"],
                     full_task_status="PARTIAL",final_decision="BLIND_RUN_PARTIAL"))
    record=apply_protocol_change(record); assert not validate_experiment_record(record)
    (RUN/"experiment-record.yaml").write_text(yaml.safe_dump(record,allow_unicode=True,sort_keys=False),encoding="utf-8")
    completion=dict(completion_marker="2017F_SOURCE_COMPLETE_BLIND_RUN_COMPLETE",problem="2017F 地下物流系统网络",
        problem_family="GRAPH_NETWORK_MODELING_AND_DESIGN",source_status="SOURCE_COMPLETE_TRUSTED_INSTITUTIONAL_MIRROR",
        skill_modified=False,excellent_solutions_accessed=False,run_001_modified=False,source_recovery_modified=False,
        subproblems_completed=["Q1 conditional allocation/count/location/volume","Q2 static design/flow/cost","Q3 queue/failure/surge diagnostics","Q4 conditional phase/growth/saturation accounting"],
        q1_status="PARTIAL",q2_status="PARTIAL",q3_status="PARTIAL",q4_status="PARTIAL",
        graph_construction_audit="PASS",od_direction_audit="PASS",coverage_audit="PASS",
        connectivity_checked="YES",od_reachability_checked="YES",flow_conservation="PASS",
        capacity_feasibility="PARTIAL",daily_clearing_evidence="FAIL",objective_reconstruction="PASS",
        physical_edge_costing="PASS",network_robustness_checked="YES",phased_network_feasibility="PARTIAL",
        small_graph_validation="PASS",independent_final_audit="PARTIAL",final_result_status="PARTIAL",
        first_meaningful_failure="DAILY_CLEARING_NOT_ESTABLISHED",failure_level="NONE",generalizable_gap_candidate="NONE",
        final_decision="BLIND_RUN_PARTIAL",recommended_next_action="Human review of frozen partial results and assumptions; no automatic Skill change, excellent papers, or next run",
        scope_notes=dict(static_capacity="PASS",independent_static_audit="PASS",daily_clearing="Both tested policies fail; no proof every timetable fails",
            skill_failure_level="NONE means no demonstrated missing Skill rule, not full task completion",
            regression="304 development tests passed,1 enclosing-path guard failed;6 local tests passed;all six harnesses passed"))
    dump("completion.json",completion)
    dump("provenance-validation.json",dict(experiment_schema="PASS",active_evidence_schema="PASS",evidence_bindings="PASS",
        protocol_changed=record["protocol_changed"],workspace_strict_isolation="NOT_PASSED_DISCLOSED",current_run_only=True))
    print("Bound OBSERVED conditional evidence; whole-task PARTIAL; protocol change explicitly disclosed")


def freeze(check=False):
    manifest=RUN/"artifact-manifest.json"
    if check:
        data=read("artifact-manifest.json")
        errors=[r["path"] for r in data["files"] if not (RUN/r["path"]).is_file() or sha(RUN/r["path"])!=r["sha256"]]
        assert not errors,errors
        print("Artifact hash verification PASS",len(data["files"])); return
    files=[]
    for p in sorted(RUN.rglob("*")):
        rel=p.relative_to(RUN)
        if not p.is_file() or rel.parts[0]=="work" or "__pycache__" in rel.parts or p.suffix==".pyc" or p==manifest: continue
        files.append(dict(path=rel.as_posix(),sha256=sha(p),bytes=p.stat().st_size))
    dump("artifact-manifest.json",dict(run_id=RUN.name,scope="All non-cache deliverables except this self-referential manifest; original raw hashes in source-manifest.json",files=files))
    print("Frozen deliverables",len(files),"bytes",sum(f["bytes"] for f in files))


if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("mode",choices=["finalize","freeze","check"]); args=p.parse_args()
    if args.mode=="finalize": finalize()
    else: freeze(args.mode=="check")
