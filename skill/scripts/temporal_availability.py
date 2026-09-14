"""Generic availability gates for longitudinal prediction features.

The gate is deliberately independent of any medical outcome or time unit.
Callers must establish the prediction cutoff before building aggregates and
use ``filter_before_aggregation`` to obtain the rows that may be aggregated.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping


class TemporalAvailabilityError(ValueError):
    """Raised when longitudinal rows cannot be safely used for aggregation."""


def _as_sequence(values: Iterable[Any]) -> list[Any]:
    if isinstance(values, (str, bytes, bytearray)):
        raise TypeError("timestamps and entity_ids must be sequences, not strings")
    try:
        return list(values)
    except TypeError as exc:
        raise TypeError("timestamps must be an iterable") from exc


def _key(value: Any) -> tuple[str, Any] | None:
    """Normalize numeric and datetime-like values without guessing units."""
    if value is None:
        return None
    try:
        if bool(value != value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, datetime):
        moment = value
        if moment.tzinfo is None:
            return ("datetime-naive", moment)
        return ("datetime-aware", moment.astimezone(timezone.utc))
    if isinstance(value, date):
        return ("datetime-naive", datetime(value.year, value.month, value.day))
    if hasattr(value, "to_pydatetime"):
        converted = value.to_pydatetime()
        if converted is value:
            return None
        return _key(converted)
    if hasattr(value, "item"):
        try:
            return _key(value.item())
        except (TypeError, ValueError):
            pass
    if isinstance(value, bool):
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        number = Decimal(text)
        return ("number", number) if number.is_finite() else None
    except InvalidOperation:
        pass
    iso = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        return _key(datetime.fromisoformat(iso))
    except ValueError:
        return None


def _display(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            pass
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral() else float(value)
    if hasattr(value, "item"):
        return _display(value.item())
    return value


def _compare(left: Any, right: Any) -> int:
    left_key = _key(left)
    right_key = _key(right)
    if left_key is None or right_key is None or left_key[0] != right_key[0]:
        raise TemporalAvailabilityError("temporal values use incompatible or unknown formats")
    return (left_key[1] > right_key[1]) - (left_key[1] < right_key[1])


def validate_temporal_availability(
    timestamps: Iterable[Any],
    *,
    cutoff: Any = None,
    prediction_as_of_time: Any = None,
    target_time: Any = None,
    entity_ids: Iterable[Any] | None = None,
    task: str = "",
    entity_key: str = "",
    target: str = "",
    time_column: str = "",
    aggregation_required: bool = True,
) -> dict[str, Any]:
    """Build a temporal availability contract and identify usable rows.

    If only ``target_time`` is supplied, it is the maximum allowed horizon.
    Use one documented unit/origin for relative times, or consistent datetime
    values. ``allowed_rows`` contains positional indexes (for ``iloc``).
    Missing or incomparable times return ``UNVERIFIED`` with no usable rows.
    """
    observed = _as_sequence(timestamps)
    entities = _as_sequence(entity_ids) if entity_ids is not None else [None] * len(observed)
    if len(entities) != len(observed):
        raise ValueError("entity_ids must have the same length as timestamps")

    boundaries = [value for value in (cutoff, prediction_as_of_time, target_time) if value is not None]
    contract: dict[str, Any] = {
        "task": task,
        "entity_key": entity_key,
        "target": target,
        "target_time": _display(target_time),
        "prediction_as_of_time": _display(prediction_as_of_time),
        "allowed_feature_horizon": None,
        "time_column": time_column,
        "aggregation_required": bool(aggregation_required),
        "post_horizon_records": 0,
        "allowed_rows": [],
        "excluded_future_rows": [],
        "excluded_entity_count": 0,
        "unknown_time_records": [],
        "max_allowed_time": None,
        "max_observed_time": None,
        "status": "UNVERIFIED",
    }
    if not boundaries:
        if not aggregation_required:
            contract["allowed_rows"] = list(range(len(observed)))
            contract["status"] = "PASS"
            contract["max_observed_time"] = _display(max(observed, key=lambda value: _key(value)[1])) if observed and all(_key(value) is not None for value in observed) else None
        return contract
    try:
        for boundary in boundaries:
            _compare(boundaries[0], boundary)
        if target_time is not None and (prediction_as_of_time is not None or cutoff is not None):
            requested_cutoff = cutoff if cutoff is not None else prediction_as_of_time
            if _compare(requested_cutoff, target_time) > 0:
                contract["status"] = "FAIL"
                contract["reason"] = "feature cutoff is later than target observation time"
                return contract
        horizon = min(boundaries, key=lambda value: _key(value)[1])
        contract["allowed_feature_horizon"] = _display(horizon)
        valid_keys = [_key(value) for value in observed]
        if any(value is None for value in valid_keys):
            contract["unknown_time_records"] = [index for index, value in enumerate(valid_keys) if value is None]
            return contract
        for value in observed:
            _compare(value, horizon)
        contract["max_observed_time"] = _display(max(observed, key=lambda value: _key(value)[1])) if observed else None
        allowed = []
        excluded = []
        for index, value in enumerate(observed):
            if _compare(value, horizon) <= 0:
                allowed.append(index)
            else:
                excluded.append(index)
        contract["allowed_rows"] = allowed
        contract["excluded_future_rows"] = excluded
        contract["post_horizon_records"] = len(excluded)
        contract["excluded_entity_count"] = len({entities[index] for index in excluded}) if entity_ids is not None else 0
        contract["max_allowed_time"] = _display(max((observed[index] for index in allowed), key=lambda value: _key(value)[1])) if allowed else None
        contract["status"] = "PASS"
        return contract
    except (TemporalAvailabilityError, TypeError, ValueError) as exc:
        contract["reason"] = str(exc)
        return contract


def filter_before_aggregation(
    observations: Any,
    *,
    time_column: str,
    cutoff: Any = None,
    prediction_as_of_time: Any = None,
    target_time: Any = None,
    entity_key: str = "",
    target: str = "",
    task: str = "",
) -> tuple[Any, dict[str, Any]]:
    """Filter a table before aggregation, failing closed on unknown horizons."""
    try:
        timestamps = observations[time_column]
    except (KeyError, TypeError, IndexError) as exc:
        raise TemporalAvailabilityError(f"missing time column: {time_column}") from exc
    if not hasattr(observations, "iloc"):
        raise TypeError("observations must be a pandas DataFrame")
    try:
        entities = observations[entity_key] if entity_key else None
    except KeyError as exc:
        raise TemporalAvailabilityError(f"missing entity key: {entity_key}") from exc
    contract = validate_temporal_availability(
        timestamps,
        cutoff=cutoff,
        prediction_as_of_time=prediction_as_of_time,
        target_time=target_time,
        entity_ids=entities,
        task=task,
        entity_key=entity_key,
        target=target,
        time_column=time_column,
        aggregation_required=True,
    )
    if contract["status"] != "PASS":
        raise TemporalAvailabilityError(f"TEMPORAL_HORIZON_{contract['status']}: {contract.get('reason', 'unverified')}")
    rows = contract["allowed_rows"]
    filtered = observations.iloc[rows].copy()
    assert_temporal_aggregation_input(filtered, contract)
    contract["filtering_before_aggregation"] = True
    return filtered, contract


def assert_temporal_aggregation_input(observations: Any, contract: Mapping[str, Any]) -> None:
    """Assert the actual aggregation input, including after joins/concats."""
    if contract.get("status") != "PASS" or contract.get("allowed_feature_horizon") is None:
        raise TemporalAvailabilityError("TEMPORAL_HORIZON_UNVERIFIED: aggregation blocked")
    try:
        checked = validate_temporal_availability(
            observations[contract["time_column"]], cutoff=contract["allowed_feature_horizon"],
        )
    except KeyError as exc:
        raise TemporalAvailabilityError("aggregation input has no availability time") from exc
    if checked["status"] != "PASS":
        raise TemporalAvailabilityError("TEMPORAL_HORIZON_UNVERIFIED: aggregation input time")
    if checked["post_horizon_records"]:
        raise TemporalAvailabilityError("FUTURE_INFORMATION_LEAKAGE: post-cutoff aggregation input")


def temporal_scope_errors(scope: Mapping[str, Any] | None) -> list[str]:
    """Validate the compact temporal provenance attached to an experiment."""
    if scope is None:
        return []
    if not isinstance(scope, Mapping):
        return ["temporal_scope must be a mapping"]
    required = {
        "target_horizon", "feature_cutoff", "post_horizon_records_excluded", "temporal_gate_status",
    }
    errors = [f"temporal_scope missing field: {field}" for field in sorted(required - set(scope))]
    if str(scope.get("temporal_gate_status", "")).upper() not in {"PASS", "FAIL", "UNVERIFIED"}:
        errors.append("temporal_gate_status must be PASS, FAIL, or UNVERIFIED")
    count = scope.get("post_horizon_records_excluded")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        errors.append("post_horizon_records_excluded must be a non-negative integer")
    if scope.get("temporal_gate_status") == "PASS":
        try:
            _compare(scope.get("feature_cutoff"), scope.get("feature_cutoff"))
            if scope.get("target_horizon") is not None and _compare(scope["feature_cutoff"], scope["target_horizon"]) > 0:
                errors.append("feature_cutoff is later than target_horizon")
        except TemporalAvailabilityError:
            errors.append("TEMPORAL_HORIZON_UNVERIFIED: missing or incompatible cutoff")
    return errors


__all__ = [
    "TemporalAvailabilityError",
    "assert_temporal_aggregation_input",
    "filter_before_aggregation",
    "temporal_scope_errors",
    "validate_temporal_availability",
]
