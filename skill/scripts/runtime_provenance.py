"""Runtime provenance contracts for experiments, workspaces, and paper claims."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

try:
    from .temporal_availability import temporal_scope_errors
except ImportError:  # pragma: no cover - bundle-local CLI
    from temporal_availability import temporal_scope_errors  # type: ignore


EXPERIMENT_STATUSES = {"PLANNED", "RUNNING", "OBSERVED", "FAILED", "INVALIDATED"}
RUN_EVIDENCE_TYPES = {"CODE_RUN", "EXPERIMENT_RESULT", "VALIDATION_RESULT", "PAPER_CLAIM"}
EXPERIMENT_FIELDS = {
    "experiment_id",
    "run_id",
    "created_at",
    "problem",
    "question",
    "status",
    "planned_protocol",
    "executed_protocol",
    "protocol_changed",
    "change_reason",
    "comparable_to_original_plan",
    "input_artifacts",
    "code_artifacts",
    "output_artifacts",
    "random_seed",
    "metrics",
    "evidence_ids",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_protocol(value: Any) -> Any:
    """Return a stable protocol identity independent of map/list ordering."""
    if isinstance(value, dict):
        return {str(key): normalize_protocol(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, list):
        normalized = [normalize_protocol(item) for item in value]
        return sorted(normalized, key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if isinstance(value, tuple):
        return normalize_protocol(list(value))
    return value


def protocols_differ(planned: Any, executed: Any) -> bool:
    """Compare planned and executed protocols after deterministic normalization."""
    return normalize_protocol(planned) != normalize_protocol(executed)


def apply_protocol_change(record: dict[str, Any]) -> dict[str, Any]:
    """Return a copy with protocol_changed computed rather than model-authored."""
    result = copy.deepcopy(record)
    result["protocol_changed"] = protocols_differ(result.get("planned_protocol"), result.get("executed_protocol"))
    return result


def _group_scope_errors(scope: Any, contract: Any) -> list[str]:
    # Historical stdlib/YAML-only provenance users do not need modelling
    # dependencies unless they actually validate the new group contract.
    try:
        from .group_validation import group_scope_errors
    except ImportError:  # pragma: no cover - direct CLI
        from group_validation import group_scope_errors
    return group_scope_errors(scope, contract)


def validate_experiment_record(record: dict[str, Any] | None) -> list[str]:
    """Validate the mandatory structured record behind observed experiment numbers."""
    if not isinstance(record, dict):
        return ["experiment-record.yaml is required"]
    errors: list[str] = []
    missing = sorted(EXPERIMENT_FIELDS - set(record))
    if missing:
        errors.append(f"experiment record missing fields: {missing}")
    status = str(record.get("status", "")).upper()
    if status not in EXPERIMENT_STATUSES:
        errors.append("status must be PLANNED, RUNNING, OBSERVED, FAILED, or INVALIDATED")
    changed = protocols_differ(record.get("planned_protocol"), record.get("executed_protocol"))
    if record.get("protocol_changed") is not changed:
        errors.append(f"protocol_changed must be computed as {changed}")
    if changed and not str(record.get("change_reason", "")).strip():
        errors.append("change_reason is required when normalized protocols differ")
    association_protocol = any(
        isinstance(record.get(name), dict) and record[name].get("association_analysis")
        for name in ("planned_protocol", "executed_protocol")
    )
    if association_protocol or "association_contract" in record or "association_scope" in record:
        try:
            from .association_analysis import association_scope_errors
        except ImportError:  # pragma: no cover - direct CLI
            from association_analysis import association_scope_errors
        errors.extend(association_scope_errors(record.get("association_contract"), record.get("association_scope")))
        association_scope = record.get("association_scope")
        if status == "OBSERVED" and (not isinstance(association_scope, dict) or association_scope.get("gate_status") != "PASS"):
            errors.append("OBSERVED association requires association gate PASS")
    temporal_scope = record.get("temporal_scope")
    if temporal_scope is not None:
        errors.extend(temporal_scope_errors(temporal_scope))
        if isinstance(temporal_scope, dict) and str(temporal_scope.get("temporal_gate_status", "")).upper() != "PASS" and status == "OBSERVED":
            errors.append("OBSERVED temporal experiment requires temporal_gate_status PASS")
    temporal_protocol = any(
        isinstance(record.get(name), dict)
        and bool(record[name].get("temporal_prediction") or record[name].get("aggregation_required"))
        for name in ("planned_protocol", "executed_protocol")
    )
    if temporal_protocol and temporal_scope is None:
        errors.append("longitudinal prediction requires temporal_scope provenance")
    group_contract = record.get("group_structure")
    group_scope = record.get("group_scope")
    group_protocol = any(
        isinstance(record.get(name), dict)
        and bool(record[name].get("repeated_entities") or record[name].get("group_validation")
                 or record[name].get("validation_unit") in {"ENTITY", "TIME", "ENTITY_TIME"})
        for name in ("planned_protocol", "executed_protocol")
    )
    if group_scope is not None or group_contract is not None:
        errors.extend(_group_scope_errors(group_scope, group_contract))
        if status == "OBSERVED":
            if not isinstance(group_contract, dict) or group_contract.get("status") != "PASS":
                errors.append("OBSERVED grouped experiment requires a verified Group Structure Contract")
            if not isinstance(group_scope, dict) or group_scope.get("group_gate_status") != "PASS":
                errors.append("OBSERVED grouped experiment requires group_gate_status PASS; leakage is INVALIDATED")
        if isinstance(group_contract, dict) and (
            group_contract.get("temporal_gate_required") or group_contract.get("validation_unit") in {"TIME", "ENTITY_TIME"}
        ) and temporal_scope is None:
            errors.append("TIME/ENTITY_TIME requires an independent temporal_scope gate")
    elif group_protocol:
        errors.append("group-aware validation requires group_structure and group_scope provenance")
    if status == "INVALIDATED":
        if not str(record.get("invalidation_reason", "")).strip():
            errors.append("INVALIDATED records require invalidation_reason")
        return errors
    if status == "OBSERVED":
        updater = str(record.get("updated_by_workflow", ""))
        if updater not in {"run_experiment", "validate_model"}:
            errors.append("OBSERVED records must be updated by run_experiment or validate_model")
        if not record.get("code_artifacts"):
            errors.append("OBSERVED records require code_artifacts")
        if not record.get("output_artifacts"):
            errors.append("OBSERVED records require output_artifacts")
        if not record.get("evidence_ids"):
            errors.append("OBSERVED records require evidence_ids")
        if changed:
            disclosure = record.get("protocol_change_disclosure")
            if not isinstance(disclosure, dict):
                errors.append("OBSERVED changed protocol requires protocol_change_disclosure")
            else:
                for field in ("planned_summary", "executed_summary", "reason", "comparable_to_original_plan"):
                    if field not in disclosure or disclosure[field] in {None, ""}:
                        errors.append(f"protocol_change_disclosure requires {field}")
    return errors


def temporal_scope_from_contract(contract: dict[str, Any]) -> dict[str, Any]:
    """Project a full availability contract into minimal experiment provenance."""
    return {
        "target_horizon": contract.get("target_time"),
        "feature_cutoff": contract.get("allowed_feature_horizon"),
        "post_horizon_records_excluded": contract.get("post_horizon_records", 0),
        "temporal_gate_status": str(contract.get("status", "UNVERIFIED")).upper(),
    }


def apply_temporal_gate(
    record: dict[str, Any], contract: dict[str, Any], *, future_rows_entered_aggregation: bool = False,
) -> dict[str, Any]:
    """Attach temporal provenance and invalidate experiments that used future rows."""
    result = copy.deepcopy(record)
    scope = temporal_scope_from_contract(contract)
    if future_rows_entered_aggregation:
        scope["temporal_gate_status"] = "FAIL"
        result["status"] = "INVALIDATED"
        reason = "FUTURE_INFORMATION_LEAKAGE: post-horizon rows entered aggregation"
        result["invalidation_reason"] = "; ".join(filter(None, [result.get("invalidation_reason"), reason]))
    result["temporal_scope"] = scope
    return result


def apply_group_gate(
    record: dict[str, Any], contract: dict[str, Any], split_report: dict[str, Any],
) -> dict[str, Any]:
    """Attach actual split evidence and invalidate leakage, independently of TIME."""
    result = copy.deepcopy(record)
    result["group_structure"] = copy.deepcopy(contract)
    scope = copy.deepcopy(split_report)
    errors = _group_scope_errors(scope, contract)
    reasons = list(scope.get("violations", [])) + errors
    if scope.get("group_gate_status") == "FAIL" or contract.get("status") == "FAIL" or reasons:
        scope["group_gate_status"] = "FAIL"
        scope["status"] = "FAIL"
        scope["violations"] = list(dict.fromkeys(reasons))
        scope["validation_result_status"] = "INVALIDATED"
        result["status"] = "INVALIDATED"
        reason = "; ".join(reasons) or contract.get("reason") or "GROUP_VALIDATION_FAILED"
        result["invalidation_reason"] = "; ".join(filter(None, [result.get("invalidation_reason"), reason]))
    elif contract.get("status") != "PASS":
        scope["group_gate_status"] = "UNVERIFIED"
        scope["status"] = "UNVERIFIED"
    result["group_scope"] = scope
    return result


def observed_result_errors(workflow: str, record: dict[str, Any] | None) -> list[str]:
    """Gate observed numeric output in both experiment and validation workflows."""
    if workflow not in {"run_experiment", "validate_model"}:
        return [f"unsupported observed-result workflow: {workflow}"]
    errors = validate_experiment_record(record)
    if isinstance(record, dict) and str(record.get("status", "")).upper() != "OBSERVED":
        errors.append("observed numeric results require experiment record status OBSERVED")
    return errors


def validate_workspace_manifest(manifest: dict[str, Any]) -> list[str]:
    """Validate legacy run roots and clean-room workspace manifests."""
    errors: list[str] = []
    required = {
        "run_id", "benchmark_id", "created_at", "active_run_id", "immutable_inputs",
        "writable_root", "prior_run_artifacts_visible", "allowed_read_roots",
        "allowed_write_root",
    }
    missing = sorted(required - set(manifest))
    if missing:
        errors.append(f"workspace manifest missing fields: {missing}")
        return errors
    run_id = str(manifest.get("run_id", ""))
    benchmark_id = str(manifest.get("benchmark_id", ""))
    writable = Path(str(manifest.get("writable_root", "")))
    if str(manifest.get("active_run_id", "")) != run_id:
        errors.append("active_run_id must equal run_id")
    if manifest.get("prior_run_artifacts_visible") is not False:
        errors.append("prior_run_artifacts_visible must be false")
    if Path(str(manifest.get("allowed_write_root", ""))) != writable:
        errors.append("allowed_write_root must equal writable_root")
    if manifest.get("isolation_mode") == "clean_room":
        if writable != Path("workspace"):
            errors.append("clean-room writable_root must be the relative workspace directory")
        if any(Path(str(root)).is_absolute() for root in manifest.get("allowed_read_roots", [])):
            errors.append("clean-room allowed_read_roots must be runtime-relative")
        if manifest.get("developer_repository_visible") is not False:
            errors.append("clean-room developer_repository_visible must be false")
        if manifest.get("evaluator_files_visible") is not False:
            errors.append("clean-room evaluator_files_visible must be false")
        for root in manifest.get("allowed_read_roots", []):
            normalized = str(root).replace("\\", "/").strip("/").lower()
            if normalized not in {"input", "skill"}:
                errors.append(f"clean-room read root is not allowlisted: {root}")
        for item in manifest.get("immutable_inputs", []):
            input_path = Path(str(item.get("path", ""))) if isinstance(item, dict) else Path()
            if not isinstance(item, dict) or not item.get("sha256") or input_path.parts[:1] != ("input",):
                errors.append("clean-room immutable inputs must use input-relative paths and SHA256")
        return errors
    if len(writable.parts) < 2 or tuple(writable.parts[-2:]) != (benchmark_id, run_id):
        errors.append("writable_root must end with <benchmark_id>/<run_id>")
    for root in manifest.get("allowed_read_roots", []):
        normalized = str(root).replace("\\", "/").lower()
        if "/benchmarks/runs/" in normalized:
            errors.append("prior benchmark run archives cannot be model-visible read roots")
    for item in manifest.get("immutable_inputs", []):
        if not isinstance(item, dict) or not item.get("path") or not item.get("sha256"):
            errors.append("immutable_inputs entries require path and sha256")
    return errors


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def run_scoped_path_errors(path: str | Path, active_run_id: str, writable_root: str | Path) -> list[str]:
    """Reject generated artifacts outside the active run's only writable root."""
    target = Path(path)
    root = Path(writable_root)
    errors: list[str] = []
    if not _is_relative_to(target, root):
        errors.append("generated artifact path is outside allowed_write_root")
    # Clean-room roots are already unique runtime roots and intentionally use
    # runtime-relative paths such as ``workspace/outputs/...``.  The run ID is
    # carried by the workspace manifest/evidence records, not repeated in
    # every filesystem path.
    return errors


