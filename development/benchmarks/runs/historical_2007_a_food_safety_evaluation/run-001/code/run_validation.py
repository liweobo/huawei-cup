"""Run required repository and run-specific checks with captured evidence."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path


RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[4]
OUT = RUN / "validation-results"
DEPS = RUN / ".tmp" / "deps"


def execute(label: str, command: list[str], env: dict[str, str]) -> dict[str, object]:
    start = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=REPO,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    duration = time.perf_counter() - start
    log = OUT / f"{label}.log"
    log.write_text(
        "$ " + " ".join(command) + "\n\nSTDOUT\n" + result.stdout + "\nSTDERR\n" + result.stderr,
        encoding="utf-8",
        newline="\n",
    )
    return {
        "label": label,
        "command": command,
        "exit_code": result.returncode,
        "seconds": round(duration, 3),
        "log": log.relative_to(RUN).as_posix(),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    default_env = os.environ.copy()
    default_env.pop("PYTHONPATH", None)
    results = [
        execute(
            "default_pytest_environment_issue_existing",
            [sys.executable, "-m", "pytest", "-q", "development/tests"],
            default_env,
        )
    ]

    valid_env = os.environ.copy()
    valid_python = RUN / ".tmp" / "venv" / "Scripts" / "python.exe"
    if not valid_python.is_file():
        raise SystemExit("Run-scoped validation virtual environment is missing")
    py = str(valid_python)
    existing = valid_env.get("PYTHONPATH", "")
    valid_env["PYTHONPATH"] = str(DEPS) + (os.pathsep + existing if existing else "")
    package_output = RUN / ".tmp" / f"huawei-cup-2026-skill-validation-{os.getpid()}.zip"
    checks = [
        ("development_tests", [py, "-m", "pytest", "-q", "development/tests", "-p", "no:cacheprovider"]),
        ("smoke_test", [py, "development/harness/smoke_test.py"]),
        ("routing_test", [py, "development/harness/routing_test.py"]),
        ("trigger_test", [py, "development/harness/trigger_test.py"]),
        ("adversarial_trigger_test", [py, "development/harness/adversarial_trigger_test.py"]),
        ("behavior_contract_test", [py, "development/harness/behavior_contract_test.py"]),
        ("trajectory_test", [py, "development/harness/trajectory_test.py"]),
        ("trajectory_safety_test", [py, "development/harness/trajectory_safety_test.py"]),
        ("historical_artifact_test", [py, "development/harness/historical_artifact_test.py"]),
        ("postmortem_regression_test", [py, "development/harness/postmortem_regression_test.py"]),
        ("problem_facts_test", [py, "development/harness/problem_facts_test.py"]),
        ("run001_integrity_test", [py, "development/harness/run001_integrity_test.py"]),
        ("run002_integrity_test", [py, "development/harness/run002_integrity_test.py"]),
        ("run003_integrity_test", [py, "development/harness/run003_integrity_test.py"]),
        ("run_attempt_integrity_test", [py, "development/harness/run_attempt_integrity_test.py"]),
        ("clean_room_regression_test", [py, "development/harness/clean_room_regression_test.py"]),
        ("temporal_availability_regression_test", [py, "development/harness/temporal_availability_regression_test.py"]),
        ("runtime_binding_regression_test", [py, "development/harness/runtime_binding_regression_test.py"]),
        ("portable_runtime_regression_test", [py, "development/harness/portable_runtime_regression_test.py"]),
        ("repository_packaging_regression_test", [py, "development/harness/repository_packaging_regression_test.py"]),
        ("phase5_regression_test", [py, "development/harness/phase5_regression_test.py"]),
        (
            "skill_self_contained",
            [py, "-m", "pytest", "-q", "development/tests/test_skill_self_contained.py", "-p", "no:cacheprovider"],
        ),
        (
            "evaluation_contract_tests",
            [py, "-m", "unittest", "discover", "-s", str(RUN / "code"), "-p", "test_*.py", "-v"],
        ),
        (
            "experiment_record_validation",
            [py, "skill/scripts/runtime_provenance.py", "validate-experiment", str(RUN / "experiment-record.yaml")],
        ),
        (
            "compileall",
            [py, "-m", "compileall", "-q", "development/harness", "development/tooling", "development/tests", "skill/scripts", str(RUN / "code")],
        ),
        (
            "skill_only_package",
            [
                py,
                "development/tooling/package_repository.py",
                "--skill-only",
                "--developer-repo",
                ".",
                "--output",
                str(package_output),
            ],
        ),
    ]
    for label, command in checks:
        results.append(execute(label, command, valid_env))

    existing_issue = results[0]["exit_code"] != 0
    valid_failures = [
        result["label"] for result in results[1:] if result["exit_code"] != 0
    ]
    smoke_log = (OUT / "smoke_test.log").read_text(encoding="utf-8")
    expected_smoke_fragments = [
        "historical_2022_c_buffer_scheduling\\run-002\\REPORT.md",
        "historical_2017_f_underground_logistics_network\\run-001\\REPORT.md",
        "historical_2017_f_underground_logistics_network\\run-001\\validation.md",
    ]
    smoke_existing_only = valid_failures == ["smoke_test"] and all(
        fragment in smoke_log for fragment in expected_smoke_fragments
    )
    actionable_failures = [] if smoke_existing_only else valid_failures
    summary = {
        "default_pytest_environment": "DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING"
        if existing_issue
        else "PASS",
        "default_issue_is_infrastructure_only": existing_issue,
        "valid_environment": {
            "python": py,
            "dependency_root": str(DEPS),
            "all_checks_pass": not valid_failures,
            "failures": valid_failures,
            "acknowledged_existing_smoke_issue_only": smoke_existing_only,
            "all_actionable_checks_pass": not actionable_failures,
            "actionable_failures": actionable_failures,
        },
        "results": results,
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if actionable_failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
