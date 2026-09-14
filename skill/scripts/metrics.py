"""Common regression, classification and clustering metrics for modelling work."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterable
from typing import Any

import numpy as np
from sklearn.base import clone
from sklearn.metrics import brier_score_loss
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    calinski_harabasz_score,
    confusion_matrix,
    davies_bouldin_score,
    f1_score,
    average_precision_score,
    precision_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)
from sklearn.model_selection import RepeatedStratifiedKFold


class ClassificationLeakageError(ValueError):
    """Raised when a classification evaluation protocol can leak labels."""


def _as_1d_array(values: Iterable[Any], *, name: str) -> np.ndarray:
    """Materialise an iterable and require a non-empty one-dimensional array."""
    array = np.asarray(list(values))
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if array.size == 0:
        raise ValueError("at least one observation is required")
    return array


def _ordered_labels(values: np.ndarray, labels: Iterable[Any] | None = None) -> list[Any]:
    """Return an explicit, stable class order without mixed-type sorting."""
    if labels is not None:
        ordered = list(labels)
        if len(set(ordered)) != len(ordered):
            raise ValueError("labels must be unique")
        missing = [value for value in dict.fromkeys(values.tolist()) if value not in ordered]
        if missing:
            raise ValueError(f"labels do not cover observed classes: {missing!r}")
        return ordered
    try:
        return np.unique(values).tolist()
    except TypeError:
        return list(dict.fromkeys(values.tolist()))


def class_distribution_summary(
    y: Iterable[Any],
    *,
    positive_label: Any | None = None,
    labels: Iterable[Any] | None = None,
    imbalance_ratio_threshold: float = 1.5,
) -> dict[str, Any]:
    """Summarise class prevalence and the majority/minority relationship.

    The helper is descriptive only.  It never drops a class or silently
    re-labels observations.  For binary work, pass ``positive_label`` when
    the positive class is not the last class in the declared ``labels`` order.
    """
    if imbalance_ratio_threshold < 1:
        raise ValueError("imbalance_ratio_threshold must be at least 1")
    values = _as_1d_array(y, name="y")
    ordered = _ordered_labels(values, labels)
    counts = Counter(values.tolist())
    class_counts = {label: int(counts[label]) for label in ordered}
    if not class_counts:
        raise ValueError("at least one class is required")
    proportions = {label: count / values.size for label, count in class_counts.items()}
    majority_label = max(ordered, key=lambda label: (class_counts[label], -ordered.index(label)))
    minority_label = min(ordered, key=lambda label: (class_counts[label], ordered.index(label)))
    majority_count = class_counts[majority_label]
    minority_count = class_counts[minority_label]
    ratio = float(majority_count / minority_count) if minority_count else float("inf")
    if positive_label is None and len(ordered) == 2:
        positive_label = ordered[-1]
    positive_prevalence = (
        float(class_counts[positive_label] / values.size)
        if positive_label in class_counts
        else None
    )
    return {
        "n": int(values.size),
        "n_classes": len(ordered),
        "class_counts": class_counts,
        "class_proportions": proportions,
        "majority_label": majority_label,
        "majority_count": majority_count,
        "minority_label": minority_label,
        "minority_count": minority_count,
        "imbalance_ratio": ratio,
        "minority_ratio": float(minority_count / values.size),
        "positive_label": positive_label,
        "positive_prevalence": positive_prevalence,
        "is_imbalanced": bool(ratio >= imbalance_ratio_threshold),
        "imbalance_ratio_threshold": float(imbalance_ratio_threshold),
    }


def _binary_label_order(
    values: np.ndarray,
    *,
    positive_label: Any | None = None,
    labels: Iterable[Any] | None = None,
) -> tuple[Any, Any, list[Any]]:
    """Resolve negative/positive labels for binary helpers."""
    ordered = _ordered_labels(values, labels)
    if len(ordered) != 2:
        raise ValueError("binary classification helpers require exactly two observed classes")
    if positive_label is None:
        positive_label = ordered[-1]
    if positive_label not in ordered:
        raise ValueError("positive_label is not present in y")
    negative_label = next(label for label in ordered if label != positive_label)
    return negative_label, positive_label, [negative_label, positive_label]


def majority_class_predictions(
    y: Iterable[Any], *, majority_label: Any | None = None
) -> np.ndarray:
    """Return an always-majority prediction vector for a labelled sample."""
    values = _as_1d_array(y, name="y")
    if majority_label is None:
        majority_label = class_distribution_summary(values)["majority_label"]
    if majority_label not in set(values.tolist()):
        raise ValueError("majority_label is not present in y")
    return np.full(values.shape, majority_label, dtype=values.dtype)


def majority_class_baseline(
    y_true: Iterable[Any],
    *,
    positive_label: Any | None = None,
    labels: Iterable[Any] | None = None,
) -> dict[str, Any]:
    """Evaluate the mandatory majority-class baseline for a binary task."""
    true = _as_1d_array(y_true, name="y_true")
    negative, positive, binary_labels = _binary_label_order(
        true, positive_label=positive_label, labels=labels
    )
    predictions = majority_class_predictions(true)
    return {
        "baseline": "majority_class",
        "majority_label": class_distribution_summary(true, labels=binary_labels)["majority_label"],
        "predictions": predictions.tolist(),
        "class_distribution": class_distribution_summary(
            true, positive_label=positive, labels=binary_labels
        ),
        "metrics": classification_metrics(
            true, predictions, labels=[negative, positive]
        ),
    }


def majority_baseline_metrics(
    y_true: Iterable[Any],
    *,
    positive_label: Any | None = None,
    labels: Iterable[Any] | None = None,
) -> dict[str, Any]:
    """Return only the metric dictionary for the majority baseline."""
    return majority_class_baseline(
        y_true, positive_label=positive_label, labels=labels
    )["metrics"]


# Short aliases keep workflow code concise while canonical names remain
# descriptive in the reference documentation.
imbalance_summary = class_distribution_summary
majority_baseline = majority_class_baseline


def regression_metrics(
    y_true: Iterable[float],
    y_pred: Iterable[float],
    *,
    zero_mape_policy: str = "omit",
) -> dict[str, float]:
    """Return MAE, MSE, RMSE, MAPE and R2 for paired finite observations."""
    true = np.asarray(list(y_true), dtype=float)
    pred = np.asarray(list(y_pred), dtype=float)
    if true.ndim != 1 or pred.ndim != 1 or true.size != pred.size:
        raise ValueError("y_true and y_pred must be one-dimensional and equally sized")
    if true.size == 0:
        raise ValueError("at least one observation is required")
    if not np.isfinite(true).all() or not np.isfinite(pred).all():
        raise ValueError("inputs must contain only finite numbers")
    errors = pred - true
    denominator = np.abs(true)
    if zero_mape_policy == "omit":
        valid = denominator > 0
        mape = float(np.mean(np.abs(errors[valid]) / denominator[valid]) * 100) if valid.any() else float("nan")
    elif zero_mape_policy == "epsilon":
        mape = float(
            np.mean(np.abs(errors) / np.maximum(denominator, np.finfo(float).eps)) * 100
        )
    else:
        raise ValueError("zero_mape_policy must be 'omit' or 'epsilon'")
    mse = float(np.mean(errors**2))
    ss_total = float(np.sum((true - np.mean(true)) ** 2))
    r2 = float(1 - np.sum(errors**2) / ss_total) if ss_total > 0 else float("nan")
    return {
        "MAE": float(np.mean(np.abs(errors))),
        "MSE": mse,
        "RMSE": float(np.sqrt(mse)),
        "MAPE": mape,
        "R2": r2,
    }


def classification_metrics(
    y_true: Iterable[object],
    y_pred: Iterable[object],
    *,
    y_score: Iterable[float] | None = None,
    labels: Iterable[object] | None = None,
) -> dict[str, Any]:
    """Return common classification metrics with safe boundary-case behavior."""
    true = np.asarray(list(y_true))
    pred = np.asarray(list(y_pred))
    if true.ndim != 1 or pred.ndim != 1 or true.size != pred.size:
        raise ValueError("y_true and y_pred must be one-dimensional and equally sized")
    if true.size == 0:
        raise ValueError("at least one observation is required")
    label_values = (
        list(labels)
        if labels is not None
        else np.unique(np.concatenate([true, pred])).tolist()
    )
    if len(label_values) < 2:
        matrix = [[int(true.size)]] if np.array_equal(true, pred) else confusion_matrix(true, pred).tolist()
    else:
        matrix = confusion_matrix(true, pred, labels=label_values).tolist()
    accuracy = float(accuracy_score(true, pred))
    balanced_accuracy = (
        accuracy if np.unique(true).size < 2 else float(balanced_accuracy_score(true, pred))
    )
    weighted_precision = float(precision_score(true, pred, average="weighted", zero_division=0))
    weighted_recall = float(recall_score(true, pred, average="weighted", zero_division=0))
    weighted_f1 = float(f1_score(true, pred, average="weighted", zero_division=0))
    result: dict[str, Any] = {
        "Accuracy": accuracy,
        "Precision": weighted_precision,
        "Recall": weighted_recall,
        "F1": weighted_f1,
        "Weighted Precision": weighted_precision,
        "Weighted Recall": weighted_recall,
        "Weighted F1": weighted_f1,
        "Macro Precision": float(precision_score(true, pred, average="macro", labels=label_values, zero_division=0)),
        "Macro Recall": float(recall_score(true, pred, average="macro", labels=label_values, zero_division=0)),
        "Macro F1": float(f1_score(true, pred, average="macro", labels=label_values, zero_division=0)),
        "Balanced Accuracy": balanced_accuracy,
        "ConfusionMatrix": matrix,
        "ROC-AUC": None,
        "PR-AUC": None,
        "Brier Score": None,
        "Positive Prevalence": None,
        "Positive Class Precision": None,
        "Positive Class Recall": None,
        "Positive Class F1": None,
        "Specificity": None,
    }
    if y_score is not None:
        scores = np.asarray(list(y_score), dtype=float)
        if scores.ndim != 1 or scores.size != true.size:
            raise ValueError("y_score must be one-dimensional and equally sized")
        unique_true = np.unique(true)
        if unique_true.size < 2:
            result["ROC-AUC"] = float("nan")
            result["PR-AUC"] = float("nan")
        elif unique_true.size == 2:
            positive = label_values[-1]
            binary_true = (true == positive).astype(int)
            result["Positive Prevalence"] = float(binary_true.mean())
            try:
                result["ROC-AUC"] = float(roc_auc_score(binary_true, scores))
            except ValueError:
                result["ROC-AUC"] = float("nan")
            try:
                result["PR-AUC"] = float(average_precision_score(binary_true, scores))
            except ValueError:
                result["PR-AUC"] = float("nan")
            if np.isfinite(scores).all() and np.all((scores >= 0) & (scores <= 1)):
                result["Brier Score"] = float(brier_score_loss(binary_true, scores))
            else:
                # A decision function is useful for ranking, but it is not a
                # probability and must not be reported as a Brier score.
                result["Brier Score"] = float("nan")
        else:
            # A one-dimensional score cannot describe all multiclass classes.
            result["ROC-AUC"] = float("nan")
            result["PR-AUC"] = float("nan")
    if len(label_values) == 2:
        positive = label_values[-1]
        negative = label_values[0]
        result["Positive Prevalence"] = float(np.mean(true == positive))
        result["Positive Class Precision"] = float(
            precision_score(true, pred, pos_label=positive, average="binary", zero_division=0)
        )
        result["Positive Class Recall"] = float(
            recall_score(true, pred, pos_label=positive, average="binary", zero_division=0)
        )
        result["Positive Class F1"] = float(
            f1_score(true, pred, pos_label=positive, average="binary", zero_division=0)
        )
        tn, fp, _, _ = confusion_matrix(true, pred, labels=[negative, positive]).ravel()
        result["Specificity"] = float(tn / (tn + fp)) if tn + fp else float("nan")
    return result


def binary_probability_metrics(
    y_true: Iterable[Any],
    y_probability: Iterable[float],
    *,
    positive_label: Any | None = None,
    labels: Iterable[Any] | None = None,
) -> dict[str, Any]:
    """Evaluate probabilities without choosing a decision threshold."""
    true = _as_1d_array(y_true, name="y_true")
    scores = np.asarray(list(y_probability), dtype=float)
    if scores.ndim != 1 or scores.size != true.size:
        raise ValueError("y_probability must be one-dimensional and equally sized")
    if not np.isfinite(scores).all() or np.any((scores < 0) | (scores > 1)):
        raise ValueError("y_probability must contain finite values in [0, 1]")
    negative, positive, binary_labels = _binary_label_order(
        true, positive_label=positive_label, labels=labels
    )
    binary_true = (true == positive).astype(int)
    result = {
        "n": int(true.size),
        "positive_label": positive,
        "negative_label": negative,
        "positive_prevalence": float(binary_true.mean()),
        "ROC-AUC": float("nan"),
        "PR-AUC": float("nan"),
        "Brier Score": float(brier_score_loss(binary_true, scores)),
    }
    if np.unique(binary_true).size == 2:
        result["ROC-AUC"] = float(roc_auc_score(binary_true, scores))
        result["PR-AUC"] = float(average_precision_score(binary_true, scores))
    return result


def evaluate_binary_threshold(
    y_true: Iterable[Any],
    y_probability: Iterable[float],
    *,
    threshold: float = 0.5,
    positive_label: Any | None = None,
    labels: Iterable[Any] | None = None,
) -> dict[str, Any]:
    """Evaluate a probability model at one explicit decision threshold."""
    if not np.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("threshold must be finite and in [0, 1]")
    true = _as_1d_array(y_true, name="y_true")
    scores = np.asarray(list(y_probability), dtype=float)
    if scores.ndim != 1 or scores.size != true.size:
        raise ValueError("y_probability must be one-dimensional and equally sized")
    if not np.isfinite(scores).all() or np.any((scores < 0) | (scores > 1)):
        raise ValueError("y_probability must contain finite values in [0, 1]")
    negative, positive, binary_labels = _binary_label_order(
        true, positive_label=positive_label, labels=labels
    )
    predicted = np.where(scores >= threshold, positive, negative)
    result = classification_metrics(
        true, predicted, y_score=scores, labels=binary_labels
    )
    result.update(
        {
            "threshold": float(threshold),
            "positive_label": positive,
            "negative_label": negative,
        }
    )
    return result


def validate_threshold_selection_scope(
    selection_scope: str = "validation", *, test_labels: Iterable[Any] | None = None
) -> dict[str, str]:
    """Fail closed when a threshold is selected from test labels or all data."""
    scope = str(selection_scope).strip().lower().replace("-", "_")
    allowed = {"validation", "inner_validation", "cross_validation"}
    if test_labels is not None:
        raise ClassificationLeakageError(
            "THRESHOLD_SELECTION_TEST_LABEL_LEAKAGE: test labels cannot tune a threshold"
        )
    if scope not in allowed:
        raise ClassificationLeakageError(
            "THRESHOLD_SELECTION_TEST_LABEL_LEAKAGE: "
            "select thresholds only inside validation, never on test/all data"
        )
    return {"status": "PASS", "selection_scope": scope}


def select_classification_threshold(
    y_validation: Iterable[Any],
    probability_validation: Iterable[float],
    *,
    thresholds: Iterable[float] | None = None,
    objective: str = "balanced_accuracy",
    positive_label: Any | None = None,
    labels: Iterable[Any] | None = None,
    selection_scope: str = "validation",
    test_labels: Iterable[Any] | None = None,
    min_recall: float | None = None,
    min_precision: float | None = None,
) -> dict[str, Any]:
    """Choose a threshold using validation labels only.

    The returned threshold must be applied to a separate test set without
    looking at its labels.  Constraint failures simply remove a candidate;
    if all candidates fail, the function raises rather than silently relaxing
    the requested operating point.
    """
    validate_threshold_selection_scope(selection_scope, test_labels=test_labels)
    true = _as_1d_array(y_validation, name="y_validation")
    scores = np.asarray(list(probability_validation), dtype=float)
    if scores.ndim != 1 or scores.size != true.size:
        raise ValueError("probability_validation must be one-dimensional and equally sized")
    if not np.isfinite(scores).all() or np.any((scores < 0) | (scores > 1)):
        raise ValueError("probability_validation must contain finite values in [0, 1]")
    if min_recall is not None and not 0 <= min_recall <= 1:
        raise ValueError("min_recall must be in [0, 1]")
    if min_precision is not None and not 0 <= min_precision <= 1:
        raise ValueError("min_precision must be in [0, 1]")
    objective_key = objective.strip().lower().replace(" ", "_").replace("-", "_")
    objective_aliases = {
        "balanced_accuracy": "Balanced Accuracy",
        "balancedaccuracy": "Balanced Accuracy",
        "f1": "Positive Class F1",
        "macro_f1": "Macro F1",
        "positive_recall": "Positive Class Recall",
        "recall": "Positive Class Recall",
        "precision": "Positive Class Precision",
        "specificity": "Specificity",
        "youden_j": "_youden_j",
    }
    if objective_key not in objective_aliases:
        raise ValueError(f"unsupported threshold objective: {objective}")
    negative, positive, binary_labels = _binary_label_order(
        true, positive_label=positive_label, labels=labels
    )
    if thresholds is None:
        candidate_values = np.unique(np.r_[0.0, 0.5, scores, 1.0])
    else:
        candidate_values = np.asarray(list(thresholds), dtype=float)
        if candidate_values.ndim != 1 or candidate_values.size == 0:
            raise ValueError("thresholds must be a non-empty one-dimensional iterable")
    if not np.isfinite(candidate_values).all() or np.any((candidate_values < 0) | (candidate_values > 1)):
        raise ValueError("thresholds must contain finite values in [0, 1]")
    candidates: list[dict[str, Any]] = []
    for candidate in sorted(set(float(value) for value in candidate_values)):
        evaluated = evaluate_binary_threshold(
            true,
            scores,
            threshold=candidate,
            positive_label=positive,
            labels=binary_labels,
        )
        if min_recall is not None and float(evaluated["Positive Class Recall"]) < min_recall:
            continue
        if min_precision is not None and float(evaluated["Positive Class Precision"]) < min_precision:
            continue
        if objective_aliases[objective_key] == "_youden_j":
            score = float(evaluated["Positive Class Recall"] + evaluated["Specificity"] - 1)
        else:
            score = float(evaluated[objective_aliases[objective_key]])
        candidates.append({"threshold": candidate, "objective_value": score, "metrics": evaluated})
    if not candidates:
        raise ValueError("no threshold satisfies the requested validation constraints")
    # Prefer the threshold closest to 0.5 for exact objective ties.  This
    # avoids an arbitrary extreme operating point on tiny validation samples.
    best = max(candidates, key=lambda item: (item["objective_value"], -abs(item["threshold"] - 0.5)))
    return {
        "status": "PASS",
        "selection_scope": str(selection_scope).strip().lower().replace("-", "_"),
        "objective": objective_key,
        "threshold": float(best["threshold"]),
        "objective_value": float(best["objective_value"]),
        "validation_metrics": best["metrics"],
        "candidates_evaluated": len(candidates),
        "positive_label": positive,
        "negative_label": negative,
    }


select_threshold = select_classification_threshold
evaluate_threshold = evaluate_binary_threshold


def validate_resampling_scope(
    placement: str | None = None,
    *,
    resampling_before_split: bool | None = None,
    inside_cv_pipeline: bool | None = None,
    split_before_resampling: bool | None = None,
) -> dict[str, str]:
    """Require resampling to occur after splitting and inside each CV pipeline."""
    if placement is not None:
        normalized = placement.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in {"before_split", "global", "full_data"}:
            resampling_before_split = True
        elif normalized in {"after_split", "split_then_resample"}:
            resampling_before_split = False
        elif normalized in {"inside_cv_pipeline", "cv_pipeline", "pipeline"}:
            resampling_before_split = False
            inside_cv_pipeline = True
        else:
            raise ValueError(f"unknown resampling placement: {placement}")
    if split_before_resampling is not None:
        resampling_before_split = not split_before_resampling
    if resampling_before_split is None:
        raise ValueError("state whether the split precedes resampling")
    if resampling_before_split:
        raise ClassificationLeakageError(
            "RESAMPLING_BEFORE_SPLIT_LEAKAGE: split before SMOTE/resampling"
        )
    if inside_cv_pipeline is not True:
        raise ClassificationLeakageError(
            "RESAMPLING_OUTSIDE_CV_PIPELINE: fit resampling separately inside each CV fold"
        )
    return {"status": "PASS", "resampling_scope": "inside_cv_pipeline"}


assert_resampling_inside_cv = validate_resampling_scope


def validate_preprocessing_scope(
    placement: str | None = None,
    *,
    fitted_before_cv: bool | None = None,
    inside_cv_pipeline: bool | None = None,
    fitted_before_split: bool | None = None,
) -> dict[str, str]:
    """Require preprocessing/selection/PCA to be fitted inside CV folds."""
    if placement is not None:
        normalized = placement.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in {"before_cv", "before_split", "full_data", "global"}:
            fitted_before_cv = True
        elif normalized in {"inside_cv_pipeline", "cv_pipeline", "pipeline"}:
            fitted_before_cv = False
            inside_cv_pipeline = True
        else:
            raise ValueError(f"unknown preprocessing placement: {placement}")
    if fitted_before_split is True:
        fitted_before_cv = True
    if fitted_before_cv is None:
        raise ValueError("state whether preprocessing was fitted before CV")
    if fitted_before_cv:
        raise ClassificationLeakageError(
            "PREPROCESSING_BEFORE_CV_LEAKAGE: fit scaling/selection/PCA/imputation per fold"
        )
    if inside_cv_pipeline is not True:
        raise ClassificationLeakageError(
            "PREPROCESSING_OUTSIDE_CV_PIPELINE: use a pipeline fitted inside each CV fold"
        )
    return {"status": "PASS", "preprocessing_scope": "inside_cv_pipeline"}


assert_preprocessing_inside_cv = validate_preprocessing_scope


def feature_sample_size_check(n_samples: int, n_features: int) -> dict[str, Any]:
    """Expose, without inventing a universal cutoff, dimensionality pressure."""
    if n_samples <= 0 or n_features < 0:
        raise ValueError("n_samples must be positive and n_features must be non-negative")
    ratio = float(n_features / n_samples)
    status = "REVIEW" if n_features >= n_samples else "PASS"
    return {
        "status": status,
        "n_samples": int(n_samples),
        "n_features": int(n_features),
        "features_per_sample": ratio,
        "regularization_or_dimension_control_required": bool(n_features >= n_samples),
    }


def imbalanced_model_selection_check(
    model_metrics: dict[str, Any],
    *,
    majority_baseline: dict[str, Any] | None = None,
    task_ignores_minority: bool = False,
) -> dict[str, Any]:
    """Reject an apparently accurate model that never detects the minority."""
    reasons: list[str] = []
    recall = model_metrics.get("Positive Class Recall")
    if recall is None:
        recall = model_metrics.get("positive_recall")
    accuracy = model_metrics.get("Accuracy", model_metrics.get("accuracy"))
    balanced = model_metrics.get("Balanced Accuracy", model_metrics.get("balanced_accuracy"))
    if not task_ignores_minority and recall is not None and float(recall) <= 0:
        reasons.append("minority_recall_is_zero")
    if majority_baseline is None and not task_ignores_minority:
        reasons.append("majority_baseline_not_compared")
    elif majority_baseline is not None and not task_ignores_minority:
        baseline_metrics = majority_baseline.get("metrics", majority_baseline)
        baseline_balanced = baseline_metrics.get("Balanced Accuracy", baseline_metrics.get("balanced_accuracy"))
        if balanced is not None and baseline_balanced is not None and float(balanced) <= float(baseline_balanced):
            reasons.append("balanced_accuracy_does_not_exceed_majority_baseline")
    if not task_ignores_minority and accuracy is not None and recall is not None and float(accuracy) > 0.8 and float(recall) <= 0:
        reasons.append("high_accuracy_minority_trap")
    return {
        "status": "VALID_FINAL_MODEL" if not reasons else "REJECT",
        "reasons": reasons,
        "accuracy_is_not_primary": True,
        "task_ignores_minority": bool(task_ignores_minority),
    }


def _take_rows(data: Any, indices: np.ndarray) -> Any:
    """Slice pandas or array-like rows without coercing feature dtypes."""
    if hasattr(data, "iloc"):
        return data.iloc[indices]
    return np.asarray(data)[indices]


def _positive_score(estimator: Any, X: Any, positive_label: Any) -> tuple[np.ndarray | None, bool]:
    """Extract a positive-class ranking score and flag actual probabilities."""
    if hasattr(estimator, "predict_proba"):
        probabilities = np.asarray(estimator.predict_proba(X), dtype=float)
        classes = list(getattr(estimator, "classes_", []))
        if probabilities.ndim != 2 or probabilities.shape[1] != len(classes):
            raise ValueError("predict_proba output does not align with estimator classes")
        if positive_label not in classes:
            raise ValueError("positive_label is not present in estimator.classes_")
        return probabilities[:, classes.index(positive_label)], True
    if hasattr(estimator, "decision_function"):
        decision = np.asarray(estimator.decision_function(X), dtype=float)
        if decision.ndim == 2:
            classes = list(getattr(estimator, "classes_", []))
            if positive_label not in classes:
                raise ValueError("positive_label is not present in estimator.classes_")
            decision = decision[:, classes.index(positive_label)]
        if decision.ndim != 1:
            raise ValueError("decision_function must return one score per row")
        return decision, False
    return None, False


def repeated_stratified_cv_metrics(
    estimator: Any,
    X: Any,
    y: Iterable[Any],
    *,
    n_splits: int = 5,
    n_repeats: int = 3,
    random_state: int = 42,
    threshold: float = 0.5,
    positive_label: Any | None = None,
    labels: Iterable[Any] | None = None,
    groups: Iterable[Any] | None = None,
) -> dict[str, Any]:
    """Run repeated stratified CV and summarise fold-level binary metrics.

    ``groups`` is rejected deliberately: grouped or temporal structure needs a
    stronger splitter chosen by the caller rather than silently falling back
    to stratification.
    """
    if groups is not None:
        raise ValueError("group/time structure requires a group-aware or temporal splitter")
    if n_splits < 2 or n_repeats < 1:
        raise ValueError("n_splits must be >= 2 and n_repeats must be >= 1")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be in [0, 1]")
    true = _as_1d_array(y, name="y")
    negative, positive, binary_labels = _binary_label_order(
        true, positive_label=positive_label, labels=labels
    )
    distribution = class_distribution_summary(
        true, positive_label=positive, labels=binary_labels
    )
    if distribution["minority_count"] < n_splits:
        raise ValueError(
            "n_splits cannot exceed the minority-class count; use fewer folds or a stronger design"
        )
    splitter = RepeatedStratifiedKFold(
        n_splits=n_splits, n_repeats=n_repeats, random_state=random_state
    )
    fold_metrics: list[dict[str, Any]] = []
    for fold_index, (train_index, test_index) in enumerate(splitter.split(np.zeros(true.size), true)):
        fitted = clone(estimator)
        fitted.fit(_take_rows(X, train_index), true[train_index])
        held_out = _take_rows(X, test_index)
        score, is_probability = _positive_score(fitted, held_out, positive)
        predicted = (
            np.where(score >= threshold, positive, negative)
            if score is not None and is_probability
            else np.asarray(fitted.predict(held_out))
        )
        evaluated = classification_metrics(
            true[test_index],
            predicted,
            y_score=score,
            labels=binary_labels,
        )
        if score is not None and not is_probability:
            evaluated["Brier Score"] = None
        scalar_metrics = {
            key: value
            for key, value in evaluated.items()
            if isinstance(value, (int, float, np.integer, np.floating))
            and value is not None
            and np.isfinite(float(value))
        }
        fold_metrics.append(
            {
                "fold": int(fold_index % n_splits + 1),
                "repeat": int(fold_index // n_splits + 1),
                "n_train": int(len(train_index)),
                "n_test": int(len(test_index)),
                "metrics": scalar_metrics,
            }
        )
    metric_names = sorted({name for fold in fold_metrics for name in fold["metrics"]})
    summary: dict[str, dict[str, Any]] = {}
    for name in metric_names:
        values = np.asarray([fold["metrics"][name] for fold in fold_metrics if name in fold["metrics"]], dtype=float)
        summary[name] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
            "median": float(np.median(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "range": [float(np.min(values)), float(np.max(values))],
            "n": int(values.size),
        }
    return {
        "status": "PASS",
        "n_splits": int(n_splits),
        "n_repeats": int(n_repeats),
        "fold_count": len(fold_metrics),
        "random_state": int(random_state),
        "threshold": float(threshold),
        "class_distribution": distribution,
        "fold_metrics": fold_metrics,
        "metrics": summary,
        "metric_summary": summary,
        "positive_label": positive,
        "negative_label": negative,
        "probability_note": "Brier score is reported only for estimators with predict_proba.",
    }


repeated_stratified_cv_summary = repeated_stratified_cv_metrics


def clustering_metrics(
    X: Iterable[Iterable[float]], labels: Iterable[object]
) -> dict[str, float]:
    """Return Silhouette, Calinski-Harabasz and Davies-Bouldin scores."""
    data = np.asarray(list(X), dtype=float)
    groups = np.asarray(list(labels))
    if data.ndim != 2 or data.shape[0] == 0 or data.shape[0] != groups.size:
        raise ValueError("X must be a non-empty 2D array aligned with labels")
    unique = np.unique(groups)
    if unique.size < 2 or unique.size >= data.shape[0]:
        raise ValueError("clustering metrics require 2 to n-1 distinct labels")
    if not np.isfinite(data).all():
        raise ValueError("X must contain only finite numbers")
    return {
        "Silhouette": float(silhouette_score(data, groups)),
        "Calinski-Harabasz": float(calinski_harabasz_score(data, groups)),
        "Davies-Bouldin": float(davies_bouldin_score(data, groups)),
    }


def main() -> None:
    """Run deterministic demos for one metric family or all of them."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--demo",
        choices=["regression", "classification", "clustering", "all"],
        help="run one deterministic example",
    )
    args = parser.parse_args()
    if args.demo is None:
        parser.error("use --demo or import a metric function")
    if args.demo in {"regression", "all"}:
        print("regression", regression_metrics([1, 2, 4], [1, 3, 3]))
    if args.demo in {"classification", "all"}:
        print(
            "classification",
            classification_metrics(
                [0, 1, 1, 0], [0, 1, 0, 0], y_score=[0.1, 0.8, 0.4, 0.2]
            ),
        )
    if args.demo in {"clustering", "all"}:
        print(
            "clustering",
            clustering_metrics([[0, 0], [0, 1], [5, 5], [5, 6]], [0, 0, 1, 1]),
        )


if __name__ == "__main__":
    main()
