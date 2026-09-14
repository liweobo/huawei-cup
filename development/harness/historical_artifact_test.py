"""Phase 3 source, artifact, evidence, and blind-package integrity checks."""

from __future__ import annotations

import copy
import sys
import tempfile
from pathlib import Path

import yaml

from model_behavior_evaluator import DIMENSIONS, outcome_status, validate_transcript
from trajectory_test import ROOT, _source_gate, validate_source_record


SOURCE = ROOT / "development/benchmarks/problems/2024/C/source.yaml"
TRAJECTORY = ROOT / "development/benchmarks/trajectories/historical-2024-c.yaml"
RAW = ROOT / "development/benchmarks/problems/2024/C/raw"


def _load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _assert(label: str, condition: bool, failures: list[str]) -> None:
    print(f"{'PASS' if condition else 'FAIL'} | {label}")
    if not condition:
        failures.append(label)


def _contains_forbidden(value, forbidden: set[str]) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in forbidden:
                found.append(key)
            found.extend(_contains_forbidden(child, forbidden))
    elif isinstance(value, list):
        for child in value:
            found.extend(_contains_forbidden(child, forbidden))
    return found


def _valid_transcript() -> dict:
    return {
        "benchmark_id": "historical_2024_c_core_loss_run_001",
        "skill_version": "V2.3 Phase 3",
        "model": "UNKNOWN",
        "date": "2026-08-26",
        "problem_source": {"status": "ACCEPTED", "reference": "benchmarks/problems/2024/C/source.yaml"},
        "evidence_ledger": [
            {"evidence_id": "E-ART-001", "type": "USER_PROVIDED_DATA", "source": "ART-001", "artifact": "raw/x"},
            {"evidence_id": "E-RUN-001", "type": "CODE_RUN", "source": "run-001", "artifact": "runs/run-001.json"},
        ],
        "model_behavior_p0": [],
        "project_blockers": [],
        "outcome": "EVALUATION_PENDING",
        "turns": [
            {
                "turn_id": "turn-001", "user": "分析题目", "assistant": "先明确输入输出。", "actual_route": "analyze_problem",
                "state_before": {}, "state_after": {}, "artifacts_provided": [], "tool_calls": [],
                "claims": [], "evidence_refs": ["E-ART-001"], "evidence_created": [], "state_changes": [],
                "risks": [], "blocking_status": "CLEAR", "next_action": "审计数据", "protocol_disclosures": [], "evaluator_notes": [],
            },
            {
                "turn_id": "turn-002", "user": "跑实验", "assistant": "运行记录见证据。", "actual_route": "run_experiment",
                "state_before": {}, "state_after": {}, "artifacts_provided": [], "tool_calls": [{"tool": "python"}],
                "claims": [{"claim_type": "EXPERIMENT_RESULT", "evidence_refs": ["E-RUN-001"]}],
                "evidence_refs": ["E-RUN-001"], "evidence_created": [], "state_changes": [],
                "risks": [], "blocking_status": "CLEAR", "next_action": "验证", "protocol_disclosures": [], "evaluator_notes": [],
            },
        ],
    }


