"""Audit CSV and .xlsx files for mathematical modelling workflows.

The report is intentionally advisory: ID, redundancy, imbalance and time
signals are candidates for review, never automatic deletion or transformation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

try:
    from .metrics import class_distribution_summary
    from .ordinal import ordinal_target_contract
    from .group_validation import group_structure_contract
    from .temporal_availability import validate_temporal_availability
except ImportError:  # pragma: no cover - direct CLI execution
    from metrics import class_distribution_summary  # type: ignore
    from ordinal import ordinal_target_contract  # type: ignore
    from group_validation import group_structure_contract  # type: ignore
    from temporal_availability import validate_temporal_availability  # type: ignore


def _json_value(value: Any) -> Any:
    """Convert pandas/numpy values into JSON-compatible values."""
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def _read_tables(path: Path) -> dict[str, pd.DataFrame]:
    """Read a supported data file into named tables.

    ``.xls`` is deliberately unsupported because this project only depends on
    the modern ``openpyxl`` reader for Excel workbooks.
    """
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return {"<csv>": pd.read_csv(path)}
    if suffix == ".xlsx":
        return pd.read_excel(path, sheet_name=None)
    raise ValueError("Unsupported file type; use .csv or .xlsx")


def _field_kind(series: pd.Series) -> str:
    """Classify a field for downstream modelling review."""
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "time"
    non_null = series.dropna()
    if len(non_null) and pd.api.types.is_string_dtype(series):
        parsed = pd.to_datetime(non_null, errors="coerce", format="mixed")
        if parsed.notna().mean() >= 0.8:
            return "time_candidate"
    return "categorical"


def _audit_table(
    frame: pd.DataFrame,
    *,
    near_constant_threshold: float = 0.95,
    correlation_threshold: float = 0.90,
    imbalance_warning_ratio: float = 10.0,
    temporal_context: Mapping[str, Any] | None = None,
    classification_target: str | None = None,
    ordinal_context: Mapping[str, Any] | None = None,
    group_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a serialisable, advisory audit for one table."""
    if not 0 < near_constant_threshold <= 1:
        raise ValueError("near_constant_threshold must be in (0, 1]")
    if not 0 < correlation_threshold <= 1:
        raise ValueError("correlation_threshold must be in (0, 1]")
    if imbalance_warning_ratio <= 1:
        raise ValueError("imbalance_warning_ratio must be greater than 1")

    effective_group_context = group_context
    if effective_group_context is None and temporal_context and temporal_context.get("entity_key"):
        effective_group_context = temporal_context
    if effective_group_context is not None and not isinstance(effective_group_context, Mapping):
        raise TypeError("group_context must be a mapping")
    group_options = effective_group_context or {}
    group_contract = group_structure_contract(
        frame, entity_key=group_options.get("entity_key"),
        validation_unit=group_options.get("validation_unit"),
        prediction_setting=group_options.get("prediction_setting"),
        task=str(group_options.get("task", "")),
        target=str(group_options.get("target") or classification_target or (ordinal_context or {}).get("target", "")),
        aggregated_from_repeated=bool(group_options.get("aggregated_from_repeated", False)),
        aggregation_provenance=group_options.get("aggregation_provenance"),
    )

    common = {
        "possible_id_columns": [],
        "constant_columns": [],
        "near_constant_columns": [],
        "class_distribution": {},
        "imbalance_ratio": {},
        "high_correlation_pairs": [],
        "time_columns": [],
        "is_monotonic": {},
        "duplicate_timestamps": {},
        "group_structure": group_contract,
    }
    if frame.empty:
        report = {
            "shape": [int(frame.shape[0]), int(frame.shape[1])],
            "columns": {},
            "duplicate_rows": 0,
            "correlation": {},
            "risk_prompts": ["empty_data: table has no rows"],
            **common,
        }
        if temporal_context is not None:
            report["temporal_availability"] = build_temporal_availability_contract(frame, temporal_context)
        if classification_target is not None:
            report["classification_target"] = {
                "target": classification_target,
                "status": "UNVERIFIED",
                "reason": "table has no rows",
            }
        if ordinal_context is not None:
            report["ordinal_target"] = {"status": "UNVERIFIED", "reason": "table has no rows"}
        return report

    numeric = frame.select_dtypes(include=["number"])
    columns: dict[str, Any] = {}
    risk_prompts: list[str] = []
    possible_id_columns: list[str] = []
    constant_columns: list[str] = []
    near_constant_columns: list[str] = []
    class_distribution: dict[str, dict[str, int]] = {}
    imbalance_ratio: dict[str, float] = {}
    time_columns: list[str] = []
    is_monotonic: dict[str, bool] = {}
    duplicate_timestamps: dict[str, int] = {}
    for raw_name in frame.columns:
        name = str(raw_name)
        series = frame[raw_name]
        non_null = series.dropna()
        unique_count = int(series.nunique(dropna=True))
        non_null_count = int(non_null.size)
        unique_ratio = unique_count / non_null_count if non_null_count else 0.0
        info: dict[str, Any] = {
            "dtype": str(series.dtype),
            "kind": _field_kind(series),
            "sample_count": int(series.notna().sum()),
            "missing_count": int(series.isna().sum()),
            "missing_rate": float(series.isna().mean()),
            "unique_count": unique_count,
        }
        if pd.api.types.is_numeric_dtype(series):
            desc = series.describe(percentiles=[0.25, 0.5, 0.75])
            info["summary"] = {
                key: _json_value(desc.get(key))
                for key in ["mean", "50%", "std", "min", "25%", "75%", "max"]
            }
            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            if pd.notna(iqr):
                outliers = ((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum()
                info["iqr_outlier_count"] = int(outliers)
                if outliers:
                    risk_prompts.append(f"outlier_review: {name} has {int(outliers)} IQR outliers")
        else:
            top = series.dropna().astype(str).value_counts().head(5).to_dict()
            info["top_values"] = {str(k): int(v) for k, v in top.items()}
        columns[str(name)] = info
        if info["missing_count"]:
            risk_prompts.append(f"missing_review: {name} has missing values")
        if unique_count <= 1:
            constant_columns.append(name)
            risk_prompts.append(f"constant_or_empty: {name}")
        elif non_null_count and float(non_null.astype(str).value_counts(normalize=True).iloc[0]) >= near_constant_threshold:
            near_constant_columns.append(name)
            risk_prompts.append(
                f"near_constant_review: {name} has a dominant value at or above {near_constant_threshold:.0%}"
            )

        is_identifier_name = any(token in name.lower() for token in ("id", "code", "编号", "编码"))
        is_monotonic_number = pd.api.types.is_numeric_dtype(series) and bool(series.dropna().is_monotonic_increasing)
        if unique_ratio >= 0.98 and (is_identifier_name or not pd.api.types.is_float_dtype(series) or is_monotonic_number):
            possible_id_columns.append(name)

        kind = info["kind"]
        if kind == "categorical" and 2 <= unique_count <= 20:
            counts = series.dropna().astype(str).value_counts().to_dict()
            class_distribution[name] = {str(key): int(value) for key, value in counts.items()}
            positive_counts = [count for count in counts.values() if count > 0]
            ratio = max(positive_counts) / min(positive_counts) if positive_counts else float("nan")
            imbalance_ratio[name] = float(ratio)
            if ratio >= imbalance_warning_ratio:
                risk_prompts.append(
                    f"class_imbalance_hint: {name} has max/min class ratio {ratio:.2f}; inspect macro metrics"
                )

        if kind in {"time", "time_candidate"}:
            parsed = pd.to_datetime(series, errors="coerce", format="mixed")
            valid_times = parsed.dropna()
            time_columns.append(name)
            is_monotonic[name] = bool(valid_times.is_monotonic_increasing)
            duplicate_count = int(valid_times.duplicated().sum())
            duplicate_timestamps[name] = duplicate_count
            if not is_monotonic[name]:
                risk_prompts.append(f"time_order_review: {name} is not monotonic")
            if duplicate_count:
                risk_prompts.append(f"duplicate_timestamp_review: {name} has {duplicate_count} repeated timestamps")

    duplicate_rows = int(frame.duplicated().sum())
    if duplicate_rows:
        risk_prompts.append(f"duplicate_review: {duplicate_rows} duplicate rows")
    correlation: dict[str, dict[str, float | None]] = {}
    if numeric.shape[1] >= 2:
        correlation = {
            str(row): {str(col): _json_value(value) for col, value in values.items()}
            for row, values in numeric.corr(numeric_only=True).to_dict().items()
        }
    high_correlation_pairs: list[dict[str, Any]] = []
    if numeric.shape[1] >= 2:
        corr_frame = numeric.corr(numeric_only=True)
        names = list(corr_frame.columns)
        for left_index, left in enumerate(names):
            for right in names[left_index + 1 :]:
                value = corr_frame.loc[left, right]
                if pd.notna(value) and abs(float(value)) >= correlation_threshold:
                    high_correlation_pairs.append(
                        {"columns": [str(left), str(right)], "correlation": float(value)}
                    )
        if high_correlation_pairs:
            risk_prompts.append(
                f"high_correlation_hint: inspect {len(high_correlation_pairs)} potential redundant/multicollinear pairs"
            )
    if time_columns:
        risk_prompts.append("time_order_hint: if used for prediction, preserve temporal causality in train/test splits")
    report = {
        "shape": [int(frame.shape[0]), int(frame.shape[1])],
        "columns": columns,
        "duplicate_rows": duplicate_rows,
        "correlation": correlation,
        "risk_prompts": sorted(set(risk_prompts)),
        "leakage_prompts": [
            "Check whether time/ID/label-after-event fields are available at prediction time.",
            "Check whether preprocessing was fit using only the training portion.",
        ],
        "unit_prompts": [
            "Confirm units across numeric fields and source files before modelling.",
        ],
        "possible_id_columns": sorted(set(possible_id_columns)),
        "constant_columns": sorted(set(constant_columns)),
        "near_constant_columns": sorted(set(near_constant_columns)),
        "class_distribution": class_distribution,
        "imbalance_ratio": imbalance_ratio,
        "high_correlation_pairs": high_correlation_pairs,
        "time_columns": sorted(set(time_columns)),
        "is_monotonic": is_monotonic,
        "duplicate_timestamps": duplicate_timestamps,
    }
    if temporal_context is not None:
        report["temporal_availability"] = build_temporal_availability_contract(frame, temporal_context)
    if classification_target is not None:
        report["classification_target"] = build_classification_target_contract(
            frame, classification_target
        )
    if ordinal_context is not None:
        report["ordinal_target"] = _build_ordinal_target_contract(frame, ordinal_context)
    report["group_structure"] = group_contract
    if group_contract.get("candidate_entity_keys") or group_contract.get("repeated_entities"):
        report["risk_prompts"].append(
            "repeated_entity_review: confirm entity identity and prediction setting; rows may be dependent"
        )
    if group_contract["status"] != "PASS":
        report["risk_prompts"].append("group_scope_unverified: resolve Group Structure Contract before formal validation")
    return report


def _build_ordinal_target_contract(
    frame: pd.DataFrame, context: Mapping[str, Any]
) -> dict[str, Any]:
    target = str(context.get("target", ""))
    if not target or target not in frame.columns:
        return {"target": target, "status": "UNVERIFIED", "reason": "declared ordinal target is not present"}
    return ordinal_target_contract(
        frame[target].dropna().tolist(),
        target=target,
        ordered_levels=context.get("ordered_levels"),
        ordering_source=context.get("ordering_source"),
        declared_type=context.get("declared_type"),
    )


def build_classification_target_contract(
    frame: pd.DataFrame, target: str
) -> dict[str, Any]:
    """Describe a declared binary target without imposing a hard imbalance gate."""
    if target not in frame.columns:
        return {
            "target": target,
            "status": "UNVERIFIED",
            "reason": f"classification target is not present in audited table: {target}",
        }
    observed = frame[target].dropna()
    if observed.empty:
        return {
            "target": target,
            "status": "UNVERIFIED",
            "reason": "classification target has no observed labels",
        }
    labels = np.unique(observed).tolist()
    if len(labels) != 2:
        return {
            "target": target,
            "status": "NOT_BINARY",
            "class_count": len(labels),
            "class_counts": {
                str(label): int((observed == label).sum()) for label in labels
            },
        }
    summary = class_distribution_summary(
        observed.tolist(), positive_label=labels[-1], labels=labels
    )
    majority_accuracy = summary["majority_count"] / summary["n"]
    return {
        "target": target,
        "status": "PASS",
        "class_counts": {
            str(label): int(count) for label, count in summary["class_counts"].items()
        },
        "positive_label": summary["positive_label"],
        "positive_count": int(summary["class_counts"][summary["positive_label"]]),
        "negative_count": int(summary["n"] - summary["class_counts"][summary["positive_label"]]),
        "minority_label": summary["minority_label"],
        "minority_count": int(summary["minority_count"]),
        "minority_ratio": float(summary["minority_ratio"]),
        "imbalance_ratio": float(summary["imbalance_ratio"]),
        "majority_baseline_accuracy": float(majority_accuracy),
        "accuracy_trap_review": bool(majority_accuracy > 0.5),
        "interpretation": (
            "Compare every candidate with the majority baseline and inspect minority/probability metrics; "
            "this diagnostic is not a hard imbalance cutoff."
        ),
    }


def build_temporal_availability_contract(
    frame: pd.DataFrame, context: Mapping[str, Any]
) -> dict[str, Any]:
    """Derive a temporal contract from an audited table and task definition."""
    if not isinstance(context, Mapping):
        raise TypeError("temporal_context must be a mapping")
    time_column = str(context.get("time_column", ""))
    entity_key = str(context.get("entity_key", ""))
    base: dict[str, Any] = {
        "task": str(context.get("task", "")),
        "entity_key": entity_key,
        "target": str(context.get("target", "")),
        "target_time": context.get("target_time"),
        "prediction_as_of_time": context.get("prediction_as_of_time"),
        "time_column": time_column,
        "aggregation_required": bool(context.get("aggregation_required", True)),
    }
    if not time_column or time_column not in frame.columns:
        base.update({
            "allowed_feature_horizon": None, "post_horizon_records": 0,
            "excluded_future_rows": [], "excluded_entity_count": None,
            "unknown_time_records": [], "max_allowed_time": None,
            "max_observed_time": None, "status": "UNVERIFIED",
            "reason": "time_column must be identified before a longitudinal feature is built",
        })
        return base
    entity_ids = frame[entity_key] if entity_key and entity_key in frame.columns else None
    contract = validate_temporal_availability(
        frame[time_column],
        prediction_as_of_time=context.get("prediction_as_of_time"),
        target_time=context.get("target_time"),
        entity_ids=entity_ids,
        task=base["task"], entity_key=entity_key, target=base["target"],
        time_column=time_column, aggregation_required=base["aggregation_required"],
    )
    if entity_key and entity_key not in frame.columns:
        contract["status"] = "UNVERIFIED"
        contract["reason"] = f"entity_key is not present in audited table: {entity_key}"
    return contract


def audit_file(
    path: str | Path,
    *,
    near_constant_threshold: float = 0.95,
    correlation_threshold: float = 0.90,
    imbalance_warning_ratio: float = 10.0,
    temporal_context: dict[str, Any] | None = None,
    classification_target: str | None = None,
    ordinal_context: dict[str, Any] | None = None,
    group_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Audit a CSV or .xlsx file and return a JSON-compatible report."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(file_path)
    tables = _read_tables(file_path)
    return {
        "file": str(file_path),
        "format": file_path.suffix.lower().lstrip("."),
        "audit_parameters": {
            "near_constant_threshold": near_constant_threshold,
            "correlation_threshold": correlation_threshold,
            "imbalance_warning_ratio": imbalance_warning_ratio,
            "classification_target": classification_target,
        },
        "sheets": {
            name: _audit_table(
                frame,
                near_constant_threshold=near_constant_threshold,
                correlation_threshold=correlation_threshold,
                imbalance_warning_ratio=imbalance_warning_ratio,
                temporal_context=temporal_context,
                classification_target=classification_target,
                ordinal_context=ordinal_context,
                group_context=group_context,
            )
            for name, frame in tables.items()
        },
    }


def main() -> None:
    """Run the command-line audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="CSV or .xlsx file")
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation")
    parser.add_argument("--near-constant-threshold", type=float, default=0.95)
    parser.add_argument("--correlation-threshold", type=float, default=0.90)
    parser.add_argument("--imbalance-warning-ratio", type=float, default=10.0)
    parser.add_argument("--temporal-context", type=Path, help="JSON task/time boundary context for longitudinal prediction")
    parser.add_argument("--classification-target", help="declared binary target column for imbalance diagnostics")
    parser.add_argument("--ordinal-context", type=Path, help="JSON target/order/source context for ordinal diagnostics")
    parser.add_argument("--group-context", type=Path, help="JSON entity_key, prediction_setting, validation_unit and optional aggregation provenance")
    args = parser.parse_args()
    temporal_context = None
    if args.temporal_context:
        temporal_context = json.loads(args.temporal_context.read_text(encoding="utf-8"))
    ordinal_context = None
    if args.ordinal_context:
        ordinal_context = json.loads(args.ordinal_context.read_text(encoding="utf-8"))
    group_context = None
    if args.group_context:
        group_context = json.loads(args.group_context.read_text(encoding="utf-8"))
    report = audit_file(
        args.path,
        near_constant_threshold=args.near_constant_threshold,
        correlation_threshold=args.correlation_threshold,
        imbalance_warning_ratio=args.imbalance_warning_ratio,
        temporal_context=temporal_context,
        classification_target=args.classification_target,
        ordinal_context=ordinal_context,
        group_context=group_context,
    )
    print(json.dumps(report, ensure_ascii=False, indent=args.indent))


if __name__ == "__main__":
    main()
