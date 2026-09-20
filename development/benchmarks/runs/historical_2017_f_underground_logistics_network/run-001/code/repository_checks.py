"""Run existing repository checks without collecting frozen duplicate workspaces."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[4]
OUT = RUN / "validation-results"
OUT.mkdir(exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
checks = [("default-pytest", [sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider"]),
          ("development-tests", [sys.executable, "-B", "-m", "pytest", "development/tests", "-q", "-p", "no:cacheprovider"])]
names = ["smoke_test", "routing_test", "trigger_test", "adversarial_trigger_test", "behavior_contract_test",
         "trajectory_test", "trajectory_safety_test", "historical_artifact_test", "postmortem_regression_test",
         "problem_facts_test", "run001_integrity_test", "run002_integrity_test", "run003_integrity_test",
         "run_attempt_integrity_test", "clean_room_regression_test", "temporal_availability_regression_test",
         "runtime_binding_regression_test", "portable_runtime_regression_test", "repository_packaging_regression_test",
         "phase5_regression_test"]
checks += [(name, [sys.executable, "-B", f"development/harness/{name}.py"]) for name in names]
results = []
for name, command in checks:
    start = time.monotonic()
    result = subprocess.run(command, cwd=REPO, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = result.stdout + result.stderr
    (OUT / f"{name}.txt").write_text(log, encoding="utf-8")
    record = {"name": name, "command": command, "returncode": result.returncode,
              "seconds": round(time.monotonic() - start, 3), "log": f"validation-results/{name}.txt"}
    results.append(record)
    (OUT / "repository-checks.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(name, result.returncode, log[-800:].replace("\n", " "), flush=True)
