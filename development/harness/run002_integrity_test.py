"""Check the canonicalized Run-002 evidence archive and provenance bindings."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "development/benchmarks/runs/historical_2024_c_core_loss/run-002"


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


def main() -> int:
    failures: list[str] = []
    manifest_path = RUN / "run-manifest.yaml"
    transcript_path = RUN / "transcript.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    raw = manifest.get("raw_archive", {})

    for key in ("result_txt", "desktop_zip"):
        entry = raw.get(key, {})
        check(f"{key} original metadata is retained", entry.get("bytes", 0) > 0 and len(str(entry.get("sha256", ""))) == 64, failures)
        check(f"{key} transfer artifact is explicitly absent after canonicalization", entry.get("status") == "NOT_RETAINED_AFTER_CANONICALIZATION" and not (RUN / entry.get("original_path", "")).exists(), failures)

    canonical = raw.get("canonical_transcript", {})
    transcript_canonical_path = RUN / canonical.get("path", "")
    check("canonical structured transcript exists", transcript_canonical_path.is_file(), failures)
    check("canonical transcript byte count matches manifest", transcript_canonical_path.is_file() and transcript_canonical_path.stat().st_size == canonical.get("bytes"), failures)
    check("canonical transcript SHA256 matches manifest", transcript_canonical_path.is_file() and sha256(transcript_canonical_path) == str(canonical.get("sha256", "")).lower(), failures)
    check("manifest points to the canonical structured transcript", manifest.get("structured_transcript") == canonical.get("path"), failures)
    check("archive removal is marked and raw metadata remains immutable", manifest.get("archive_removed_after_canonicalization") is True and manifest.get("immutable_raw") is True, failures)

    ledger = yaml.safe_load((RUN / "evidence-ledger.yaml").read_text(encoding="utf-8"))
    ledger_ok = True
    for item in ledger.get("evidence", []):
        path_value = str(item.get("artifact", ""))
        path = ROOT / "development" / path_value if path_value.startswith("benchmarks/") else RUN / path_value
        ledger_ok = ledger_ok and path.is_file() and sha256(path) == str(item.get("sha256", "")).lower()
    check("retained evidence ledger entries resolve with SHA256", ledger_ok, failures)
    active_evidence = RUN / "observed-artifacts/outputs/20260831_evidence_registry/20260831T163625"
    check("selected active evidence run is retained", active_evidence.is_dir() and (active_evidence / "evidence_manifest.json").is_file(), failures)
    check("run-002 outcome remains NEEDS_REVIEW", manifest.get("outcome") == "NEEDS_REVIEW", failures)

    transcript = yaml.safe_load(transcript_path.read_text(encoding="utf-8"))
    check("transcript uses schema version 3", transcript.get("schema_version") == 3, failures)
    check("transcript binds active run to run-002", transcript.get("active_run_id") == "run-002", failures)
    # Run-003 is now a completed sibling benchmark archive.  The historical
    # Run-002 check should verify separation, not require later runs to be
    # absent from the evolving repository.
    run003 = RUN.parent / "run-003"
    check("Run-003 archive is retained as a separate sibling", run003 != RUN and (run003 / "run-manifest.yaml").is_file(), failures)

    reconstructed_path = RUN / "analysis/reconstructed-workspace-manifest.yaml"
    source_path = ROOT / "development/benchmarks/problems/2024/C/source.yaml"
    reconstructed = yaml.safe_load(reconstructed_path.read_text(encoding="utf-8"))
    source = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    source_hashes = {
        Path(item["raw_path"]).name: str(item["sha256"]).lower()
        for item in source.get("artifacts", [])
        if isinstance(item, dict) and item.get("raw_path") and item.get("sha256")
    }
    manifest_inputs = reconstructed.get("immutable_inputs", [])
    check(
        "reconstructed manifest immutable input hashes match source manifest",
        bool(manifest_inputs)
        and all(
            source_hashes.get(Path(str(item.get("path", ""))).name) == str(item.get("sha256", "")).lower()
            for item in manifest_inputs
        ),
        failures,
    )

    total = 15
    print(f"\nRun-002 Integrity Test: {'PASS' if not failures else 'FAIL'} ({total - len(failures)}/{total} checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
