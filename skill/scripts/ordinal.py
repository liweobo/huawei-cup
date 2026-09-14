"""Ordinal target contracts, metrics and low-capacity validation helpers."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix, mean_absolute_error, mean_squared_error
from sklearn.model_selection import RepeatedStratifiedKFold


class OrdinalValidationError(ValueError):
    """Raised when an ordinal contract or probability protocol is invalid."""


def _values(values: Iterable[Any], name: str) -> np.ndarray:
    result = np.asarray(list(values), dtype=object)
    if result.ndim != 1 or result.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional iterable")
    return result


def _levels(ordered_levels: Sequence[Any]) -> list[Any]:
    levels = list(ordered_levels)
    if len(levels) < 2 or len(set(levels)) != len(levels):
        raise ValueError("ordered_levels must contain at least two unique levels")
    return levels


def ordinal_target_contract(
    y: Iterable[Any],
    *,
    target: str = "target",
    ordered_levels: Sequence[Any] | None = None,
    ordering_source: str | None = None,
    declared_type: str | None = None,
) -> dict[str, Any]:
    """Classify a target only when its ordering is evidenced explicitly.

    Numeric labels are not treated as continuous or ordinal automatically.
    An ordinal result requires both an ordered level list and a source such as
    the problem statement, schema, or user declaration.
    """
    values = _values(y, "y")
    declared = (declared_type or "").strip().lower().replace("-", "_")
    if declared in {"continuous", "regression", "continuous_regression"}:
        return {"target": target, "target_type": "CONTINUOUS_REGRESSION", "status": "PASS"}
    if declared in {"nominal", "nominal_classification", "multiclass"}:
        return {"target": target, "target_type": "NOMINAL_CLASSIFICATION", "status": "PASS"}
    if ordered_levels is None or not ordering_source or not str(ordering_source).strip():
        return {
            "target": target,
            "target_type": "UNKNOWN_CLASSIFICATION",
            "status": "UNVERIFIED",
            "reason": "ordered levels and their source must be supplied; labels alone do not prove order",
            "observed_levels": list(dict.fromkeys(values.tolist())),
        }
    levels = _levels(ordered_levels)
    unknown = [value for value in dict.fromkeys(values.tolist()) if value not in levels]
    if unknown:
        return {
            "target": target,
            "target_type": "ORDINAL_CLASSIFICATION",
            "status": "FAIL",
            "ordered_levels": levels,
            "ordering_source": str(ordering_source),
            "reason": f"observed values are absent from ordered_levels: {unknown!r}",
        }
    counts = {level: int(np.sum(values == level)) for level in levels}
    extreme = {level: count for level, count in counts.items() if level in {levels[0], levels[-1]}}
    return {
        "target": target,
        "target_type": "ORDINAL_CLASSIFICATION",
        "status": "PASS",
        "ordered_levels": levels,
        "ordering_source": str(ordering_source),
        "level_count": len(levels),
        "class_counts": counts,
        "extreme_class_counts": extreme,
        "min_class_count": min(counts.values()),
        "primary_metric": "MAE",
        "secondary_metrics": ["Quadratic Weighted Kappa", "RMSE", "Within-One-Level Accuracy"],
        "model_family_candidates": ["cumulative_ordinal_logistic", "nominal_multiclass_baseline", "ordinal_approximation_regression"],
    }


build_ordinal_target_contract = ordinal_target_contract


def ordinal_metrics(
    y_true: Iterable[Any],
    y_pred: Iterable[Any],
    *,
    ordered_levels: Sequence[Any],
    large_error_threshold: int | None = None,
) -> dict[str, Any]:
    """Return distance-aware metrics for an ordered target."""
    levels = _levels(ordered_levels)
    true = _values(y_true, "y_true")
    pred = _values(y_pred, "y_pred")
    if true.size != pred.size:
        raise ValueError("y_true and y_pred must have equal length")
    mapping = {level: index for index, level in enumerate(levels)}
    unknown = [value for value in np.r_[true, pred].tolist() if value not in mapping]
    if unknown:
        raise ValueError(f"values absent from ordered_levels: {unknown!r}")
    # Keep the public label container flexible, while giving sklearn metrics
    # a homogeneous native dtype for numeric labels loaded as numpy scalars.
    metric_true = np.asarray(true.tolist())
    metric_pred = np.asarray(pred.tolist())
    true_index = np.asarray([mapping[value] for value in true], dtype=float)
    pred_index = np.asarray([mapping[value] for value in pred], dtype=float)
    errors = np.abs(pred_index - true_index)
    threshold = int(2 if large_error_threshold is None else large_error_threshold)
    if threshold < 1:
        raise ValueError("large_error_threshold must be positive")
    return {
        "n": int(true.size),
        "ordered_levels": levels,
        "MAE": float(mean_absolute_error(true_index, pred_index)),
        "RMSE": float(np.sqrt(mean_squared_error(true_index, pred_index))),
        "Quadratic Weighted Kappa": float(cohen_kappa_score(true_index, pred_index, weights="quadratic")),
        "Accuracy": float(accuracy_score(metric_true, metric_pred)),
        "Within-One-Level Accuracy": float(np.mean(errors <= 1)),
        "Large Ordinal Error Rate": float(np.mean(errors >= threshold)),
        "large_error_threshold": threshold,
        "ConfusionMatrix": confusion_matrix(metric_true, metric_pred, labels=np.asarray(levels)).tolist(),
    }


ordinal_classification_metrics = ordinal_metrics


def ordinal_baseline(
    y: Iterable[Any], *, ordered_levels: Sequence[Any], strategy: str = "median"
) -> dict[str, Any]:
    """Evaluate median or most-frequent ordinal prediction baselines."""
    levels = _levels(ordered_levels)
    values = _values(y, "y")
    mapping = {level: index for index, level in enumerate(levels)}
    if any(value not in mapping for value in values):
        raise ValueError("y contains values absent from ordered_levels")
    key = strategy.strip().lower().replace("-", "_").replace(" ", "_")
    if key == "median":
        label = levels[int(np.median([mapping[value] for value in values]))]
    elif key in {"most_frequent", "mode"}:
        counts = {level: int(np.sum(values == level)) for level in levels}
        label = max(levels, key=lambda level: (counts[level], -mapping[level]))
    else:
        raise ValueError("strategy must be 'median' or 'most_frequent'")
    predictions = np.full(values.shape, label, dtype=object)
    return {
        "baseline": key,
        "prediction": label,
        "predictions": predictions.tolist(),
        "ordinal_approximation": False,
        "metrics": ordinal_metrics(values, predictions, ordered_levels=levels),
    }


median_ordinal_baseline = ordinal_baseline


def ordinal_approximation_metadata(*, method: str = "regression_then_clip_round") -> dict[str, Any]:
    """Mark continuous regression plus rounding as an approximation baseline."""
    return {"method": method, "ordinal_approximation": True, "final_output": "clip_then_round_to_ordered_levels"}


def round_regression_to_ordinal(
    predictions: Iterable[float], *, ordered_levels: Sequence[Any]
) -> np.ndarray:
    """Clip and round a continuous approximation onto ordered level indices."""
    levels = _levels(ordered_levels)
    values = np.asarray(list(predictions), dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("predictions must be a finite one-dimensional iterable")
    indices = np.clip(np.rint(values), 0, len(levels) - 1).astype(int)
    return np.asarray([levels[index] for index in indices], dtype=object)


regression_ordinal_baseline = round_regression_to_ordinal


def validate_ordinal_probabilities(
    probabilities: Iterable[Iterable[float]], *, ordered_levels: Sequence[Any], tolerance: float = 1e-8
) -> dict[str, Any]:
    """Check class-probability normalization and non-negativity."""
    levels = _levels(ordered_levels)
    matrix = np.asarray(list(probabilities), dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] != len(levels) or matrix.shape[0] == 0:
        raise ValueError("probabilities must be a non-empty matrix with one column per level")
    sums = matrix.sum(axis=1)
    valid = bool(np.isfinite(matrix).all() and np.all(matrix >= -tolerance) and np.all(np.abs(sums - 1) <= tolerance))
    return {"status": "PASS" if valid else "FAIL", "row_count": int(matrix.shape[0]), "level_count": len(levels), "max_sum_error": float(np.max(np.abs(sums - 1))), "min_probability": float(np.min(matrix))}


def expected_ordinal_score(probabilities: Iterable[Iterable[float]], *, ordered_levels: Sequence[Any]) -> np.ndarray:
    """Compute E[level index] after probability validation."""
    levels = _levels(ordered_levels)
    matrix = np.asarray(list(probabilities), dtype=float)
    report = validate_ordinal_probabilities(matrix, ordered_levels=levels)
    if report["status"] != "PASS":
        raise OrdinalValidationError("ORDINAL_PROBABILITY_INVALID: rows must sum to one")
    return matrix @ np.arange(len(levels), dtype=float)


def validate_cumulative_probabilities(
    cumulative: Iterable[Iterable[float]], *, tolerance: float = 1e-8, repair: bool = False
) -> dict[str, Any]:
    """Check P(Y > level) monotonicity, optionally projecting to a monotone sequence."""
    matrix = np.asarray(list(cumulative), dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] < 1 or matrix.shape[0] == 0:
        raise ValueError("cumulative must be a non-empty 2D matrix")
    if not np.isfinite(matrix).all() or np.any((matrix < -tolerance) | (matrix > 1 + tolerance)):
        return {"status": "FAIL", "reason": "cumulative probabilities must lie in [0, 1]"}
    violations = int(np.sum(np.diff(matrix, axis=1) > tolerance))
    result: dict[str, Any] = {"status": "PASS" if violations == 0 else "FAIL", "violations": violations, "row_count": int(matrix.shape[0]), "threshold_count": int(matrix.shape[1])}
    if repair:
        repaired = np.minimum.accumulate(np.clip(matrix, 0, 1), axis=1)
        result["repaired"] = True
        result["repaired_cumulative"] = repaired.tolist()
        result["status_after_repair"] = "PASS"
    return result


class CumulativeOrdinalLogistic(BaseEstimator, ClassifierMixin):
    """Low-capacity cumulative-threshold classifier with monotone probabilities."""

    def __init__(self, ordered_levels: Sequence[Any], *, C: float = 1.0, class_weight: Any = None, max_iter: int = 1000):
        self.ordered_levels = ordered_levels
        self.C = C
        self.class_weight = class_weight
        self.max_iter = max_iter

    def fit(self, X: Any, y: Iterable[Any]) -> "CumulativeOrdinalLogistic":
        levels = _levels(self.ordered_levels)
        values = _values(y, "y")
        mapping = {level: index for index, level in enumerate(levels)}
        if any(value not in mapping for value in values):
            raise ValueError("y contains values absent from ordered_levels")
        encoded = np.asarray([mapping[value] for value in values])
        self.classes_ = np.asarray(levels, dtype=object)
        self.models_ = []
        for threshold in range(len(levels) - 1):
            target = (encoded > threshold).astype(int)
            model = LogisticRegression(C=self.C, class_weight=self.class_weight, max_iter=self.max_iter, solver="liblinear")
            self.models_.append(model.fit(X, target))
        return self

    def _cumulative(self, X: Any) -> np.ndarray:
        values = []
        for model in self.models_:
            values.append(model.predict_proba(X)[:, 1])
        return np.minimum.accumulate(np.column_stack(values), axis=1)

    def predict_proba(self, X: Any) -> np.ndarray:
        cumulative = self._cumulative(X)
        result = np.column_stack([1 - cumulative[:, 0], np.diff(cumulative, axis=1) * -1, cumulative[:, -1]])
        result = np.clip(result, 0, 1)
        return result / result.sum(axis=1, keepdims=True)

    def predict(self, X: Any) -> np.ndarray:
        probabilities = self.predict_proba(X)
        return self.classes_[np.argmax(probabilities, axis=1)]


def ordinal_cv_metrics(
    estimator: Any,
    X: Any,
    y: Iterable[Any],
    *,
    ordered_levels: Sequence[Any],
    n_splits: int = 5,
    n_repeats: int = 2,
    random_state: int = 42,
    groups: Iterable[Any] | None = None,
) -> dict[str, Any]:
    """Run repeated stratified CV with explicit sparse-class feasibility checks."""
    if groups is not None:
        raise ValueError("group/time structure requires a group-aware or temporal splitter")
    levels = _levels(ordered_levels)
    values = _values(y, "y")
    counts = {level: int(np.sum(values == level)) for level in levels}
    missing = [level for level, count in counts.items() if count == 0]
    if missing:
        raise ValueError(f"ordered_levels have no observed samples: {missing!r}")
    if n_splits < 2 or n_repeats < 1:
        raise ValueError("n_splits must be >= 2 and n_repeats must be >= 1")
    if n_splits > min(counts.values()):
        raise OrdinalValidationError("ORDINAL_CV_FOLD_INFEASIBLE: n_splits exceeds minimum class count")
    # ``_values`` keeps object dtype so heterogeneous labels remain stable,
    # but sklearn's splitter rejects an object array of numpy scalar labels as
    # an ``unknown`` target.  Rebuild a homogeneous view for splitting only.
    split_values = np.asarray(values.tolist())
    splitter = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=random_state)
    folds: list[dict[str, Any]] = []
    for index, (train_idx, test_idx) in enumerate(splitter.split(np.zeros(values.size), split_values)):
        test_counts = {level: int(np.sum(values[test_idx] == level)) for level in levels}
        if any(count == 0 for count in test_counts.values()):
            raise OrdinalValidationError("ORDINAL_CV_CLASS_COVERAGE_FAIL: a validation fold misses a level")
        fitted = clone(estimator).fit(
            X.iloc[train_idx] if hasattr(X, "iloc") else np.asarray(X)[train_idx],
            split_values[train_idx],
        )
        heldout = X.iloc[test_idx] if hasattr(X, "iloc") else np.asarray(X)[test_idx]
        prediction = fitted.predict(heldout)
        folds.append({"fold": int(index % n_splits + 1), "repeat": int(index // n_splits + 1), "train_class_counts": {str(level): int(np.sum(values[train_idx] == level)) for level in levels}, "test_class_counts": {str(level): count for level, count in test_counts.items()}, "metrics": ordinal_metrics(split_values[test_idx], prediction, ordered_levels=levels)})
    names = ["MAE", "RMSE", "Quadratic Weighted Kappa", "Accuracy", "Within-One-Level Accuracy", "Large Ordinal Error Rate"]
    summary = {}
    for name in names:
        vals = np.asarray([fold["metrics"][name] for fold in folds], dtype=float)
        summary[name] = {"mean": float(vals.mean()), "std": float(vals.std(ddof=1)), "median": float(np.median(vals)), "min": float(vals.min()), "max": float(vals.max()), "range": [float(vals.min()), float(vals.max())], "n": int(vals.size)}
    return {"status": "PASS", "ordered_levels": levels, "class_counts": counts, "min_class_count": min(counts.values()), "n_splits": n_splits, "n_repeats": n_repeats, "fold_count": len(folds), "folds": folds, "metrics": summary, "metric_summary": summary}


repeated_ordinal_cv_metrics = ordinal_cv_metrics
