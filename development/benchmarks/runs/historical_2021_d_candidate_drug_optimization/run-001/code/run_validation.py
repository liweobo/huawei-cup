"""Run effective repository and graduation-run validation without repairing frozen findings."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


RUN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = RUN_ROOT.parents[4]
LOG_DIR = REPO_ROOT / ".tmp" / "2021d-validation"
OUTPUT = RUN_ROOT / "outputs" / "validation-results.json"

HARNESSES = [
    "routing_test.py",
    "trigger_test.py",
    "adversarial_trigger_test.py",
    "behavior_contract_test.py",
    "trajectory_test.py",
    "trajectory_safety_test.py",
    "historical_artifact_test.py",
    "postmortem_regression_test.py",
    "problem_facts_test.py",
    "run001_integrity_test.py",
    "run002_integrity_test.py",
    "run003_integrity_test.py",
    "run_attempt_integrity_test.py",
    "clean_room_regression_test.py",
    "temporal_availability_regression_test.py",
    "runtime_binding_regression_test.py",
    "portable_runtime_regression_test.py",
    "repository_packaging_regression_test.py",
    "phase5_regression_test.py",
    "protocol_order_regression_test.py",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(name: str, args: list[str], expected: str = "PASS") -> dict:
    started = time.time()
    process = subprocess.run(
        args,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    payload = process.stdout
    (LOG_DIR / f"{name}.log").write_bytes(payload)
    text = payload.decode("utf-8", errors="replace")
    lines = [line for line in text.splitlines() if line.strip()]
    if expected == "PASS":
        status = "PASS" if process.returncode == 0 else "FAIL"
    else:
        status = expected
    return {
        "name": name,
        "command": args,
        "return_code": process.returncode,
        "classification": status,
        "duration_seconds": time.time() - started,
        "log_sha256": sha256(payload),
        "log_bytes": len(payload),
        "representative_lines": lines[-12:],
        "local_log": str((LOG_DIR / f"{name}.log").relative_to(REPO_ROOT)),
        "local_log_commit_policy": "EXCLUDED_LOCAL_CACHE",
    }


def main() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    python = sys.executable
    results = []
    package_output = LOG_DIR / "huawei-cup-2026-skill.zip"
    package_output.unlink(missing_ok=True)
    results.append(
        run(
            "smoke_test",
            [python, "development/harness/smoke_test.py"],
            expected="EXISTING_SMOKE_FAILURES_PRESERVED",
        )
    )
    for harness in HARNESSES:
        results.append(run(harness.removesuffix(".py"), [python, f"development/harness/{harness}"]))
    results.append(run("development_tests", [python, "-m", "pytest", "-q", "development/tests"]))
    results.append(
        run(
            "graduation_artifact_tests",
            [python, "-m", "pytest", "-q", str(RUN_ROOT / "code" / "test_run_artifacts.py")],
        )
    )
    results.append(
        run(
            "compileall",
            [
                python,
                "-m",
                "compileall",
                "-q",
                "development/harness",
                "development/tooling",
                "development/tests",
                "skill/scripts",
                str(RUN_ROOT / "code"),
            ],
        )
    )
    results.append(
        run(
            "skill_only_package",
            [
                python,
                "development/tooling/package_repository.py",
                "--skill-only",
                "--developer-repo",
                ".",
                "--output",
                str(package_output),
            ],
        )
    )
    effective_failures = [
        item["name"]
        for item in results
        if item["classification"] == "FAIL"
    ]
    summary = {
        "effective_python": python,
        "default_pytest_environment": "DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING: default interpreter lacks pytest; run-scoped isolated environment used",
        "smoke_finding_policy": "EXISTING_SMOKE_FAILURES_PRESERVED; frozen historical paths were not edited",
        "results": results,
        "effective_failure_count": len(effective_failures),
        "effective_failures": effective_failures,
        "status": "PASS" if not effective_failures else "FAIL",
    }
    OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "effective_failures": effective_failures}, indent=2))


if __name__ == "__main__":
    main()
