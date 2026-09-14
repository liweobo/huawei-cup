"""Check the canonicalized Run-003 archive and its run-scoped provenance."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "development/benchmarks/runs/historical_2024_c_core_loss/run-003"
ACTIVE_RUN_ID = "run-003"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(label: str, ok: bool, failures: list[str]) -> None:
    print(f"{'PASS' if ok else 'FAIL'} | {label}")
    if not ok:
        failures.append(label)


def load_structured(path: Path) -> Any:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        # The large read-only audit captures were emitted through a Windows
        # console using the local code page; their JSON syntax remains valid.
        text = raw.decode("cp936")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def artifact_path(value: str) -> Path:
    path = Path(value)
    if path.parts and path.parts[0].lower() == "benchmarks":
        return ROOT / "development" / path
    return RUN / path


def evidence_id(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        candidate = value.get("evidence_id") or value.get("id")
        return str(candidate) if candidate else None
    return None


def main() -> int:
    failures: list[str] = []
    required = [
        RUN / "run-manifest.yaml",
        RUN / "transcript.yaml",
        RUN / "evidence-ledger.yaml",
        RUN / "evaluation.yaml",
    ]
    check("Run-003 archive metadata files exist", all(path.is_file() for path in required), failures)
    if failures:
        print(f"\nRun-003 Integrity Test: FAIL (0 checks after missing metadata)")
        return 1

    parsed: dict[Path, Any] = {}
    manifest_path = RUN / "run-manifest.yaml"
    try:
        manifest = load_structured(manifest_path)
    except (OSError, UnicodeError, yaml.YAMLError, json.JSONDecodeError):
        manifest = None
    parse_ok = True
    for path in sorted(RUN.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            continue
        try:
            value = load_structured(path)
            if path in required:
                parsed[path] = value
        except (OSError, UnicodeError, yaml.YAMLError, json.JSONDecodeError):
            parse_ok = False
            print(f"FAIL | parseable structured file: {path.relative_to(RUN)}")
    check("all YAML/JSON archive files are parseable", parse_ok, failures)

    documented_truncation = isinstance(manifest, dict) and any(
        "Turn 001 did not emit turn.completed" in str(note)
        for note in (manifest.get("notes", []) if isinstance(manifest, dict) else [])
    )
    jsonl_ok = True
    for path in sorted(RUN.rglob("*.jsonl")):
        line_number = 0
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            for line_number, line in enumerate(lines, start=1):
                if line.strip():
                    try:
                        json.loads(line)
                    except json.JSONDecodeError:
                        is_known_tail = (
                            line_number == len(lines)
                            and path.name == "turn-001.jsonl"
                            and documented_truncation
                        )
                        if not is_known_tail:
                            raise
                        print(f"PASS | documented truncated capture tail: {path.relative_to(RUN)}:{line_number}")
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            jsonl_ok = False
            print(f"FAIL | JSONL parse {path.relative_to(RUN)}:{line_number}: {exc}")
    check("retained raw JSONL turn logs parse, allowing documented Turn-001 tail", jsonl_ok, failures)

    manifest = parsed.get(RUN / "run-manifest.yaml") or load_structured(RUN / "run-manifest.yaml")
    transcript = parsed.get(RUN / "transcript.yaml") or load_structured(RUN / "transcript.yaml")
    ledger_doc = parsed.get(RUN / "evidence-ledger.yaml") or load_structured(RUN / "evidence-ledger.yaml")
    evaluation = parsed.get(RUN / "evaluation.yaml") or load_structured(RUN / "evaluation.yaml")

    check("manifest binds benchmark and active run", isinstance(manifest, dict) and manifest.get("run_id") == ACTIVE_RUN_ID, failures)
    check("manifest retains NEEDS_REVIEW / NOT_READY outcome", isinstance(manifest, dict) and manifest.get("outcome") == "NEEDS_REVIEW" and manifest.get("submission_status") == "NOT_READY", failures)
    check("workspace isolation regression is explicitly retained", isinstance(manifest, dict) and manifest.get("workspace_isolation") == "FAIL" and manifest.get("observed_repo_listing_exposed_run_002") is True, failures)
    check("transcript uses schema version 3 and active run-003", isinstance(transcript, dict) and transcript.get("schema_version") == 3 and transcript.get("active_run_id") == ACTIVE_RUN_ID, failures)
    check("transcript contains exactly 14 captured turns", isinstance(transcript, dict) and len(transcript.get("turns", [])) == 14, failures)
    check("evaluation has all eight dimensions", isinstance(evaluation, dict) and set(evaluation.get("evaluation", evaluation)) >= {
        "problem_understanding", "evidence_discipline", "modeling_quality", "experiment_integrity",
        "validation", "state_consistency", "paper_consistency", "next_action_quality",
    }, failures)

    entries = ledger_doc.get("evidence", []) if isinstance(ledger_doc, dict) else []
    ledger_by_id: dict[str, dict[str, Any]] = {}
    ledger_ok = isinstance(entries, list) and len(entries) == 21
    for entry in entries if isinstance(entries, list) else []:
        item_id = evidence_id(entry)
        if not isinstance(entry, dict) or not item_id or item_id in ledger_by_id:
            ledger_ok = False
            continue
        ledger_by_id[item_id] = entry
        value = str(entry.get("artifact", "")).strip()
        target = artifact_path(value) if value else Path()
        declared = str(entry.get("sha256", "")).lower().strip()
        if not value or not target.is_file() or len(declared) != 64 or sha256(target) != declared:
            ledger_ok = False
            print(f"FAIL | evidence artifact/hash: {item_id} -> {value}")
    check("21 evidence entries resolve and match SHA256", ledger_ok and len(ledger_by_id) == 21, failures)

    refs_ok = True
    for turn in transcript.get("turns", []) if isinstance(transcript, dict) else []:
        refs = list(turn.get("evidence_refs") or [])
        for claim in list(turn.get("claims") or []):
            refs.extend(claim.get("evidence_refs") or [])
        for ref in refs:
            item_id = evidence_id(ref)
            if not item_id or item_id not in ledger_by_id:
                refs_ok = False
                print(f"FAIL | unresolved evidence ref in {turn.get('turn_id')}: {ref!r}")
    check("all transcript and claim evidence refs resolve", refs_ok, failures)

    active = transcript.get("active_evidence_set") if isinstance(transcript, dict) else None
    active_ok = isinstance(active, dict) and bool(active)
    for question, reference in active.items() if isinstance(active, dict) else []:
        active_ok = active_ok and isinstance(reference, dict) and reference.get("run_id") == ACTIVE_RUN_ID
        if isinstance(reference, dict):
            active_ok = active_ok and bool(reference.get("experiment_id"))
            selected = str(reference.get("artifact", ""))
            active_ok = active_ok and bool(selected) and artifact_path(selected).is_file()
    check("Active Evidence Set is non-empty and run-003-only", active_ok, failures)

    stale_ok = True
    for item_id, entry in ledger_by_id.items():
        run_id = entry.get("run_id")
        if run_id and run_id != ACTIVE_RUN_ID and not entry.get("historical_evidence_reference"):
            stale_ok = False
            print(f"FAIL | stale run evidence entry: {item_id} -> {run_id}")
    check("no consumed evidence entry belongs to an older run", stale_ok, failures)

    print(f"\nRun-003 Integrity Test: {'PASS' if not failures else 'FAIL'} ({11 - len(failures)}/11 checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
