"""Tests for regression, classification and clustering metrics."""

import math

import pytest

from skill.scripts.metrics import (
    classification_metrics,
    clustering_metrics,
    regression_metrics,
)


def test_regression_metrics_known_values() -> None:
    """Regression metrics should match a hand-checkable example."""
    result = regression_metrics([1, 2, 3], [1, 3, 2])
    assert result["MAE"] == pytest.approx(2 / 3)
    assert result["MSE"] == pytest.approx(2 / 3)
    assert result["RMSE"] == pytest.approx(math.sqrt(2 / 3))
    assert result["R2"] == pytest.approx(0.0)


def test_regression_metrics_zero_and_invalid_inputs() -> None:
    """Zero targets and invalid arrays should have explicit behavior."""
    result = regression_metrics([0, 2], [1, 2])
    assert result["MAPE"] == pytest.approx(0.0)
    with pytest.raises(ValueError):
        regression_metrics([], [])
    with pytest.raises(ValueError):
        regression_metrics([1], [1, 2])
    with pytest.raises(ValueError):
        regression_metrics([1], [1], zero_mape_policy="bad")


def test_classification_metrics_boundary_cases() -> None:
    """Undefined precision and single-class AUC should not crash."""
    result = classification_metrics([0, 1, 1], [0, 0, 0], y_score=[0.1, 0.2, 0.3])
    assert result["Accuracy"] == pytest.approx(1 / 3)
    assert result["Precision"] >= 0
    assert result["ConfusionMatrix"] == [[1, 0], [2, 0]]
    single = classification_metrics([1, 1], [1, 1], y_score=[0.8, 0.9])
    assert math.isnan(single["ROC-AUC"])
    with pytest.raises(ValueError):
        classification_metrics([], [])
    with pytest.raises(ValueError):
        classification_metrics([0], [0], y_score=[0.1, 0.2])


def test_classification_metrics_reports_imbalance_aware_metrics() -> None:
    """Macro and balanced metrics should expose a 98:2 majority predictor."""
    result = classification_metrics([0] * 98 + [1] * 2, [0] * 100, y_score=[0.1] * 100)
    assert result["Accuracy"] == pytest.approx(0.98)
    assert result["Macro F1"] < result["Accuracy"]
    assert result["Balanced Accuracy"] == pytest.approx(0.5)
    assert result["Positive Class Recall"] == pytest.approx(0.0)
    assert result["Specificity"] == pytest.approx(1.0)


def test_classification_metrics_balanced_binary() -> None:
    """Balanced binary predictions should expose all binary diagnostics."""
    result = classification_metrics(
        [0, 0, 1, 1],
        [0, 1, 1, 1],
        y_score=[0.1, 0.6, 0.8, 0.9],
    )
    assert result["Macro F1"] > 0
    assert result["Balanced Accuracy"] == pytest.approx(0.75)
    assert result["Positive Class Recall"] == pytest.approx(1.0)
    assert result["Specificity"] == pytest.approx(0.5)
    assert result["PR-AUC"] is not None


def test_classification_metrics_multiclass_macro_metrics() -> None:
    """Macro metrics should also work for multiclass labels."""
    result = classification_metrics([0, 1, 2, 0, 1, 2], [0, 1, 1, 0, 0, 2])
    assert 0 <= result["Macro Precision"] <= 1
    assert 0 <= result["Macro Recall"] <= 1
    assert 0 <= result["Macro F1"] <= 1
    assert result["Positive Class Recall"] is None


def test_clustering_metrics_and_invalid_labels() -> None:
    """Well-separated clusters should score and invalid partitions should fail."""
    result = clustering_metrics([[0, 0], [0, 1], [5, 5], [5, 6]], [0, 0, 1, 1])
    assert result["Silhouette"] > 0
    assert result["Calinski-Harabasz"] > 0
    assert result["Davies-Bouldin"] >= 0
    with pytest.raises(ValueError):
        clustering_metrics([[0], [1]], [0, 0])
    with pytest.raises(ValueError):
        clustering_metrics([], [])
