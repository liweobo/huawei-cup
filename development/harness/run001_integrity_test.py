"""Check the canonicalized Run-001 evidence archive and source bindings."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "development/benchmarks/runs/historical_2024_c_core_loss/run-001"


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


def evidence_path(value: str) -> Path:
    path = Path(value)
    return ROOT / "development" / path if path.parts and path.parts[0] == "benchmarks" else RUN / path


def main() -> int:
    failures: list[str] = []
    manifest = yaml.safe_load((RUN / "run-manifest.yaml").read_text(encoding="utf-8"))
    raw = manifest.get("raw_archive", {})
    result_entry = raw.get("result_txt", {})
    result_path = RUN / result_entry.get("path", "")
    check("result.txt exists", result_path.is_file(), failures)
    check("result.txt byte count matches manifest", result_path.is_file() and result_path.stat().st_size == result_entry.get("bytes"), failures)
    check("result.txt SHA256 matches manifest", result_path.is_file() and sha256(result_path) == result_entry.get("sha256"), failures)

    archive_entry = raw.get("original_archive", {})
    check("original transfer archive metadata is retained", archive_entry.get("bytes") == 113550814 and len(str(archive_entry.get("sha256", ""))) == 64, failures)
    check("transfer archive is marked removed after canonicalization", manifest.get("archive_removed_after_canonicalization") is True and archive_entry.get("status") == "REMOVED_AFTER_CANONICALIZATION" and not (RUN / "raw/test.zip").exists(), failures)

    source = yaml.safe_load((ROOT / "development/benchmarks/problems/2024/C/source.yaml").read_text(encoding="utf-8"))
    source_ok = True
    for item in source.get("artifacts", []):
        path = ROOT / "development/benchmarks/problems/2024/C" / str(item.get("raw_path", ""))
        source_ok = source_ok and path.is_file() and path.stat().st_size == item.get("size") and sha256(path) == str(item.get("sha256", "")).lower()
    check("canonical problem raw inputs match source manifest", source_ok, failures)

    ledger = yaml.safe_load((RUN / "evidence-ledger.yaml").read_text(encoding="utf-8"))
    ledger_ok = True
    for item in ledger.get("evidence", []):
        path = evidence_path(str(item.get("artifact", "")))
        ledger_ok = ledger_ok and path.is_file() and sha256(path) == str(item.get("sha256", "")).lower()
    check("all retained evidence ledger entries resolve with SHA256", ledger_ok, failures)
    retained_paths = {str(item.get("artifact", "")) for item in ledger.get("evidence", [])}
    check("curated evidence projection retains required run artifacts", all(any(token in path for path in retained_paths) for token in ("q1_baseline.py", "q2_validate_protocol.py", "final_submission_check.md")), failures)

    check("raw archive is marked immutable", manifest.get("immutable_raw") is True, failures)
    check("run-001 outcome remains NEEDS_REVIEW", manifest.get("outcome") == "NEEDS_REVIEW", failures)
    print(f"\nRun-001 Integrity Test: {'PASS' if not failures else 'FAIL'} ({10 - len(failures)}/10 checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