def validate_evidence_entry(entry: dict[str, Any], active_run_id: str | None = None) -> list[str]:
    """Bind run-produced evidence to a run and, where relevant, an experiment."""
    errors: list[str] = []
    evidence_type = str(entry.get("type", "")).upper()
    if evidence_type in RUN_EVIDENCE_TYPES:
        if not entry.get("run_id"):
            errors.append(f"{evidence_type} evidence requires run_id")
        if active_run_id and entry.get("run_id") != active_run_id and not entry.get("historical_evidence_reference"):
            errors.append("current run cannot consume evidence from another run without historical_evidence_reference")
    if evidence_type in {"CODE_RUN", "EXPERIMENT_RESULT", "VALIDATION_RESULT"} and not entry.get("experiment_id"):
        errors.append(f"{evidence_type} evidence requires experiment_id")
    return errors


def validate_active_evidence_set(data: dict[str, Any], active_run_id: str) -> list[str]:
    """Require one explicitly selected evidence version per active paper question."""
    errors: list[str] = []
    active = data.get("active_evidence_set") if isinstance(data, dict) else None
    if not isinstance(active, dict) or not active:
        return ["ACTIVE_EVIDENCE_SET must be a non-empty mapping"]
    for question, reference in active.items():
        if not isinstance(reference, dict):
            errors.append(f"active evidence {question} must be a mapping")
            continue
        if reference.get("run_id") != active_run_id:
            errors.append(f"active evidence {question} must belong to ACTIVE_RUN_ID")
        if not reference.get("experiment_id"):
            errors.append(f"active evidence {question} requires experiment_id")
    return errors


