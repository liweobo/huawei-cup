"""Generic contracts added from the run-001 postmortem."""

from __future__ import annotations

from collections import defaultdict
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill.scripts.runtime_provenance import protocols_differ


CANONICAL_AUDIT_KEYS = {
    "total_rows",
    "missing_cells",
    "invalid_rows",
    "duplicate_full_rows",
    "frequency_boundary_rows",
    "anomaly_rows",
    "unresolved_questions",
}


def canonical_audit_summary(raw_report: dict[str, Any]) -> dict[str, Any]:
    """Normalize an audit report to stable, response-facing metrics."""
    totals = raw_report.get("totals", raw_report.get("data_audit", {}))
    return {
        "total_rows": totals.get("rows", totals.get("total_rows")),
        "missing_cells": totals.get("missing_cells"),
        "invalid_rows": totals.get("invalid_rows", totals.get("non_numeric_expected", 0)),
        "duplicate_full_rows": totals.get("duplicate_full_rows", totals.get("duplicate_rows")),
        "frequency_boundary_rows": totals.get("frequency_outside_stated_range", totals.get("frequency_boundary_rows")),
        "anomaly_rows": totals.get("anomaly_rows", "NOT_OBSERVED_AS_SINGLE_CANONICAL_COUNT"),
        "unresolved_questions": list(totals.get("unresolved_questions", [])),
    }


def contradiction_errors(summary: dict[str, Any], claims: list[dict[str, Any]]) -> list[str]:
    """Find contradictory values for canonical metrics in one response."""
    errors: list[str] = []
    values: dict[str, set[str]] = defaultdict(set)
    for claim in claims:
        metric = str(claim.get("metric", "")).strip()
        if metric not in CANONICAL_AUDIT_KEYS:
            continue
        if "value" in claim:
            values[metric].add(repr(claim["value"]))
    for metric, seen in values.items():
        if len(seen) > 1:
            errors.append(f"contradictory canonical metric {metric}: {sorted(seen)}")
        canonical = summary.get(metric)
        if canonical is not None and seen and repr(canonical) not in seen:
            errors.append(f"canonical metric {metric} disagrees with summary: expected {canonical!r}, claims={sorted(seen)}")
    return errors


def validate_protocol_record(record: dict[str, Any]) -> list[str]:
    """Require explicit disclosure when execution differs from the plan."""
    errors: list[str] = []
    planned = record.get("planned_protocol")
    executed = record.get("executed_protocol")
    changed = record.get("protocol_changed")
    if planned is None or executed is None:
        errors.append("planned_protocol and executed_protocol are required")
        return errors
    changed_by_structure = protocols_differ(planned, executed)
    if changed_by_structure and changed is not True:
        errors.append("protocol_changed must be true when planned and executed protocols differ")
    if changed_by_structure and not str(record.get("change_reason", "")).strip():
        errors.append("change_reason is required for protocol drift")
    if not changed_by_structure and changed is True:
        errors.append("protocol_changed cannot be true when protocols are identical")
    if record.get("status") not in {"PLANNED", "RUNNING", "OBSERVED", "FAILED"}:
        errors.append("status must be PLANNED, RUNNING, OBSERVED, or FAILED")
    return errors
