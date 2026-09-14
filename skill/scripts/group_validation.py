"""Entity-aware split contracts, hard leakage gates, and fold provenance.

These helpers do not choose an outcome metric or replace temporal availability.
Supply raw features (or audited aggregates) and an unfitted sklearn pipeline.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from numbers import Integral
import re
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone, is_classifier
from sklearn.model_selection import GroupKFold, KFold, StratifiedKFold

try:
    from sklearn.model_selection import StratifiedGroupKFold
except ImportError:  # pragma: no cover - old sklearn installations
    StratifiedGroupKFold = None


class GroupValidationError(ValueError):
    """An unsafe or infeasible validation protocol; never a warning-only gate."""


SCOPE_UNITS = {
    "SAME_ENTITY_RECORD": "ROW",
    "NEW_ENTITY": "ENTITY",
    "SAME_ENTITY_FUTURE": "TIME",
    "NEW_ENTITY_FUTURE": "ENTITY_TIME",
    "INDEPENDENT_ROWS": "ROW",
}


def _values(values: Iterable[Any], name: str, *, allow_empty: bool = False) -> np.ndarray:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{name} must be row values, not a string")
    array = np.asarray(list(values), dtype=object)
    if array.ndim != 1 or (not allow_empty and not len(array)):
        raise ValueError(f"{name} must be a non-empty one-dimensional iterable")
    return array


def _missing(value: Any) -> bool:
    return bool(pd.isna(value)) or (isinstance(value, str) and not value.strip())


def _ids(values: Iterable[Any], name: str) -> np.ndarray:
    array = _values(values, name)
    if any(_missing(value) for value in array):
        raise GroupValidationError(f"GROUP_KEY_MISSING: {name} contains unknown IDs")
    try:
        set(array.tolist())
    except TypeError as exc:
        raise GroupValidationError(f"{name} must contain scalar, hashable IDs") from exc
    return array


def _sorted_ids(values: Iterable[Any]) -> list[Any]:
    ordered = sorted(set(values), key=lambda value: (type(value).__name__, str(value)))
    return [value.item() if isinstance(value, np.generic) else value for value in ordered]


def _scope(prediction_setting: str | None, validation_unit: str | None,
           *, repeated: bool, entity_known: bool = True) -> dict[str, Any]:
    setting = str(prediction_setting or "").strip().upper()
    unit = str(validation_unit or "").strip().upper()
    if unit and unit not in set(SCOPE_UNITS.values()):
        raise ValueError("validation_unit must be ROW, ENTITY, TIME, or ENTITY_TIME")
    if setting and setting not in SCOPE_UNITS:
        raise ValueError(f"prediction_setting must be one of {sorted(SCOPE_UNITS)}")
    # A non-row unit explicitly answers the scope question. Repeated data plus
    # ROW is ambiguous until the same-entity prediction setting is declared.
    if not setting:
        setting = {"ENTITY": "NEW_ENTITY", "TIME": "SAME_ENTITY_FUTURE",
                   "ENTITY_TIME": "NEW_ENTITY_FUTURE"}.get(unit, "")
        if not setting and not repeated and not entity_known:
            setting = "INDEPENDENT_ROWS"
    expected = SCOPE_UNITS.get(setting)
    reason = ""
    status = "PASS"
    if not expected:
        status, reason = "UNVERIFIED", "declare the prediction setting before validation"
    elif unit and unit != expected:
        status, reason = "FAIL", "validation_unit conflicts with prediction_setting"
    elif repeated and setting == "INDEPENDENT_ROWS":
        status, reason = "FAIL", "PSEUDOREPLICATION: repeated rows are not independent entities"
    return {
        "prediction_setting": setting or "UNVERIFIED",
        "validation_unit": unit or expected or "UNVERIFIED",
        "group_independence_required": setting in {"NEW_ENTITY", "NEW_ENTITY_FUTURE"},
        "temporal_gate_required": setting in {"SAME_ENTITY_FUTURE", "NEW_ENTITY_FUTURE"},
        "status": status, "reason": reason,
    }


def _candidate_entity_keys(frame: Any) -> list[str]:
    """Use identifier syntax, not domain-specific names or ID substrings."""
    candidates = []
    for raw_name in frame.columns:
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(raw_name)).lower()
        identifier = bool(re.search(r"(^|[_\s-])(id|key|code|identifier)$", name))
        identifier |= name in {"entity", "subject", "group"}
        identifier |= name.endswith(("编号", "编码", "标识"))
        observed = frame[raw_name].dropna()
        if identifier and observed.duplicated().any():
            candidates.append(str(raw_name))
    return candidates


def _structure(values: Iterable[Any]) -> dict[str, Any]:
    array = _values(values, "entity_ids", allow_empty=True)
    missing = sum(_missing(value) for value in array)
    counts = Counter(value for value in array if not _missing(value))
    sizes = list(counts.values())
    return {
        "n_entities": len(counts), "n_rows": len(array),
        "min_rows_per_entity": min(sizes) if sizes else None,
        "median_rows_per_entity": float(np.median(sizes)) if sizes else None,
        "max_rows_per_entity": max(sizes) if sizes else None,
        "repeated_entities": sum(size > 1 for size in sizes),
        "missing_entity_rows": missing,
        "effective_independent_units": len(counts),
        "pseudoreplication_risk": any(size > 1 for size in sizes),
    }


def validate_aggregation_provenance(provenance: Mapping[str, Any] | None) -> dict[str, Any]:
    """One row per entity does not erase the source table's leakage risks."""
    if not isinstance(provenance, Mapping):
        return {"status": "UNVERIFIED", "reason": "aggregation provenance is required"}
    temporal = provenance.get("temporal_gate_status")
    if provenance.get("within_entity_only") is False or temporal == "FAIL":
        raise GroupValidationError("AGGREGATION_LEAKAGE: cross-entity or future input")
    if provenance.get("learned_preprocessing_scope") == "ALL_DATA":
        raise GroupValidationError("UNSUPERVISED_PREPROCESSING_LEAKAGE: global aggregate preprocessing")
    verified = (
        provenance.get("within_entity_only") is True
        and temporal in {"PASS", "NOT_APPLICABLE"}
        and provenance.get("learned_preprocessing_scope") in {"NONE", "TRAIN_FOLD"}
        and (temporal != "NOT_APPLICABLE" or bool(provenance.get("temporal_rationale")))
    )
    return {**dict(provenance), "status": "PASS" if verified else "UNVERIFIED"}