def validate_paper_claim(claim: dict[str, Any], active_set: dict[str, Any], active_run_id: str) -> list[str]:
    """Reject stale or inactive evidence versions in paper claims."""
    errors: list[str] = []
    if "association_contract" in claim:
        try:
            from .association_analysis import review_association_claim
        except ImportError:  # pragma: no cover - direct CLI
            from association_analysis import review_association_claim
        claim_text = claim.get("text", claim.get("claim", ""))
        if not isinstance(claim_text, str) or not claim_text.strip():
            errors.append("ASSOCIATION_CLAIM_TEXT_REQUIRED: include the actual paper sentence")
        else:
            reviewed = review_association_claim(claim_text, claim["association_contract"])
            errors.extend(item["code"] for item in reviewed["findings"])
    question = str(claim.get("question", ""))
    reference = claim.get("evidence_ref")
    if not isinstance(reference, dict):
        return errors + ["paper claim requires structured evidence_ref"]
    ref_run = reference.get("run_id")
    if ref_run != active_run_id and not claim.get("historical_evidence_reference"):
        errors.append("STALE_EVIDENCE_REFERENCE: paper claim references another run")
    selected = active_set.get("active_evidence_set", {}).get(question)
    if not isinstance(selected, dict):
        errors.append(f"paper claim question {question!r} has no active evidence selection")
    elif (reference.get("run_id"), reference.get("experiment_id")) != (selected.get("run_id"), selected.get("experiment_id")):
        errors.append("paper claim does not reference ACTIVE_EVIDENCE_SET")
    for field in ("artifact", "json_path"):
        if not reference.get(field):
            errors.append(f"paper claim evidence_ref requires {field}")
    return errors


