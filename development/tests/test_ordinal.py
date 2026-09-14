"""Generic regression tests for ordered-target modelling contracts."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from skill.scripts.ordinal import (
    CumulativeOrdinalLogistic,
    OrdinalValidationError,
    ordinal_baseline,
    ordinal_cv_metrics,
    ordinal_metrics,
    ordinal_target_contract,
    ordinal_approximation_metadata,
    round_regression_to_ordinal,
    validate_cumulative_probabilities,
    validate_ordinal_probabilities,
)
from skill.scripts.temporal_availability import filter_before_aggregation


LEVELS = ["low", "medium", "high"]


def test_distance_aware_metrics_treat_nearby_error_as_better() -> None:
    y_true = ["low", "medium", "high"]
    nearby = ["medium", "medium", "medium"]
    distant = ["high", "high", "low"]
    near_report = ordinal_metrics(y_true, nearby, ordered_levels=LEVELS)
    distant_report = ordinal_metrics(y_true, distant, ordered_levels=LEVELS)
    assert near_report["MAE"] < distant_report["MAE"]
    assert near_report["Within-One-Level Accuracy"] > 0


def test_median_ordinal_baseline_is_distance_aware() -> None:
    report = ordinal_baseline(
        ["low", "medium", "high", "high"], ordered_levels=LEVELS, strategy="median"
    )
    assert report["baseline"] == "median"
    assert report["prediction"] == "medium"
    assert report["ordinal_approximation"] is False


def test_sparse_minimum_class_count_limits_folds() -> None:
    X = pd.DataFrame({"x": np.arange(9, dtype=float)})
    y = np.array(["low"] * 3 + ["medium"] * 3 + ["high"] * 3, dtype=object)
    estimator = CumulativeOrdinalLogistic(LEVELS)
    with pytest.raises(OrdinalValidationError, match="FOLD_INFEASIBLE"):
        ordinal_cv_metrics(estimator, X, y, ordered_levels=LEVELS, n_splits=5)


def test_explicit_order_source_activates_ordinal_target() -> None:
    report = ordinal_target_contract(
        ["low", "medium", "high"],
        target="severity",
        ordered_levels=LEVELS,
        ordering_source="problem statement section 2",
    )
    assert report["status"] == "PASS"
    assert report["target_type"] == "ORDINAL_CLASSIFICATION"


def test_missing_order_source_fails_closed() -> None:
    report = ordinal_target_contract(
        ["low", "medium", "high"], target="severity", ordered_levels=LEVELS
    )
    assert report["status"] == "UNVERIFIED"


def test_nominal_multiclass_does_not_activate_ordinal() -> None:
    report = ordinal_target_contract(
        ["red", "green", "blue"],
        target="colour",
        declared_type="nominal",
    )
    assert report["status"] == "PASS"
    assert report["target_type"] == "NOMINAL_CLASSIFICATION"


def test_regression_rounding_is_explicitly_approximate() -> None:
    metadata = ordinal_approximation_metadata()
    rounded = round_regression_to_ordinal([0.2, 1.6, 4.0], ordered_levels=LEVELS)
    assert metadata["ordinal_approximation"] is True
    assert rounded.tolist() == ["low", "high", "high"]


def test_probabilities_are_normalized_and_cumulative_is_monotone() -> None:
    probabilities = [[0.2, 0.5, 0.3], [0.7, 0.2, 0.1]]
    report = validate_ordinal_probabilities(probabilities, ordered_levels=LEVELS)
    assert report["status"] == "PASS"
    bad = validate_cumulative_probabilities([[0.2, 0.5], [0.8, 0.3]])
    assert bad["status"] == "FAIL"
    repaired = validate_cumulative_probabilities([[0.2, 0.5], [0.8, 0.3]], repair=True)
    assert repaired["status_after_repair"] == "PASS"


def test_cumulative_candidate_has_valid_probability_rows() -> None:
    X = pd.DataFrame({"x": np.arange(12, dtype=float)})
    y = np.array(["low"] * 4 + ["medium"] * 4 + ["high"] * 4, dtype=object)
    estimator = CumulativeOrdinalLogistic(LEVELS).fit(X, y)
    probabilities = estimator.predict_proba(X)
    report = validate_ordinal_probabilities(probabilities, ordered_levels=LEVELS)
    assert report["status"] == "PASS"
    assert np.allclose(probabilities.sum(axis=1), 1.0)


def test_temporal_gate_remains_before_ordinal_aggregation() -> None:
    frame = pd.DataFrame({"entity": ["a", "a"], "time": [1, 40], "value": [2, 999]})
    filtered, contract = filter_before_aggregation(
        frame, time_column="time", entity_key="entity", target_time=30
    )
    assert filtered["value"].tolist() == [2]
    assert contract["post_horizon_records"] == 1
