"""Deterministic regressions for protocol provenance and run isolation."""

from __future__ import annotations

import copy
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill.scripts.runtime_provenance import (
    apply_protocol_change,
    final_readiness_errors,
    initialize_workspace,
    observed_result_errors,
    protocols_differ,
    run_scoped_path_errors,
    validate_active_evidence_set,
    validate_evidence_entry,
    validate_experiment_record,
    validate_paper_claim,
    validate_workspace_manifest,
)


def check(label: str, ok: bool, failures: list[str]) -> None:
    print(f"{'PASS' if ok else 'FAIL'} | {label}")
    if not ok:
        failures.append(label)


def observed_record() -> dict:
    record = {
        "experiment_id": "EXP-Q2-001",
        "run_id": "run-test",
        "created_at": "2026-09-01T00:00:00Z",
        "problem": "fixture",
        "question": "Q2",
        "status": "OBSERVED",
        "updated_by_workflow": "validate_model",
        "planned_protocol": {
            "validation": [
                {"type": "stratified_holdout", "test_size": 0.2, "seed": 2024},
                {"type": "leave_one_temperature_out", "levels": [25, 50, 70, 90]},
            ]
        },
        "executed_protocol": {
            "validation": [
                {"type": "repeated_stratified_holdout", "repeats": 50, "seed": 2024},
                {"type": "unseen_frequency_group"},
                {"type": "leave_one_temperature_out", "levels": [25, 50, 70, 90]},
            ]
        },
        "change_reason": "Repeated frequencies made one random holdout optimistic.",
        "comparable_to_original_plan": False,
        "protocol_change_disclosure": {
            "planned_summary": "One stratified holdout plus leave-one-temperature-out.",
            "executed_summary": "Fifty repeats plus unseen-frequency and leave-one-temperature-out validation.",
            "reason": "Repeated frequencies required a stricter generalization check.",
            "comparable_to_original_plan": False,
        },
        "input_artifacts": ["training.xlsx"],
        "code_artifacts": ["validate.py"],
        "output_artifacts": ["metrics.json"],
        "random_seed": 2024,
        "metrics": {"MAPE": 0.17},
        "evidence_ids": ["EV-Q2-001"],
    }
    return apply_protocol_change(record)


def main() -> int:
    failures: list[str] = []

    check(
        "A validate_model observed result requires Experiment Record",
        any("experiment-record.yaml" in error for error in observed_result_errors("validate_model", None)),
        failures,
    )
    valid_record = observed_record()
    check("A validate_model accepts a complete observed record", not observed_result_errors("validate_model", valid_record), failures)

    check("B normalized protocol diff detects expanded validation", protocols_differ(valid_record["planned_protocol"], valid_record["executed_protocol"]), failures)
    key_reordered = copy.deepcopy(valid_record["planned_protocol"])
    key_reordered["validation"] = [
        {key: stage[key] for key in reversed(list(stage))} for stage in key_reordered["validation"]
    ]
    check("B protocol identity ignores mapping key ordering", not protocols_differ(valid_record["planned_protocol"], key_reordered), failures)
    reordered = copy.deepcopy(valid_record["planned_protocol"])
    reordered["validation"].reverse()
    check("B protocol identity detects sequence reordering", protocols_differ(valid_record["planned_protocol"], reordered), failures)

    no_reason = copy.deepcopy(valid_record)
    no_reason["change_reason"] = ""
    check("C changed protocol requires reason", any("change_reason" in error for error in validate_experiment_record(no_reason)), failures)

    no_disclosure = copy.deepcopy(valid_record)
    no_disclosure["protocol_change_disclosure"] = None
    check("D observed changed protocol requires user disclosure", any("protocol_change_disclosure" in error for error in validate_experiment_record(no_disclosure)), failures)

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "skill").mkdir()
        immutable = root / "input/problem.txt"
        immutable.parent.mkdir(parents=True)
        immutable.write_text("immutable", encoding="utf-8")
        workspace = initialize_workspace(root, "benchmark-fixture", "run-test", "2026-09-01T00:00:00Z", [immutable])
        manifest = yaml.safe_load((workspace / "workspace-manifest.yaml").read_text(encoding="utf-8"))
        check("E workspace initializer creates an isolated valid manifest", not validate_workspace_manifest(manifest), failures)
        check("E current-run artifact path is accepted", not run_scoped_path_errors(workspace / "outputs/metrics.json", "run-test", workspace), failures)
        check("E artifact outside ACTIVE_RUN_ID is rejected", bool(run_scoped_path_errors(root / "metrics.json", "run-test", workspace)), failures)

    active_set = {
        "active_run_id": "run-test",
        "active_evidence_set": {"Q1": {"run_id": "run-test", "experiment_id": "EXP-Q1-002"}},
    }
    stale_claim = {
        "claim_id": "CLAIM-Q1",
        "question": "Q1",
        "evidence_ref": {"run_id": "run-old", "experiment_id": "EXP-Q1-001", "artifact": "metrics.json", "json_path": "accuracy"},
    }
    check("F stale paper evidence from another run is rejected", any("STALE_EVIDENCE_REFERENCE" in error for error in validate_paper_claim(stale_claim, active_set, "run-test")), failures)
    active_claim = copy.deepcopy(stale_claim)
    active_claim["evidence_ref"].update({"run_id": "run-test", "experiment_id": "EXP-Q1-002"})
    check("G active evidence set is structurally valid", not validate_active_evidence_set(active_set, "run-test"), failures)
    check("G paper claim from active evidence set is accepted", not validate_paper_claim(active_claim, active_set, "run-test"), failures)

    evidence = {"evidence_id": "EV-Q2-001", "type": "VALIDATION_RESULT", "run_id": "run-test", "experiment_id": "EXP-Q2-001"}
    check("run-produced evidence binds run_id and experiment_id", not validate_evidence_entry(evidence, "run-test"), failures)
    missing_run = dict(evidence)
    missing_run.pop("run_id")
    check("run-produced evidence without run_id is rejected", bool(validate_evidence_entry(missing_run, "run-test")), failures)

    final_state = {
        "status": "READY",
        "required_questions": {"Q1": "COMPLETE", "Q2": "COMPLETE", "Q3": "INCOMPLETE", "Q4": "INCOMPLETE", "Q5": "INCOMPLETE"},
        "required_artifacts": {"submission_workbook": "MISSING", "final_paper": "MISSING"},
        "compliance_status": "UNVERIFIED",
    }
    check("H incomplete Q3/Q4/Q5 block final READY", len(final_readiness_errors(final_state)) >= 5, failures)

    total = 15
    print(f"\nPhase 5 Regression Test: {'PASS' if not failures else 'FAIL'} ({total - len(failures)}/{total} checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
