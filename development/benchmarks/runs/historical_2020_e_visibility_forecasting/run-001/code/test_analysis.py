from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


MODULE_PATH = Path(__file__).with_name("run_analysis.py")
SPEC = importlib.util.spec_from_file_location("visibility_analysis", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_synthetic_guards_fail_closed():
    result = MODULE.synthetic_guards()
    assert result["status"] == "PASS"
    assert result["tests"]["future_target_as_feature"]["blocked"] is True
    assert result["tests"]["realized_future_weather_as_exogenous_feature"]["blocked"] is True
    assert result["tests"]["rolling_window_includes_post_origin"]["blocked"] is True
    assert result["tests"]["random_shuffle_for_time_forecast"]["blocked"] is True
    assert result["tests"]["recursive_h2_uses_observed_h1_target"]["blocked"] is True
    assert result["tests"]["scaler_fit_on_full_series"]["blocked"] is True
    assert result["tests"]["time_reversal_claims_same_forecast_protocol"]["blocked"] is True
    assert result["tests"]["relative_proxy_as_mor_150m"]["blocked"] is True
    assert result["tests"]["current_and_lagged_features_only"]["blocked"] is False


def test_sequential_interval_uses_only_prior_errors():
    rows = []
    for index in range(12):
        rows.append(
            {
                "origin": pd.Timestamp("2020-01-01") + pd.Timedelta(minutes=index),
                "horizon_minutes": 5,
                "method": "persistence",
                "prediction": 10.0,
                "actual": 10.0 + index,
            }
        )
    MODULE.sequential_interval(rows, "persistence", "horizon_minutes", min_history=10)
    assert "interval_radius" not in rows[9]
    assert rows[10]["interval_radius"] == 9.0


def test_regression_metric_identity():
    metrics = MODULE.regression_metrics([1, 2, 3], [1, 2, 3])
    assert metrics["mae"] == 0.0
    assert metrics["rmse"] == 0.0