def final_readiness_errors(state: dict[str, Any]) -> list[str]:
    """Block READY while any required question, artifact, or compliance check is open."""
    ready = str(state.get("status", "")).upper() == "READY" or state.get("ready") is True
    if not ready:
        return []
    errors: list[str] = []
    for question, status in state.get("required_questions", {}).items():
        if str(status).upper() != "COMPLETE":
            errors.append(f"{question} is incomplete; final_check cannot be READY")
    for artifact, status in state.get("required_artifacts", {}).items():
        if status is not True and str(status).upper() not in {"COMPLETE", "VERIFIED", "AVAILABLE"}:
            errors.append(f"required artifact {artifact} is missing or incomplete")
    if str(state.get("compliance_status", "")).upper() != "VERIFIED":
        errors.append("compliance status is not VERIFIED")
    return errors


def initialize_workspace(
    repo_root: Path,
    benchmark_id: str,
    run_id: str,
    created_at: str,
    immutable_inputs: list[Path],
) -> Path:
    """Create a fresh run-scoped workspace and its initial manifests."""
    runtime_root = repo_root.resolve()
    writable = runtime_root / "workspace"
    if writable.exists():
        raise FileExistsError(f"runtime workspace already exists: {writable}")
    for name in ("work", "outputs", "experiment-records", "evidence", "paper"):
        (writable / name).mkdir(parents=True, exist_ok=False if name == "work" else True)
    input_records = []
    for path in immutable_inputs:
        resolved = path.resolve()
        try:
            relative = resolved.relative_to(runtime_root).as_posix()
        except ValueError as exc:
            raise ValueError("immutable inputs must be inside the runtime root") from exc
        if not relative.startswith("input/"):
            raise ValueError("immutable inputs must be under input/")
        input_records.append({"path": relative, "sha256": sha256(resolved)})
    manifest = {
        "run_id": run_id,
        "benchmark_id": benchmark_id,
        "created_at": created_at,
        "active_run_id": run_id,
        "immutable_inputs": input_records,
        "isolation_mode": "clean_room",
        "writable_root": "workspace",
        "prior_run_artifacts_visible": False,
        "developer_repository_visible": False,
        "evaluator_files_visible": False,
        "allowed_read_roots": ["input", "skill"],
        "allowed_write_root": "workspace",
    }
    errors = validate_workspace_manifest(manifest)
    if errors:
        raise ValueError("; ".join(errors))
    (writable / "workspace-manifest.yaml").write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (writable / "evidence/active-evidence-set.yaml").write_text(
        yaml.safe_dump({"active_run_id": run_id, "active_evidence_set": {}}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return writable


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize or validate run-scoped provenance artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init = subparsers.add_parser("init-workspace")
    init.add_argument("--repo-root", type=Path, required=True)
    init.add_argument("--benchmark-id", required=True)
    init.add_argument("--run-id", required=True)
    init.add_argument("--created-at", required=True)
    init.add_argument("--immutable-input", type=Path, action="append", required=True)
    validate = subparsers.add_parser("validate-experiment")
    validate.add_argument("record", type=Path)
    args = parser.parse_args()
    if args.command == "init-workspace":
        print(initialize_workspace(args.repo_root, args.benchmark_id, args.run_id, args.created_at, args.immutable_input))
        return 0
    record = yaml.safe_load(args.record.read_text(encoding="utf-8"))
    errors = validate_experiment_record(record)
    if errors:
        print("FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
