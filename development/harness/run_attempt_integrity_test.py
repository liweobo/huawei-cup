"""Check the frozen pre-model Run-004 launch-attempt record."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ATTEMPT = ROOT / "development/benchmarks/run-attempts/historical_2024_c_core_loss/run-004-attempt-001"


def check(label: str, ok: bool, failures: list[str]) -> None:
    print(f"{'PASS' if ok else 'FAIL'} | {label}")
    if not ok:
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    manifest_path = ATTEMPT / "attempt-manifest.yaml"
    error_path = ATTEMPT / "platform-error.txt"
    clean_manifest = ATTEMPT / "clean-room-manifest.yaml"
    visibility = ATTEMPT / "visibility-report.yaml"
    check("attempt manifest exists", manifest_path.is_file(), failures)
    check("platform error exists", error_path.is_file(), failures)
    check("prepared clean-room evidence is retained", clean_manifest.is_file() and visibility.is_file(), failures)
    if not manifest_path.is_file():
        print("\nRun Attempt Integrity: FAIL")
        return 1
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    check("attempt is distinct from behavioral archive", manifest.get("attempt_id") == "run-004-attempt-001" and not (ATTEMPT.parent.parent / "run-004").exists(), failures)
    check("execution stopped before Turn 1", manifest.get("execution_status") == "ABORTED_BEFORE_TURN_1" and manifest.get("behaviorally_evaluable") is False, failures)
    check("failure is infrastructure-owned", manifest.get("failure_category") == "PRE_MODEL_EXECUTION" and manifest.get("failure_owner") == "PLATFORM", failures)
    check("transport and binding are separate failures", set(manifest.get("subcategories", [])) == {"PLATFORM_TRANSPORT", "WORKSPACE_BINDING"}, failures)
    check("model behavior is not evaluated", manifest.get("model_behavior_p0") == "NOT_EVALUATED", failures)
    check("Turn 1 submission and response are distinguished", manifest.get("turn1_submission_attempted") is True and manifest.get("assistant_response_observed") is False, failures)
    check("retry retains Run-004 id", manifest.get("retry_allowed") is True and manifest.get("retry_run_id") == "run-004", failures)
    error_text = error_path.read_text(encoding="utf-8") if error_path.is_file() else ""
    check("transport error preserves missing call_id diagnosis", "function_call_output" in error_text and "call_id" in error_text, failures)
    clean = yaml.safe_load(clean_manifest.read_text(encoding="utf-8")) if clean_manifest.is_file() else {}
    report = yaml.safe_load(visibility.read_text(encoding="utf-8")) if visibility.is_file() else {}
    check("prepared clean room passed its own gate", clean.get("run_id") == "run-004" and clean.get("visibility_scan", {}).get("status") == "PASS", failures)
    check("retained visibility report has no forbidden match", report.get("status") == "PASS" and report.get("forbidden_matches") == [], failures)
    check("retained manifest and report hashes are reproducible", hashlib.sha256(clean_manifest.read_bytes()).hexdigest() == "f20f8f4696199701d6bbf9bea66323c5ff8e334062e1f2a10fbb12bcf521eb6f" and hashlib.sha256(visibility.read_bytes()).hexdigest() == "a4d38eb493f0c5df5ddcc766bb2db42ad6c7a1004284bc11ce7ea48b28673235", failures)
    print(f"\nRun Attempt Integrity: {'PASS' if not failures else 'FAIL'} ({14 - len(failures)}/14 checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