def group_structure_contract(
    data: Any, *, entity_key: str | None = None, validation_unit: str | None = None,
    prediction_setting: str | None = None, task: str = "", target: str = "",
    aggregated_from_repeated: bool = False,
    aggregation_provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Audit repeated identifiers and preserve statistics before confirmation.

    Automatic candidates are advisory; confirm their semantics with entity_key.
    Repeated observations never acquire ROW validation by default.
    """
    frame = data if hasattr(data, "columns") else None
    key = str(entity_key or "").strip()
    candidates = [name for name in _candidate_entity_keys(frame) if name != target] if frame is not None else []
    base = {
        "entity_key": key or None, "candidate_entity_keys": candidates,
        "candidate_structures": {name: _structure(frame[name]) for name in candidates},
        "n_entities": None, "n_rows": len(frame) if frame is not None else None,
        "min_rows_per_entity": None, "median_rows_per_entity": None,
        "max_rows_per_entity": None, "repeated_entities": 0,
        "task": task, "target": target, "aggregated_from_repeated": aggregated_from_repeated,
    }
    unconfirmed = not key and bool(candidates)
    if unconfirmed and len(candidates) == 1:
        key = candidates[0]
        base["entity_key"] = key
    base["entity_key_source"] = "NAME_CANDIDATE" if unconfirmed else "DECLARED" if key else "NONE_DETECTED"
    if frame is not None and (not key or key not in frame.columns):
        scope = _scope(prediction_setting, validation_unit, repeated=bool(candidates), entity_known=bool(key))
        base.update(scope)
        base["unit_of_analysis"] = "UNVERIFIED" if key or candidates else "ROW"
        if key or candidates or scope["prediction_setting"] != "INDEPENDENT_ROWS":
            base.update(status="UNVERIFIED", reason="identify and confirm entity_key")
        if frame.empty:
            base.update(status="UNVERIFIED", reason="table has no rows")
        return base
    if not key:
        raise ValueError("entity_key is required for an iterable of entity IDs")
    stats = _structure(frame[key] if frame is not None else data)
    base.update(stats)
    base.update(_scope(prediction_setting, validation_unit, repeated=bool(stats["repeated_entities"])))
    base["unit_of_analysis"] = "ENTITY"
    if unconfirmed or stats["missing_entity_rows"] or not stats["n_rows"]:
        base.update(status="UNVERIFIED", reason="confirm entity_key and resolve missing/empty IDs")
    if aggregated_from_repeated:
        provenance = validate_aggregation_provenance(aggregation_provenance)
        base["aggregation_provenance"] = provenance
        if stats["repeated_entities"]:
            base.update(status="FAIL", reason="aggregated entity table still has duplicate entities")
        elif provenance["status"] != "PASS":
            base.update(status="UNVERIFIED", reason="verify aggregation before row/entity equivalence")
    return base


build_group_structure_contract = group_structure_contract


def group_overlap(train_groups: Iterable[Any], validation_groups: Iterable[Any]) -> dict[str, Any]:
    train = set(_ids(train_groups, "train_groups").tolist())
    valid = set(_ids(validation_groups, "validation_groups").tolist())
    overlap = _sorted_ids(train & valid)
    return {"status": "FAIL" if overlap else "PASS", "overlap_count": len(overlap),
            "overlap_entities": overlap, "train_group_count": len(train),
            "validation_group_count": len(valid)}


def assert_group_independence(train_groups: Iterable[Any], validation_groups: Iterable[Any]) -> dict[str, Any]:
    report = group_overlap(train_groups, validation_groups)
    if report["overlap_count"]:
        raise GroupValidationError(f"GROUP_LEAKAGE: {report['overlap_count']} shared entities; INVALIDATED")
    return report


validate_group_split = assert_group_independence


def validate_group_cv_feasibility(
    groups: Iterable[Any], *, y: Iterable[Any] | None = None,
    n_splits: int = 5, stratified: bool = False,
) -> dict[str, Any]:
    """Preflight group sizes and target-level support before constructing CV."""
    values = _ids(groups, "groups")
    stats = _structure(values)
    if not isinstance(n_splits, Integral) or isinstance(n_splits, bool) or n_splits < 2:
        raise GroupValidationError("GROUP_CV_FOLD_INFEASIBLE: n_splits must be an integer >= 2")
    if n_splits > stats["n_entities"]:
        raise GroupValidationError(
            f"GROUP_CV_FOLD_INFEASIBLE: requested {n_splits} folds but only {stats['n_entities']} groups"
        )
    if stratified and y is None:
        raise ValueError("y is required for grouped stratification")
    class_groups = {}
    class_rows = {}
    if y is not None:
        labels = _ids(y, "target levels")
        if len(labels) != len(values):
            raise ValueError("y and groups must have equal length")
        for label in dict.fromkeys(labels.tolist()):
            class_groups[str(label)] = _sorted_ids(values[labels == label].tolist())
            class_rows[str(label)] = int(np.sum(labels == label))
        if len(class_groups) < 2 or any(len(ids) < 2 for ids in class_groups.values()):
            raise GroupValidationError(
                "GROUP_CLASS_COVERAGE_INFEASIBLE: each target level needs >= 2 groups for all training folds"
            )
    counts = {level: len(ids) for level, ids in class_groups.items()}
    feasible = all(count >= n_splits for count in counts.values())
    return {
        "status": "PASS", "n_groups": stats["n_entities"], "n_rows": len(values),
        "n_splits": int(n_splits),
        **{name: stats[name] for name in ("min_rows_per_entity", "median_rows_per_entity", "max_rows_per_entity")},
        "class_group_counts": counts, "class_groups": class_groups, "class_row_counts": class_rows,
        "stratification_feasible": feasible,
        "stratification_status": ("STRATIFIED_GROUP_FEASIBLE" if feasible else "FALLBACK_GROUP_ONLY")
        if stratified else "NOT_REQUESTED",
        "coverage_note": "group-level counts are necessary, not sufficient; inspect actual folds",
    }


def _indices(values: Sequence[int], n_rows: int) -> np.ndarray:
    array = np.asarray(values)
    if array.ndim != 1 or not array.size or array.dtype.kind not in "iu":
        raise GroupValidationError("INVALID_SPLIT_INDEX: non-empty integer row indexes required")
    if (array < 0).any() or (array >= n_rows).any() or len(np.unique(array)) != len(array):
        raise GroupValidationError("INVALID_SPLIT_INDEX: duplicate or out-of-range row index")
    return array.astype(int)


def audit_group_cv_splits(
    splits: Iterable[tuple[Sequence[int], Sequence[int]]], groups: Iterable[Any], *,
    group_key: str = "groups", split_strategy: str = "EXPLICIT_SPLITS",
    prediction_setting: str | None = None, validation_unit: str | None = None,
) -> dict[str, Any]:
    """Inspect all folds, including failed diagnostics, without accepting scores.

    TIME / ENTITY_TIME reports certify only the group gate. A separate temporal
    gate and a time-aware split are still mandatory for formal validation.
    """
    values = _ids(groups, "groups")
    scope = _scope(prediction_setting, validation_unit or (None if prediction_setting else "ENTITY"),
                   repeated=len(set(values)) < len(values))
    folds, violations = [], []
    if scope["status"] != "PASS":
        violations.append("VALIDATION_SCOPE_UNVERIFIED" if scope["status"] == "UNVERIFIED" else "VALIDATION_SCOPE_MISMATCH")
    for number, (train_ids, valid_ids) in enumerate(splits, 1):
        train, valid = _indices(train_ids, len(values)), _indices(valid_ids, len(values))
        overlap = group_overlap(values[train], values[valid])
        if np.intersect1d(train, valid).size:
            violations.append("SPLIT_OVERLAP")
        if scope["group_independence_required"] and overlap["overlap_count"]:
            violations.append("GROUP_LEAKAGE")
        if scope["prediction_setting"] in {"SAME_ENTITY_RECORD", "SAME_ENTITY_FUTURE"}:
            if set(values[valid]) - set(values[train]):
                violations.append("SAME_ENTITY_SCOPE_MISMATCH")
        folds.append({
            "fold": number, "train_rows": len(train), "validation_rows": len(valid),
            "train_row_ids": train.tolist(), "validation_row_ids": valid.tolist(),
            "train_groups": overlap["train_group_count"], "validation_groups": overlap["validation_group_count"],
            "train_group_ids": _sorted_ids(values[train]), "validation_group_ids": _sorted_ids(values[valid]),
            "overlap_count": overlap["overlap_count"], "overlap_entities": overlap["overlap_entities"],
        })
    if not folds:
        raise GroupValidationError("EMPTY_VALIDATION: at least one non-empty fold is required")
    status = "FAIL" if violations else "PASS"
    return {
        **scope, "status": status, "group_gate_status": status,
        "validation_result_status": "INVALIDATED" if violations else "UNVERIFIED" if scope["temporal_gate_required"] else "VALIDATED",
        "violations": sorted(set(violations)), "groups_used": True, "group_key": group_key,
        "n_entities": len(set(values)), "n_rows": len(values),
        "split_strategy": split_strategy, "n_splits": len(folds), "fold_count": len(folds),
        "overlap_count": sum(fold["overlap_count"] for fold in folds), "folds": folds,
    }


def validate_group_cv_splits(
    splits: Iterable[tuple[Sequence[int], Sequence[int]]], groups: Iterable[Any], **kwargs: Any,
) -> dict[str, Any]:
    report = audit_group_cv_splits(splits, groups, **kwargs)
    if report["status"] != "PASS":
        raise GroupValidationError(f"{', '.join(report['violations'])}: validation INVALIDATED")
    return report


def _make_splits(
    X: Any, groups: Iterable[Any], *, y: Iterable[Any] | None, n_splits: int,
    stratified: bool, random_state: int, validation_unit: str | None,
    prediction_setting: str | None, target_type: str,
) -> tuple[list[tuple[np.ndarray, np.ndarray]], dict[str, Any]]:
    values = _ids(groups, "groups")
    if len(X) != len(values):
        raise ValueError("X and groups must have equal length")
    scope = _scope(prediction_setting, validation_unit or (None if prediction_setting else "ENTITY"),
                   repeated=len(set(values)) < len(values), entity_known=False)
    if scope["status"] != "PASS":
        raise GroupValidationError(f"VALIDATION_SCOPE_UNVERIFIED: {scope['reason']}")
    if scope["temporal_gate_required"]:
        raise GroupValidationError("TEMPORAL_SPLITTER_REQUIRED: supply time-aware splits and check both gates")
    if target_type not in {"regression", "binary", "multiclass", "ordinal"}:
        raise ValueError("target_type must be regression, binary, multiclass, or ordinal")
    labels = _values(y, "y") if y is not None else None
    if labels is not None and len(labels) != len(values):
        raise ValueError("X, y, and groups must have equal length")
    classification = stratified or target_type != "regression"
    if classification and labels is None:
        raise ValueError("classification requires y")
    units = values if scope["validation_unit"] == "ENTITY" else np.arange(len(values))
    feasibility = validate_group_cv_feasibility(units, y=labels if classification else None,
                                                n_splits=n_splits, stratified=stratified)
    native_y = np.asarray(labels.tolist()) if labels is not None else None
    if scope["validation_unit"] == "ROW":
        if stratified and not feasibility["stratification_feasible"]:
            raise GroupValidationError("CLASS_CV_FOLD_INFEASIBLE: fewer rows per level than n_splits")
        splitter = StratifiedKFold(n_splits, shuffle=True, random_state=random_state) if stratified else KFold(n_splits, shuffle=True, random_state=random_state)
        split_iter = splitter.split(np.zeros(len(values)), native_y)
    else:
        if stratified and feasibility["stratification_feasible"] and StratifiedGroupKFold is not None:
            splitter = StratifiedGroupKFold(n_splits, shuffle=True, random_state=random_state)
        else:
            splitter = GroupKFold(n_splits)
            if stratified:
                feasibility["stratification_status"] = "FALLBACK_GROUP_ONLY"
        codes, _ = pd.factorize(values, sort=False)
        split_iter = splitter.split(np.zeros(len(values)), native_y, codes)
    splits = list(split_iter)
    report = validate_group_cv_splits(splits, values, prediction_setting=scope["prediction_setting"],
                                      validation_unit=scope["validation_unit"], split_strategy=type(splitter).__name__)
    report["feasibility"] = feasibility
    if classification:
        for fold, (train, valid) in zip(report["folds"], splits):
            levels = list(dict.fromkeys(labels.tolist()))
            fold["train_level_counts"] = {str(level): int(np.sum(labels[train] == level)) for level in levels}
            fold["validation_level_counts"] = {str(level): int(np.sum(labels[valid] == level)) for level in levels}
            if not all(fold["train_level_counts"].values()):
                raise GroupValidationError("GROUP_CLASS_COVERAGE_INFEASIBLE: a training fold lacks a target level")
            fold["validation_level_coverage"] = "COMPLETE" if all(fold["validation_level_counts"].values()) else "PARTIAL"
    return splits, report


def group_cv_splits(
    X: Any, groups: Iterable[Any], *, y: Iterable[Any] | None = None, n_splits: int = 5,
    stratified: bool = False, random_state: int = 42, validation_unit: str | None = None,
    prediction_setting: str | None = None, target_type: str = "regression",
) -> list[tuple[np.ndarray, np.ndarray]]:
    return _make_splits(X, groups, y=y, n_splits=n_splits, stratified=stratified,
                       random_state=random_state, validation_unit=validation_unit,
                       prediction_setting=prediction_setting, target_type=target_type)[0]


make_group_cv_splits = group_cv_splits


def group_cv_evaluate(
    estimator: Any, X: Any, y: Iterable[Any], groups: Iterable[Any], *,
    scorer: Callable[[Any, Any], float], n_splits: int = 5, stratified: bool = False,
    random_state: int = 42, validation_unit: str | None = None,
    prediction_setting: str | None = None, target_type: str | None = None, group_key: str = "groups",
) -> dict[str, Any]:
    """Clone the complete pipeline in each fold; reuse existing task metrics.

    Transformations performed before this call still require fit-row provenance;
    a precomputed PCA/clustering matrix cannot establish its own safety.
    """
    labels = np.asarray(list(y))
    values = _ids(groups, "groups")
    target_type = target_type or ("multiclass" if is_classifier(estimator) else "regression")
    splits, report = _make_splits(X, values, y=labels, n_splits=n_splits, stratified=stratified,
                                random_state=random_state, validation_unit=validation_unit,
                                prediction_setting=prediction_setting, target_type=target_type)
    report["group_key"] = group_key
    scores = []
    for fold, (train, valid) in zip(report["folds"], splits):
        fitted = clone(estimator)
        x_train = X.iloc[train] if hasattr(X, "iloc") else np.asarray(X)[train]
        x_valid = X.iloc[valid] if hasattr(X, "iloc") else np.asarray(X)[valid]
        fitted.fit(x_train, labels[train])
        score = float(scorer(labels[valid], fitted.predict(x_valid)))
        if not np.isfinite(score):
            raise GroupValidationError("UNDEFINED_FOLD_METRIC: inspect target coverage; do not silently omit this fold")
        scores.append(score)
        fold.update(score=score, pipeline_fit_row_ids=train.tolist(), pipeline_fit_scope="TRAIN_FOLD")
    return {
        "status": "PASS", "error_scope": "VALIDATION_ERROR", "eligible_for_model_selection": True,
        "n_splits": len(splits), "fold_count": len(splits), "scores": scores,
        "mean_score": float(np.mean(scores)), "std_score": float(np.std(scores, ddof=1)),
        "folds": report["folds"], "group_validation": report,
        "validation_unit": report["validation_unit"], "split_strategy": report["split_strategy"],
    }


group_cross_validate = group_cv_evaluate


def validate_unsupervised_scope(
    *, operation: str = "unsupervised preprocessing", fitted_inside_fold: bool | None = None,
    fit_row_ids: Iterable[Any] | None = None, train_row_ids: Iterable[Any] | None = None,
    validation_row_ids: Iterable[Any] | None = None,
) -> dict[str, Any]:
    """Check actual fit rows for scaling, PCA, clustering, or subgroup rules.

    A Boolean assertion alone is UNVERIFIED; record the rows used by fit().
    Independent fixed rules require a source, not a learned all-data fit.
    """
    if fitted_inside_fold is False:
        raise GroupValidationError(f"UNSUPERVISED_PREPROCESSING_LEAKAGE: {operation}; INVALIDATED")
    if fit_row_ids is None or train_row_ids is None or validation_row_ids is None:
        return {"status": "UNVERIFIED", "operation": operation, "reason": "actual fit/train/validation row IDs required"}
    fit = set(_ids(fit_row_ids, "fit_row_ids"))
    train = set(_ids(train_row_ids, "train_row_ids"))
    valid = set(_ids(validation_row_ids, "validation_row_ids"))
    if fit - train or fit & valid or train & valid:
        raise GroupValidationError(f"UNSUPERVISED_PREPROCESSING_LEAKAGE: {operation} fit uses non-training rows; INVALIDATED")
    return {"status": "PASS", "operation": operation, "fitted_inside_fold": True,
            "fit_row_ids": _sorted_ids(fit), "train_row_ids": _sorted_ids(train),
            "validation_row_ids": _sorted_ids(valid), "validation_fit_overlap_count": 0}


def validate_bootstrap_scope(bootstrap_unit: str, *, repeated_entities: bool) -> dict[str, Any]:
    unit = str(bootstrap_unit).strip().upper()
    if unit not in {"ROW", "ENTITY"}:
        raise ValueError("bootstrap_unit must be ROW or ENTITY")
    if repeated_entities and unit == "ROW":
        raise GroupValidationError("ROW_BOOTSTRAP_DEPENDENCE: cannot claim independent uncertainty from correlated rows")
    return {"status": "PASS", "bootstrap_unit": unit, "repeated_entities": bool(repeated_entities),
            "independent_uncertainty_estimate": True,
            "assumption": "resampling units are independent; retain all rows of each sampled entity"}


def error_scope_report(*, fit_residual_count: int | None = None,
                       validation_error_count: int | None = None) -> dict[str, Any]:
    if fit_residual_count is None and validation_error_count is None:
        raise ValueError("provide at least one error scope count")
    for count in (fit_residual_count, validation_error_count):
        if count is not None and (not isinstance(count, Integral) or isinstance(count, bool) or count < 0):
            raise ValueError("error counts must be non-negative integers")
    return {
        "status": "PASS", "fit_residual": {"scope": "FIT_RESIDUAL", "count": fit_residual_count},
        "validation_error": {"scope": "VALIDATION_ERROR", "count": validation_error_count},
        "interpretation": "observed - fitted is in-sample; only held-out predictions measure validation error",
    }


def group_scope_errors(scope: Mapping[str, Any], contract: Mapping[str, Any]) -> list[str]:
    """Recheck saved entity IDs; an authored overlap_count=0 is not evidence."""
    if not isinstance(scope, Mapping) or not isinstance(contract, Mapping):
        return ["group_scope and group_structure must be mappings"]
    required = {"groups_used", "group_key", "split_strategy", "n_splits", "folds", "n_entities", "n_rows",
                "prediction_setting", "validation_unit", "overlap_count", "group_gate_status"}
    errors = [f"group_scope missing field: {name}" for name in sorted(required - scope.keys())]
    if scope.get("group_key") != contract.get("entity_key"):
        errors.append("group_scope group_key must match the Group Structure Contract")
    if scope.get("validation_unit") != contract.get("validation_unit") or scope.get("prediction_setting") != contract.get("prediction_setting"):
        errors.append("group_scope must match the declared validation scope")
    for name in ("n_rows", "n_entities"):
        if scope.get(name) != contract.get(name):
            errors.append(f"group_scope {name} disagrees with the audited entities; do not substitute row IDs")
    try:
        expected = _scope(contract.get("prediction_setting"), contract.get("validation_unit"),
                          repeated=bool(contract.get("repeated_entities")))
    except ValueError as exc:
        return errors + [str(exc)]
    if contract.get("status") == "PASS" and expected["status"] != "PASS":
        errors.append("Group Structure Contract cannot PASS without a valid prediction setting")
    independence_required = expected["group_independence_required"]
    folds = scope.get("folds")
    if not isinstance(folds, list) or not folds or scope.get("n_splits") != len(folds):
        return errors + ["group_scope requires actual folds matching n_splits"]
    overlap_total = 0
    for fold in folds:
        try:
            checked = group_overlap(fold["train_group_ids"], fold["validation_group_ids"])
        except (KeyError, TypeError, ValueError):
            errors.append("group_scope requires non-missing train/validation entity IDs for every fold")
            continue
        overlap_total += checked["overlap_count"]
        if fold.get("overlap_count") != checked["overlap_count"]:
            errors.append("GROUP_LEAKAGE: recorded overlap_count disagrees with actual entity IDs")
        if scope.get("group_gate_status") == "PASS" and independence_required and checked["overlap_count"]:
            errors.append("GROUP_LEAKAGE: an overlapping entity split cannot PASS")
        try:
            train_rows = _indices(fold["train_row_ids"], contract["n_rows"])
            validation_rows = _indices(fold["validation_row_ids"], contract["n_rows"])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"group_scope requires actual fold row IDs: {exc}")
            continue
        if np.intersect1d(train_rows, validation_rows).size:
            errors.append("SPLIT_OVERLAP: recorded train and validation row IDs overlap")
        for operation in fold.get("preprocessing", []):
            try:
                result = validate_unsupervised_scope(operation=operation.get("operation"),
                    fit_row_ids=operation.get("fit_row_ids"), train_row_ids=train_rows,
                    validation_row_ids=validation_rows)
                if result["status"] != "PASS":
                    errors.append("UNSUPERVISED_SCOPE_UNVERIFIED")
            except (TypeError, ValueError) as exc:
                if scope.get("group_gate_status") != "FAIL":
                    errors.append(str(exc))
    if scope.get("overlap_count") != overlap_total:
        errors.append("group_scope total overlap_count is inconsistent")
    if scope.get("groups_used") is not True or not scope.get("split_strategy"):
        errors.append("group_scope must identify the groups and actual split strategy")
    if scope.get("group_gate_status") not in {"PASS", "FAIL", "UNVERIFIED"}:
        errors.append("group_gate_status must be PASS, FAIL, or UNVERIFIED")
    return errors


def review_group_validation(
    contract: Mapping[str, Any], report: Mapping[str, Any] | None, *,
    claimed_independent_n: int | None = None, claimed_generalization: bool = False,
    error_scope: str | None = None,
) -> list[dict[str, Any]]:
    """Structured reviewer findings; prose review also inspects source code."""
    findings = []
    recorded_errors = list(report.get("violations", [])) + group_scope_errors(report, contract) if report is not None else []
    if contract.get("group_independence_required"):
        if report is None:
            findings.append({"priority": "P0", "code": "GROUP_LEAKAGE", "status": "UNVERIFIED",
                             "message": "new-entity validation needs actual group split evidence"})
        elif report.get("overlap_count", 0) or "GROUP_LEAKAGE" in " ".join(recorded_errors):
            findings.append({"priority": "P0", "code": "GROUP_LEAKAGE", "status": "INVALIDATED",
                             "message": "training and validation share entities"})
    if "UNSUPERVISED_PREPROCESSING_LEAKAGE" in " ".join(recorded_errors):
        findings.append({"priority": "P0", "code": "UNSUPERVISED_PREPROCESSING_LEAKAGE", "status": "INVALIDATED",
                         "message": "a learned preprocessing step used held-out rows"})
    if contract.get("repeated_entities") and claimed_independent_n is not None and claimed_independent_n > contract["n_entities"]:
        findings.append({"priority": "P1", "code": "PSEUDOREPLICATION", "status": "DEPENDENCE ISSUE",
                         "message": f"{contract['n_rows']} correlated observations are not that many independent samples; report {contract['n_entities']} entities"})
    if claimed_generalization and error_scope == "FIT_RESIDUAL":
        findings.append({"priority": "P1", "code": "FIT_RESIDUAL_AS_VALIDATION",
                         "message": "in-sample residuals do not establish out-of-entity generalization"})
    return findings
