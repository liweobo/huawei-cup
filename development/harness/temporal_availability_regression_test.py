"""Targeted regression for generic temporal availability gates."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill.scripts.runtime_provenance import apply_temporal_gate, validate_experiment_record
from skill.scripts.temporal_availability import TemporalAvailabilityError, assert_temporal_aggregation_input, filter_before_aggregation


def check(label: str, ok: bool, failures: list[str]) -> None:
    print(f"{'PASS' if ok else 'FAIL'} | {label}")
    if not ok:
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    frame = pd.DataFrame({"entity": ["p1", "p1", "p2"], "time_h": [100, 1000, 2200], "volume": [2.0, 4.0, 999.0]})
    filtered, contract = filter_before_aggregation(frame, time_column="time_h", entity_key="entity", target="day90", target_time=2160)
    check("target horizon is identified before feature generation", contract["allowed_feature_horizon"] == 2160, failures)
    check("post-horizon row is found", contract["post_horizon_records"] == 1, failures)
    check("affected entity count is reported", contract["excluded_entity_count"] == 1, failures)
    check("filter precedes aggregation", filtered["volume"].max() == 4.0, failures)
    check("future row is absent from allowed input", 2200 not in filtered["time_h"].tolist(), failures)
    try:
        assert_temporal_aggregation_input(frame, contract)
    except TemporalAvailabilityError as exc:
        rejected = "FUTURE_INFORMATION_LEAKAGE" in str(exc)
    else:
        rejected = False
    check("aggregation-before-filter is rejected", rejected, failures)
    base = {
        "experiment_id": "EXP-TEMP-REGRESSION", "run_id": "run-fixture", "created_at": "2026-01-01T00:00:00Z",
        "problem": "synthetic", "question": "Q", "status": "OBSERVED", "updated_by_workflow": "run_experiment",
        "planned_protocol": {"aggregation_required": True}, "executed_protocol": {"aggregation_required": True},
        "protocol_changed": False, "change_reason": "", "comparable_to_original_plan": True,
        "input_artifacts": ["input"], "code_artifacts": ["code"], "output_artifacts": ["output"],
        "random_seed": 1, "metrics": {"score": 0.0}, "evidence_ids": ["EV-TEMP"],
    }
    invalidated = apply_temporal_gate(base, contract, future_rows_entered_aggregation=True)
    check("future aggregation invalidates experiment", invalidated["status"] == "INVALIDATED", failures)
    check("invalidated record remains provenance-valid", not validate_experiment_record(invalidated), failures)
    unknown = pd.DataFrame({"entity": ["p1"], "time_h": [100], "volume": [1.0]})
    try:
        filter_before_aggregation(unknown, time_column="time_h", entity_key="entity")
    except TemporalAvailabilityError as exc:
        blocked = "UNVERIFIED" in str(exc)
    else:
        blocked = False
    check("unknown horizon blocks observed feature generation", blocked, failures)
    print(f"\nTemporal Availability Regression: {'PASS' if not failures else 'FAIL'} ({10 - len(failures)}/10 checks)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

