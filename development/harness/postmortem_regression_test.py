"""Deterministic regressions derived from the first real Layer B run."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from regression_contracts import canonical_audit_summary, contradiction_errors, validate_protocol_record


ROOT = Path(__file__).resolve().parents[2]
RUN_ARTIFACTS = ROOT / "development/benchmarks/runs/historical_2024_c_core_loss/run-001/raw/generated-artifacts"


def check(label: str, ok: bool, failures: list[str]) -> None:
    print(f"{'PASS' if ok else 'FAIL'} | {label}")
    if not ok:
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    raw_audit = json.loads((RUN_ARTIFACTS / "attachment1_audit.json").read_text(encoding="utf-8"))
    summary = canonical_audit_summary(raw_audit)
    check("canonical audit summary preserves duplicate_full_rows=1", summary["duplicate_full_rows"] == 1, failures)
    claims = [{"metric": "duplicate_full_rows", "value": 0}, {"metric": "duplicate_full_rows", "value": 1}]
    check("contradictory duplicate count is rejected", bool(contradiction_errors(summary, claims)), failures)
    consistent_claims = [{"metric": "duplicate_full_rows", "value": 1}]
    check("consistent canonical duplicate count is accepted", not contradiction_errors(summary, consistent_claims), failures)

    unchanged = {"planned_protocol": "GroupKFold exact frequency", "executed_protocol": "GroupKFold exact frequency", "protocol_changed": False, "change_reason": "", "status": "OBSERVED"}
    check("unchanged protocol is valid", not validate_protocol_record(unchanged), failures)
    drift = {"planned_protocol": "GroupKFold exact frequency", "executed_protocol": ["random KFold", "leave-temperature"], "protocol_changed": False, "change_reason": "", "status": "OBSERVED"}
    check("undeclared protocol drift is rejected", any("protocol_changed" in e for e in validate_protocol_record(drift)), failures)
    disclosed = copy.deepcopy(drift)
    disclosed.update({"protocol_changed": True, "change_reason": "Additional diagnostics and random folds were executed.", "status": "OBSERVED"})
    check("declared protocol drift is accepted", not validate_protocol_record(disclosed), failures)
    simulated = {"type": "SIMULATED_PERTURBATION", "claim": "input noise sensitivity"}
    check("sensitivity perturbation remains simulated", simulated["type"] != "NEW_MEASUREMENT", failures)
    print(f"\nPostmortem Regression Test: {'PASS' if not failures else 'FAIL'} ({7 - len(failures)}/7 checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
