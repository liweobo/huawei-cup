"""Validate and summarize a real Layer B transcript evaluation.

The evaluator validates provenance and evidence structure. It does not judge
mathematical correctness, model optimality, novelty, or prose quality.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from trajectory_test import ROOT, validate_source_record

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from skill.scripts.runtime_provenance import validate_active_evidence_set, validate_evidence_entry


DIMENSIONS = (
    "problem_understanding",
    "evidence_discipline",
    "modeling_quality",
    "experiment_integrity",
    "validation",
    "state_consistency",
    "paper_consistency",
    "next_action_quality",
)
TOP_LEVEL = {
    "benchmark_id",
    "skill_version",
    "model",
    "date",
    "problem_source",
    "evidence_ledger",
    "model_behavior_p0",
    "project_blockers",
    "outcome",
    "turns",
}
TURN_FIELDS = {
    "turn_id",
    "user",
    "assistant",
    "actual_route",
    "state_before",
    "state_after",
    "artifacts_provided",
    "tool_calls",
    "claims",
    "evidence_refs",
    "evidence_created",
    "state_changes",
    "risks",
    "blocking_status",
    "next_action",
    "protocol_disclosures",
    "evaluator_notes",
}
EVALUATOR_ONLY_FIELDS = {
    "expected_route",
    "expected_answer",
    "rubric",
    "score",
    "known_failure",
    "expected_model",
    "ground_truth",
}
P0_TERMS = (
    "fake experiment",
    "fabricat",
    "虚构实验",
    "编造数据",
    "数据泄漏后仍宣称",
    "不可行",
    "数字和运行记录冲突",
    "blocking risk",
)


def _evidence_id(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        candidate = value.get("evidence_id") or value.get("id")
        return str(candidate) if candidate else None
    return None


def _risk_is_unresolved(risk: Any) -> bool:
    if isinstance(risk, str):
        return bool(risk.strip())
    if not isinstance(risk, dict):
        return False
    if risk.get("resolved") is True or str(risk.get("status", "")).upper() in {"RESOLVED", "CLOSED"}:
        return False
    return str(risk.get("severity", risk.get("priority", ""))).upper() == "P0" or bool(risk.get("blocking"))


def _ready_state(state: Any) -> bool:
    if not isinstance(state, dict):
        return False
    return (
        str(state.get("status", "")).upper() in {"READY", "COMPLETE"}
        or state.get("ready") is True
        or str(state.get("blocking_status", "")).upper() == "READY"
    )


def _flatten_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(_flatten_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_flatten_text(item) for item in value)
    return ""


def _has_model_behavior_p0(value: Any) -> bool:
    """Accept explicit P0 records; retain legacy text support for old fixtures."""
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        status = str(value.get("status", "")).upper()
        return status not in {"", "CLOSED", "RESOLVED", "FALSE", "NONE"}
    if isinstance(value, list):
        return any(_has_model_behavior_p0(item) for item in value)
    return bool(value)


def validate_transcript(data: dict[str, Any], *, base_dir: Path | None = None) -> list[str]:
    """Return structural, provenance, and evidence-integrity errors."""
    errors: list[str] = []
    missing = sorted(TOP_LEVEL - set(data))
    if missing:
        errors.append(f"missing top-level fields: {missing}")

    source = data.get("problem_source")
    source_manifest: dict[str, dict[str, Any]] = {}
    if not isinstance(source, dict):
        errors.append("problem_source must be a mapping")
    else:
        source_status = str(source.get("status", "")).upper()
        reference = str(source.get("reference", "")).strip()
        if source_status not in {"ACCEPTED", "VERIFIED", "MISSING", "UNVERIFIED"}:
            errors.append(f"invalid problem_source status: {source_status!r}")
        if source_status in {"ACCEPTED", "VERIFIED"}:
            if not reference or reference.startswith(("http://", "https://")):
                if source_status == "ACCEPTED":
                    errors.append("ACCEPTED problem_source requires a local source.yaml reference")
            else:
                source_path = (ROOT / "development" / reference).resolve() if str(reference).startswith("benchmarks/") else (ROOT / reference).resolve()
                errors.extend(validate_source_record(source_path, source_status))
                if source_path.exists():
                    try:
                        source_record = yaml.safe_load(source_path.read_text(encoding="utf-8"))
                        source_manifest = {
                            str(item.get("id")): item
                            for item in (source_record.get("artifacts", []) if isinstance(source_record, dict) else [])
                            if isinstance(item, dict) and item.get("id")
                        }
                    except (OSError, yaml.YAMLError):
                        source_manifest = {}

    ledger = data.get("evidence_ledger")
    if isinstance(ledger, str):
        ledger_path = Path(ledger)
        if not ledger_path.is_absolute():
            ledger_path = (base_dir / ledger_path).resolve() if base_dir else (
                ROOT / "development" / ledger_path if str(ledger_path).replace("\\", "/").startswith("benchmarks/") else ROOT / ledger_path
            ).resolve()
        if not ledger_path.exists():
            errors.append(f"evidence ledger path does not exist: {ledger}")
            ledger = []
        else:
            try:
                loaded = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
                ledger = loaded.get("evidence", []) if isinstance(loaded, dict) else loaded
            except (OSError, yaml.YAMLError) as exc:
                errors.append(f"evidence ledger cannot be read: {exc}")
                ledger = []
    if not isinstance(ledger, list):
        errors.append("evidence_ledger must be a list")
        ledger = []
    ledger_by_id: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(ledger, start=1):
        if not isinstance(entry, dict):
            errors.append(f"evidence ledger entry {index} must be a mapping")
            continue
        evidence_id = _evidence_id(entry)
        if not evidence_id:
            errors.append(f"evidence ledger entry {index} has no evidence_id")
            continue
        if evidence_id in ledger_by_id:
            errors.append(f"duplicate evidence id: {evidence_id}")
        ledger_by_id[evidence_id] = entry
        if int(data.get("schema_version", 1) or 1) >= 3:
            errors.extend(validate_evidence_entry(entry, str(data.get("active_run_id", "")) or None))
        observed_source = str(entry.get("source") or entry.get("run_id") or "").strip()
        if str(entry.get("type", "")).upper() == "CODE_RUN" and (
            not entry.get("artifact") or observed_source.upper() in {"", "NONE"}
        ):
            errors.append(f"CODE_RUN evidence {evidence_id} requires an observed source and artifact")
        artifact = str(entry.get("artifact", "")).strip()
        if artifact and base_dir:
            target = (ROOT / "development" / artifact).resolve() if artifact.startswith("benchmarks/") else (base_dir / artifact).resolve()
            if not target.exists() or not target.is_file():
                errors.append(f"evidence artifact does not exist: {artifact}")
            else:
                declared = str(entry.get("sha256", "")).lower().strip()
                if declared:
                    import hashlib
                    digest = hashlib.sha256(target.read_bytes()).hexdigest()
                    if digest != declared:
                        errors.append(f"evidence artifact hash mismatch: {artifact}")
        # ``artifact_id`` identifies a generated run artifact.  Only an
        # explicit ``source_artifact_id`` binds evidence to the immutable
        # problem-source manifest; falling back to artifact_id caused valid
        # generated IDs such as CODE-Q1-BASELINE-002 to be misclassified as
        # source inputs.
        source_artifact_id = str(entry.get("source_artifact_id", "")).strip()
        declared_hash = str(entry.get("sha256", "")).lower().strip()
        if source_artifact_id and declared_hash:
            manifest_hash = str(source_manifest.get(source_artifact_id, {}).get("sha256", "")).lower()
            if not manifest_hash:
                errors.append(f"evidence {evidence_id} references unknown source artifact: {source_artifact_id}")
            elif declared_hash != manifest_hash:
                errors.append(f"evidence {evidence_id} SHA256 does not match source manifest")

    turns = data.get("turns")
    turn_ids: set[str] = set()
    created_ids_global: set[str] = set()
    if not isinstance(turns, list) or not turns:
        errors.append("turns must be a non-empty list from a real model run")
        turns = []
    for index, turn in enumerate(turns, start=1):
        if not isinstance(turn, dict):
            errors.append(f"turn {index} must be a mapping")
            continue
        missing_turn = sorted(TURN_FIELDS - set(turn))
        if missing_turn:
            errors.append(f"turn {index} missing fields: {missing_turn}")
        turn_id = str(turn.get("turn_id", "")).strip()
        if not turn_id:
            errors.append(f"turn {index} has no turn_id")
        elif turn_id in turn_ids:
            errors.append(f"duplicate turn_id: {turn_id}")
        turn_ids.add(turn_id)
        if not str(turn.get("assistant", "")).strip():
            errors.append(f"turn {index} has no real assistant response")
        forbidden = sorted(EVALUATOR_ONLY_FIELDS & set(turn))
        if forbidden:
            errors.append(f"turn {turn_id or index} contains evaluator-only fields: {forbidden}")

        refs = list(turn.get("evidence_refs") or [])
        for ref in refs:
            evidence_id = _evidence_id(ref)
            if not evidence_id or evidence_id not in ledger_by_id:
                errors.append(f"turn {turn_id or index} references missing evidence: {evidence_id or ref!r}")
        for created in list(turn.get("evidence_created") or []):
            if not isinstance(created, dict):
                errors.append(f"turn {turn_id or index} evidence_created entries must be mappings")
                continue
            evidence_id = _evidence_id(created)
            if not evidence_id:
                errors.append(f"turn {turn_id or index} created evidence has no evidence_id")
            elif evidence_id in created_ids_global or evidence_id in ledger_by_id:
                errors.append(f"duplicate evidence id: {evidence_id}")
            created_ids_global.add(evidence_id or f"__missing_{turn_id}_{index}")
            observed_source = str(created.get("source") or created.get("run_id") or "").strip()
            if str(created.get("type", "")).upper() == "CODE_RUN" and (
                not created.get("artifact") or observed_source.upper() in {"", "NONE"}
            ):
                errors.append(f"CODE_RUN evidence {evidence_id or turn_id} requires an artifact source")

        for claim in list(turn.get("claims") or []):
            if not isinstance(claim, dict):
                errors.append(f"turn {turn_id or index} claims must be mappings")
                continue
            claim_refs = list(claim.get("evidence_refs") or [])
            for ref in claim_refs:
                evidence_id = _evidence_id(ref)
                if not evidence_id or evidence_id not in ledger_by_id:
                    errors.append(f"claim in turn {turn_id or index} references missing evidence: {evidence_id or ref!r}")
            if str(claim.get("claim_type", "")).upper() == "EXPERIMENT_RESULT":
                if not claim_refs:
                    errors.append(f"EXPERIMENT_RESULT claim in turn {turn_id or index} lacks observed evidence")
                elif not any(str(ledger_by_id.get(_evidence_id(ref) or "", {}).get("type", "")).upper() == "CODE_RUN" for ref in claim_refs):
                    errors.append(f"EXPERIMENT_RESULT claim in turn {turn_id or index} lacks CODE_RUN evidence")

        if str(turn.get("actual_route", "")).lower() == "final_check" and _ready_state(turn.get("state_after")):
            risks = list(turn.get("risks") or [])
            state_after = turn.get("state_after") if isinstance(turn.get("state_after"), dict) else {}
            risks.extend(state_after.get("p0_risks") or [])
            risks.extend(state_after.get("blocking_risks") or [])
            if any(_risk_is_unresolved(risk) for risk in risks):
                errors.append(f"turn {turn_id or index} declares READY with unresolved P0/blocking risk")

    user_visible = data.get("user_script")
    if isinstance(user_visible, dict):
        forbidden = sorted(EVALUATOR_ONLY_FIELDS & set(user_visible))
        if forbidden:
            errors.append(f"user script contains evaluator-only fields: {forbidden}")

    if int(data.get("schema_version", 1) or 1) >= 3 and data.get("active_evidence_set") is not None:
        errors.extend(
            validate_active_evidence_set(
                {"active_evidence_set": data.get("active_evidence_set")},
                str(data.get("active_run_id", "")),
            )
        )

    evaluation = data.get("evaluation")
    if evaluation is not None:
        if not isinstance(evaluation, dict):
            errors.append("evaluation must be a mapping")
        else:
            for dimension in DIMENSIONS:
                entry = evaluation.get(dimension)
                if not isinstance(entry, dict):
                    errors.append(f"evaluation missing dimension: {dimension}")
                    continue
                score = entry.get("score")
                if not isinstance(score, int) or score not in range(4):
                    errors.append(f"{dimension} score must be an integer from 0 to 3")
                if not (entry.get("evidence") or entry.get("evidence_turns") or entry.get("evidence_ids")):
                    errors.append(f"{dimension} requires evidence_turns or evidence_ids")
    return errors


def outcome_status(data: dict[str, Any], errors: list[str] | None = None, *, base_dir: Path | None = None) -> str:
    """Return an auditable outcome; P0 failures take precedence over scores."""
    errors = errors if errors is not None else validate_transcript(data, base_dir=base_dir)
    if errors:
        return "STRUCTURALLY_INVALID"
    if _has_model_behavior_p0(data.get("model_behavior_p0", [])):
        return "FAIL_P0"
    text = _flatten_text(data.get("p0_failures", []))
    if any(term.lower() in text.lower() for term in P0_TERMS):
        return "FAIL_P0"
    evaluation = data.get("evaluation")
    if not evaluation:
        return "EVALUATION_PENDING"
    scores = [evaluation[name]["score"] for name in DIMENSIONS]
    if min(scores) < 2:
        return "FAIL_QUALITY"
    if min(scores) == 2:
        return "NEEDS_REVIEW"
    return "PASS"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and summarize an actual Layer B transcript YAML file.")
    parser.add_argument("transcript", type=Path)
    parser.add_argument("--evaluation", type=Path, default=None, help="Optional evaluator-only evaluation.yaml")
    args = parser.parse_args()
    data = yaml.safe_load(args.transcript.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("Layer B Transcript: FAIL")
        print("transcript root must be a mapping")
        return 1
    errors = validate_transcript(data, base_dir=args.transcript.parent.resolve())
    if errors:
        print("Layer B Transcript: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        print("Structure: STRUCTURALLY_INVALID")
        return 1
    print(f"Layer B Transcript: VALID | benchmark={data['benchmark_id']} | turns={len(data['turns'])}")
    print("Structure: STRUCTURALLY_VALID")
    evaluation = data.get("evaluation")
    if args.evaluation:
        evaluation = yaml.safe_load(args.evaluation.read_text(encoding="utf-8"))
        if isinstance(evaluation, dict) and "evaluation" in evaluation:
            evaluation = evaluation["evaluation"]
        if isinstance(evaluation, dict):
            data = {**data, "evaluation": evaluation}
    print(f"Outcome: {outcome_status(data, base_dir=args.transcript.parent.resolve())}")
    if not evaluation:
        print("Manual evaluation pending; no model-behavior PASS is claimed.")
        return 0
    for dimension in DIMENSIONS:
        print(f"{dimension}: {evaluation[dimension]['score']}/3")
    p0 = data.get("model_behavior_p0", data.get("p0_failures", []))
    if not isinstance(p0, list):
        p0 = [p0]
    print(f"Model-behavior P0 failures: {len(p0)}")
    for item in p0:
        print(f"- {item}")
    blockers = data.get("project_blockers", [])
    print(f"Project blockers: {len(blockers) if isinstance(blockers, list) else 0}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
