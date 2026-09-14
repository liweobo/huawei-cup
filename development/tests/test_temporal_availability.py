from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from skill.scripts.data_audit import audit_file
from skill.scripts.runtime_provenance import (
    apply_temporal_gate,
    temporal_scope_from_contract,
    validate_experiment_record,
)
from skill.scripts.temporal_availability import (
    TemporalAvailabilityError,
    assert_temporal_aggregation_input,
    filter_before_aggregation,
    validate_temporal_availability,
)


def longitudinal_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "entity": ["a", "a", "a", "b", "b"],
            "time_h": [100, 1000, 2200, 100, 2200],
            "value": [2, 4, 10_000, 3, 9_999],
        }
    )


def test_post_outcome_observations_are_excluded_before_aggregation() -> None:
    filtered, contract = filter_before_aggregation(
        longitudinal_frame(), time_column="time_h", entity_key="entity",
        target="outcome", target_time=2160, task="prediction",
    )
    assert filtered["time_h"].tolist() == [100, 1000, 100]
    assert filtered.groupby("entity")["value"].max().to_dict() == {"a": 4, "b": 3}
    assert contract["allowed_feature_horizon"] == 2160
    assert contract["post_horizon_records"] == 2
    assert contract["excluded_entity_count"] == 2


def test_baseline_prediction_only_allows_time_zero() -> None:
    frame = pd.DataFrame({"entity": ["a", "a", "a"], "time": [0, 10, 20], "value": [1, 2, 3]})
    filtered, contract = filter_before_aggregation(frame, time_column="time", entity_key="entity", cutoff=0)
    assert filtered["time"].tolist() == [0]
    assert contract["post_horizon_records"] == 2


def test_earlier_prediction_cutoff_wins_over_later_outcome() -> None:
    frame = pd.DataFrame({"time": [3, 7, 15], "value": [1, 2, 3]})
    filtered, contract = filter_before_aggregation(frame, time_column="time", prediction_as_of_time=7, target_time=30)
    assert filtered["time"].tolist() == [3, 7]
    assert contract["allowed_feature_horizon"] == 7


def test_no_future_rows_pass_and_unknown_horizon_blocks() -> None:
    report = validate_temporal_availability([1, 2, 3], target_time=3)
    assert report["status"] == "PASS"
    assert report["post_horizon_records"] == 0
    assert report["excluded_future_rows"] == []
    unknown = validate_temporal_availability([1, 2, 3])
    assert unknown["status"] == "UNVERIFIED"
    with pytest.raises(TemporalAvailabilityError, match="TEMPORAL_HORIZON_UNVERIFIED"):
        filter_before_aggregation(pd.DataFrame({"time": [1], "value": [1]}), time_column="time")


def test_incompatible_or_late_cutoff_fails_closed() -> None:
    late = validate_temporal_availability([1, 2], prediction_as_of_time=40, target_time=30)
    assert late["status"] == "FAIL"
    assert "later" in late["reason"]
    mixed = validate_temporal_availability(["day-1"], target_time=30)
    assert mixed["status"] == "UNVERIFIED"


def test_aggregation_before_filter_is_rejected_even_when_future_value_is_extreme() -> None:
    frame = longitudinal_frame()
    contract = validate_temporal_availability(frame["time_h"], entity_ids=frame["entity"], target_time=2160,
                                               time_column="time_h")
    # A future maximum must never influence the aggregate or pass the assertion.
    assert frame.groupby("entity")["value"].max()["a"] == 10_000
    with pytest.raises(TemporalAvailabilityError, match="FUTURE_INFORMATION_LEAKAGE"):
        assert_temporal_aggregation_input(frame, contract)
    filtered, _ = filter_before_aggregation(frame, time_column="time_h", entity_key="entity", target_time=2160)
    first_entity = filtered.loc[filtered["entity"] == "a"].sort_values("time_h")
    assert first_entity["value"].iloc[-1] == 4
    assert first_entity["value"].max() == 4
    assert first_entity["value"].iloc[-1] - first_entity["value"].iloc[0] == 2
    assert (first_entity["value"].iloc[-1] - first_entity["value"].iloc[0]) / (
        first_entity["time_h"].iloc[-1] - first_entity["time_h"].iloc[0]
    ) == pytest.approx(2 / 900)


def test_audit_can_attach_temporal_contract_without_blocking_static_tables(tmp_path: Path) -> None:
    path = tmp_path / "longitudinal.csv"
    longitudinal_frame().to_csv(path, index=False)
    report = audit_file(path, temporal_context={"task": "prediction", "entity_key": "entity",
                                                  "target": "day30", "target_time": 2160,
                                                  "time_column": "time_h"})
    contract = report["sheets"]["<csv>"]["temporal_availability"]
    assert contract["status"] == "PASS"
    assert contract["post_horizon_records"] == 2
    static = audit_file(path)
    assert "temporal_availability" not in static["sheets"]["<csv>"]
    static_contract = validate_temporal_availability(["opaque-a", "opaque-b"], aggregation_required=False)
    assert static_contract["status"] == "PASS"
    assert static_contract["allowed_rows"] == [0, 1]


def test_temporal_provenance_and_invalidated_experiment() -> None:
    contract = validate_temporal_availability([100, 2200], target_time=2160)
    scope = temporal_scope_from_contract(contract)
    assert scope == {"target_horizon": 2160, "feature_cutoff": 2160,
                     "post_horizon_records_excluded": 1, "temporal_gate_status": "PASS"}
    base = {
        "experiment_id": "EXP-TEMP-001", "run_id": "run-test", "created_at": "2026-01-01T00:00:00Z",
        "problem": "fixture", "question": "Q", "status": "OBSERVED", "updated_by_workflow": "run_experiment",
        "planned_protocol": {"aggregation_required": True}, "executed_protocol": {"aggregation_required": True},
        "protocol_changed": False, "change_reason": "", "comparable_to_original_plan": True,
        "input_artifacts": ["input"], "code_artifacts": ["code"], "output_artifacts": ["output"],
        "random_seed": 1, "metrics": {"score": 1}, "evidence_ids": ["EV-1"],
    }
    invalidated = apply_temporal_gate(base, contract, future_rows_entered_aggregation=True)
    assert invalidated["status"] == "INVALIDATED"
    assert invalidated["temporal_scope"]["temporal_gate_status"] == "FAIL"
    assert not validate_experiment_record(invalidated)
    observed = apply_temporal_gate(base, contract)
    assert not validate_experiment_record(observed)
