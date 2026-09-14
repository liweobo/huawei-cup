"""Targeted ordinal comparison for the frozen 2023E Q3 feature assembly.

This test reads the frozen source module and raw inputs, uses only the first
100 labelled training patients, and writes no run artifacts.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from skill.scripts.ordinal import (
    CumulativeOrdinalLogistic,
    ordinal_baseline,
    ordinal_cv_metrics,
)


PROJECT = Path(__file__).resolve().parents[2]
RAW = PROJECT / "development/benchmarks/problems/2023/E/raw"
BASELINE_SCRIPT = (
    PROJECT
    / "development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/code/clinical_baseline.py"
)
LEVELS = list(range(7))


def _load_frozen_baseline_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("historical_2023e_ordinal_baseline", BASELINE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen 2023E baseline module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _frames(module: ModuleType) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw = module.read_inputs(RAW)
    clinical = module.prepare_clinical(raw["clinical"])
    clinical.attrs["input_dir"] = str(RAW)
    serial_to_time, _ = module.make_lookup(raw["lookup"])
    longitudinal = module.expand_volume_table(raw["volume"], serial_to_time, clinical)
    hemo = module.shape_features(raw["hemo_shape"], "hemo")
    edema = module.shape_features(raw["ed_shape"], "edema")
    baseline, _ = module.assemble_features(clinical, longitudinal, hemo, edema)
    followup = module.make_q3_followup_features(clinical, longitudinal, outcome_horizon_h=2160.0)
    return clinical, baseline, followup


def _compare(frame: pd.DataFrame, module: ModuleType) -> dict[str, object]:
    train = frame.head(100).dropna(subset=["mrs90"]).copy()
    y = train["mrs90"].astype(int).to_numpy()
    X = train.drop(columns=["mrs90"])
    preprocessor, _ = module.make_preprocessor(train, "mrs90")
    nominal = Pipeline(
        [
            ("prep", clone(preprocessor)),
            ("model", LogisticRegression(C=0.2, max_iter=3000, solver="lbfgs")),
        ]
    )
    ordinal = Pipeline(
        [
            ("prep", clone(preprocessor)),
            ("model", CumulativeOrdinalLogistic(LEVELS, C=0.2, max_iter=3000)),
        ]
    )
    nominal_report = ordinal_cv_metrics(
        nominal, X, y, ordered_levels=LEVELS, n_splits=4, n_repeats=2, random_state=42
    )
    ordinal_report = ordinal_cv_metrics(
        ordinal, X, y, ordered_levels=LEVELS, n_splits=4, n_repeats=2, random_state=42
    )
    median = ordinal_baseline(y, ordered_levels=LEVELS, strategy="median")

    def compact(report: dict[str, object]) -> dict[str, object]:
        metrics = report["metrics"]
        assert isinstance(metrics, dict)
        return {
            name: {key: values[key] for key in ("mean", "std")}
            for name, values in metrics.items()
        }

    return {
        "n": int(len(y)),
        "class_counts": {str(level): int(np.sum(y == level)) for level in LEVELS},
        "median_baseline": {
            "prediction": median["prediction"],
            "metrics": {
                key: median["metrics"][key]
                for key in ["MAE", "RMSE", "Quadratic Weighted Kappa", "Accuracy", "Within-One-Level Accuracy"]
            },
        },
        "nominal_multinomial": compact(nominal_report),
        "cumulative_ordinal": compact(ordinal_report),
        "fold_protocol": "4-fold x 2 repeats, random_state=42",
    }


def test_2023e_q3a_and_q3b_compare_nominal_and_ordinal_without_mutating_history() -> None:
    module = _load_frozen_baseline_module()
    clinical, baseline, followup = _frames(module)
    train_ids = set(clinical.head(100)["patient_id"])
    assert len(train_ids) == 100

    # The frozen source contains the known post-90-day records.  The Q3b
    # feature assembly must exclude them before any aggregate is computed.
    raw = module.read_inputs(RAW)
    serial_to_time, _ = module.make_lookup(raw["lookup"])
    longitudinal = module.expand_volume_table(raw["volume"], serial_to_time, clinical)
    post_horizon = longitudinal[longitudinal["onset_to_imaging_h"] > 2160.0]
    assert len(post_horizon) == 9
    assert post_horizon["patient_id"].nunique() == 8
    assert set(followup["followup_horizon_used"].dropna().unique()) == {2160.0}

    q3a = baseline[baseline["patient_id"].isin(train_ids)].copy()
    q3b = followup[followup["patient_id"].isin(train_ids)].copy()
    q3a_result = _compare(q3a, module)
    q3b_result = _compare(q3b, module)
    for result in (q3a_result, q3b_result):
        assert result["n"] == 100
        assert result["fold_protocol"] == "4-fold x 2 repeats, random_state=42"
        assert {"MAE", "RMSE", "Quadratic Weighted Kappa", "Accuracy", "Within-One-Level Accuracy"} <= set(
            result["nominal_multinomial"]
        )
        assert {"MAE", "RMSE", "Quadratic Weighted Kappa", "Accuracy", "Within-One-Level Accuracy"} <= set(
            result["cumulative_ordinal"]
        )
    print("2023E_Q3_ORDINAL_TARGETED=" + json.dumps({"Q3a": q3a_result, "Q3b": q3b_result}, sort_keys=True))
