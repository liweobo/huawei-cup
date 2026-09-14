"""Generic regressions for small-sample imbalanced binary classification."""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from skill.scripts.metrics import (
    ClassificationLeakageError,
    binary_probability_metrics,
    class_distribution_summary,
    evaluate_binary_threshold,
    feature_sample_size_check,
    imbalanced_model_selection_check,
    majority_class_baseline,
    repeated_stratified_cv_metrics,
    select_classification_threshold,
    validate_preprocessing_scope,
    validate_resampling_scope,
)


def test_majority_accuracy_trap_is_rejected() -> None:
    y = [0] * 80 + [1] * 20
    baseline = majority_class_baseline(y, positive_label=1)
    metrics = baseline["metrics"]
    assert metrics["Accuracy"] == pytest.approx(0.8)
    assert metrics["Positive Class Recall"] == pytest.approx(0.0)
    assert metrics["Balanced Accuracy"] == pytest.approx(0.5)
    decision = imbalanced_model_selection_check(metrics, majority_baseline=baseline)
    assert decision["status"] == "REJECT"
    assert "minority_recall_is_zero" in decision["reasons"]
    assert imbalanced_model_selection_check(
        metrics, task_ignores_minority=True
    )["status"] == "VALID_FINAL_MODEL"


def test_lower_accuracy_candidate_can_detect_minority() -> None:
    y = np.array([0] * 80 + [1] * 20)
    prediction = np.array([0] * 65 + [1] * 15 + [1] * 13 + [0] * 7)
    score = np.where(prediction == 1, 0.7, 0.2)
    metrics = evaluate_binary_threshold(y, score, positive_label=1)
    baseline = majority_class_baseline(y, positive_label=1)
    assert metrics["Accuracy"] < baseline["metrics"]["Accuracy"]
    assert metrics["Positive Class Recall"] == pytest.approx(0.65)
    assert metrics["Balanced Accuracy"] > baseline["metrics"]["Balanced Accuracy"]
    assert imbalanced_model_selection_check(metrics, majority_baseline=baseline)["status"] == "VALID_FINAL_MODEL"


def test_constant_probability_pr_auc_matches_positive_prevalence() -> None:
    y = [0] * 80 + [1] * 20
    metrics = binary_probability_metrics(y, [0.2] * 100, positive_label=1)
    assert metrics["positive_prevalence"] == pytest.approx(0.2)
    assert metrics["PR-AUC"] == pytest.approx(metrics["positive_prevalence"])
    assert metrics["Brier Score"] == pytest.approx(0.16)


def test_lower_threshold_exposes_recall_precision_tradeoff() -> None:
    y = [0, 0, 0, 0, 1, 1, 1, 1]
    probabilities = [0.05, 0.15, 0.35, 0.45, 0.25, 0.40, 0.55, 0.80]
    at_half = evaluate_binary_threshold(y, probabilities, threshold=0.5, positive_label=1)
    at_point_three = evaluate_binary_threshold(y, probabilities, threshold=0.3, positive_label=1)
    assert at_point_three["Positive Class Recall"] > at_half["Positive Class Recall"]
    assert at_point_three["Positive Class Precision"] < at_half["Positive Class Precision"]
    selected = select_classification_threshold(
        y,
        probabilities,
        thresholds=[0.3, 0.5],
        objective="positive_recall",
        min_precision=0.5,
        positive_label=1,
    )
    assert selected["selection_scope"] == "validation"
    assert selected["threshold"] == pytest.approx(0.3)

    # The threshold constraint applies to the positive class, rather than the
    # support-weighted precision that can hide a weak minority operating point.
    with pytest.raises(ValueError, match="no threshold"):
        select_classification_threshold(
            y,
            probabilities,
            thresholds=[0.3],
            objective="positive_recall",
            min_precision=0.7,
            positive_label=1,
        )


def test_threshold_selection_with_test_labels_fails_closed() -> None:
    with pytest.raises(ClassificationLeakageError, match="TEST_LABEL_LEAKAGE"):
        select_classification_threshold(
            [0, 1], [0.2, 0.8], test_labels=[0, 1], positive_label=1
        )
    with pytest.raises(ClassificationLeakageError, match="TEST_LABEL_LEAKAGE"):
        select_classification_threshold(
            [0, 1], [0.2, 0.8], selection_scope="test", positive_label=1
        )


def test_resampling_must_follow_split_and_live_inside_cv_pipeline() -> None:
    with pytest.raises(ClassificationLeakageError, match="RESAMPLING_BEFORE_SPLIT"):
        validate_resampling_scope("before_split")
    with pytest.raises(ClassificationLeakageError, match="OUTSIDE_CV_PIPELINE"):
        validate_resampling_scope(resampling_before_split=False, inside_cv_pipeline=False)
    assert validate_resampling_scope("inside_cv_pipeline")["status"] == "PASS"


def test_feature_selection_and_other_preprocessing_must_be_inside_cv() -> None:
    with pytest.raises(ClassificationLeakageError, match="PREPROCESSING_BEFORE_CV"):
        validate_preprocessing_scope("full_data")
    assert validate_preprocessing_scope("inside_cv_pipeline")["status"] == "PASS"
    assert feature_sample_size_check(20, 30)["status"] == "REVIEW"
    assert feature_sample_size_check(100, 12)["status"] == "PASS"


def test_nearly_balanced_task_is_not_blocked_and_repeated_cv_is_summarised() -> None:
    X, y = make_classification(
        n_samples=100,
        n_features=6,
        n_informative=4,
        n_redundant=0,
        weights=[0.55, 0.45],
        random_state=8,
    )
    distribution = class_distribution_summary(y, positive_label=1)
    assert distribution["is_imbalanced"] is False
    model = Pipeline(
        [("scale", StandardScaler()), ("model", LogisticRegression(max_iter=1000))]
    )
    result = repeated_stratified_cv_metrics(
        model, X, y, n_splits=5, n_repeats=2, positive_label=1
    )
    assert result["status"] == "PASS"
    assert result["fold_count"] == 10
    for metric in [
        "ROC-AUC",
        "PR-AUC",
        "Brier Score",
        "Positive Class Recall",
        "Positive Class Precision",
        "Positive Class F1",
        "Balanced Accuracy",
        "Specificity",
    ]:
        assert {"mean", "std", "median", "min", "max", "range"} <= set(result["metrics"][metric])


def test_repeated_stratification_yields_to_group_or_time_structure() -> None:
    model = LogisticRegression()
    with pytest.raises(ValueError, match="group-aware or temporal"):
        repeated_stratified_cv_metrics(
            model,
            np.arange(20).reshape(10, 2),
            [0, 1] * 5,
            n_splits=2,
            groups=["a"] * 5 + ["b"] * 5,
        )