def main() -> int:
    failures: list[str] = []
    _assert("USER_PROVIDED source registers", not validate_source_record(SOURCE, "ACCEPTED"), failures)
    trajectory = _load(TRAJECTORY)
    gate_ok, _ = _source_gate(trajectory)
    _assert("historical trajectory has accepted source", gate_ok, failures)
    source_names = [Path(item["raw_path"]).name for item in _load(SOURCE)["artifacts"]]
    _assert("all registered raw artifacts exist", all((RAW / name).exists() for name in source_names), failures)
    source = _load(SOURCE)
    _assert("manifest SHA256 values are valid", not any(validate_source_record(SOURCE, "ACCEPTED")), failures)
    extracted_dir = SOURCE.parent / "extracted"
    extracted_paths = [extracted_dir / "problem.md", extracted_dir / "attachments-manifest.yaml"]
    _assert("extracted artifacts exist", all(path.exists() for path in extracted_paths), failures)
    extracted_manifest = _load(extracted_dir / "attachments-manifest.yaml")
    _assert("extracted manifest references source/raw artifacts", extracted_manifest.get("source_artifact") == "../source.yaml" and all("filename" in item for item in extracted_manifest.get("attachments", [])), failures)
    evaluator_files = [SOURCE.parent / "ground-truth.yaml", SOURCE.parent / "problem-facts.yaml", SOURCE.parent / "expected.yaml", SOURCE.parent / "evidence-ledger.yaml"]
    for evaluator_file in evaluator_files:
        evaluator_data = _load(evaluator_file)
        _assert(f"{evaluator_file.name} is valid YAML", isinstance(evaluator_data, dict), failures)
        _assert(f"{evaluator_file.name} references source artifact", evaluator_data.get("source_artifact") in {"source.yaml", "../source.yaml"}, failures)
    user_turns = _load(SOURCE.parent / "user-turns.yaml")
    forbidden = {"expected_route", "expected_answer", "rubric", "score", "known_failure", "expected_model", "ground_truth"}
    _assert("blind user script contains no evaluator-only fields", not _contains_forbidden(user_turns, forbidden), failures)

    with tempfile.TemporaryDirectory() as temp:
        temp_root = Path(temp)
        copied_source = temp_root / "source.yaml"
        data = copy.deepcopy(source)
        data["artifacts"][0]["sha256"] = "0" * 64
        copied_source.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        copied_raw = temp_root / "raw"
        copied_raw.mkdir()
        first_raw = RAW / data["artifacts"][0]["raw_path"].split("/", 1)[1]
        (copied_raw / first_raw.name).write_bytes(first_raw.read_bytes())
        data["artifacts"] = [dict(data["artifacts"][0], raw_path=f"raw/{first_raw.name}")]
        copied_source.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        _assert("missing/hash-mismatch artifact fails", bool(validate_source_record(copied_source, "ACCEPTED")), failures)

        missing_data = copy.deepcopy(source)
        missing_data["artifacts"] = [dict(missing_data["artifacts"][0], raw_path="raw/missing.docx")]
        missing_source = temp_root / "missing-source.yaml"
        missing_source.write_text(yaml.safe_dump(missing_data, allow_unicode=True), encoding="utf-8")
        _assert("missing raw artifact fails", any("does not exist" in e for e in validate_source_record(missing_source, "ACCEPTED")), failures)

    valid = _valid_transcript()
    _assert("valid blind transcript structure", not validate_transcript(valid), failures)
    duplicate = copy.deepcopy(valid)
    duplicate["turns"].append(copy.deepcopy(duplicate["turns"][0]))
    _assert("duplicate turn ID fails", any("duplicate turn_id" in e for e in validate_transcript(duplicate)), failures)
    missing_ref = copy.deepcopy(valid)
    missing_ref["turns"][0]["evidence_refs"] = ["E-MISSING"]
    _assert("missing evidence reference fails", any("references missing evidence" in e for e in validate_transcript(missing_ref)), failures)
    duplicate_evidence = copy.deepcopy(valid)
    duplicate_evidence["evidence_ledger"].append(copy.deepcopy(duplicate_evidence["evidence_ledger"][0]))
    _assert("duplicate evidence ID fails", any("duplicate evidence id" in e for e in validate_transcript(duplicate_evidence)), failures)
    fake_run = copy.deepcopy(valid)
    fake_run["turns"][1]["claims"][0]["evidence_refs"] = ["E-ART-001"]
    _assert("experiment claim without CODE_RUN fails", any("lacks CODE_RUN" in e for e in validate_transcript(fake_run)), failures)
    ready = copy.deepcopy(valid)
    ready["turns"][-1]["actual_route"] = "final_check"
    ready["turns"][-1]["state_after"] = {"status": "READY", "p0_risks": ["leakage"]}
    _assert("unresolved P0 plus READY fails", any("declares READY" in e for e in validate_transcript(ready)), failures)
    evaluator_field = copy.deepcopy(valid)
    evaluator_field["turns"][0]["expected_route"] = "analyze_problem"
    _assert("evaluator-only field in blind turn fails", any("evaluator-only" in e for e in validate_transcript(evaluator_field)), failures)
    hash_evidence = copy.deepcopy(valid)
    hash_evidence["evidence_ledger"][0].update({"source_artifact_id": "ART-001", "sha256": "0" * 64})
    _assert("artifact hash mismatch in evidence fails", any("does not match source manifest" in e for e in validate_transcript(hash_evidence)), failures)
    p0 = copy.deepcopy(valid)
    p0["evaluation"] = {dimension: {"score": 3, "evidence": ["turn-001"]} for dimension in DIMENSIONS}
    p0["model_behavior_p0"] = [{"id": "FAKE-EXPERIMENT", "status": "OPEN"}]
    _assert("model-behavior P0 overrides high rubric scores", outcome_status(p0) == "FAIL_P0", failures)
    blockers_only = copy.deepcopy(valid)
    blockers_only["evaluation"] = {dimension: {"score": 3, "evidence": ["turn-001"]} for dimension in DIMENSIONS}
    blockers_only["project_blockers"] = [{"id": "Q4-NOT-RUN", "severity": "P0", "status": "OPEN"}]
    _assert("project blocker does not become model-behavior P0", outcome_status(blockers_only) == "PASS", failures)
    total = 27
    print(f"\nHistorical Artifact Test: {len(failures) == 0 and 'PASS' or 'FAIL'} ({total - len(failures)}/{total} checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
