"""Focused 2023E Q1b regression for the generic imbalance protocol.

This test reads the frozen source data and reuses the historical baseline
feature assembly, but writes no artifacts and does not rerun Q2 or Q3.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from skill.scripts.metrics import (
    feature_sample_size_check,
    imbalanced_model_selection_check,
    majority_class_baseline,
    repeated_stratified_cv_metrics,
)


PROJECT = Path(__file__).resolve().parents[2]
RAW = PROJECT / "development/benchmarks/problems/2023/E/raw"
BASELINE_SCRIPT = (
    PROJECT
    / "development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/code/clinical_baseline.py"
)


def _load_frozen_baseline_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("historical_2023e_baseline", BASELINE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen 2023E baseline module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _q1_training_frame(module: ModuleType):
    raw = module.read_inputs(RAW)
    clinical = module.prepare_clinical(raw["clinical"])
    clinical.attrs["input_dir"] = str(RAW)
    serial_to_time, _ = module.make_lookup(raw["lookup"])
    longitudinal = module.expand_volume_table(raw["volume"], serial_to_time, clinical)
    hemo = module.shape_features(raw["hemo_shape"], "hemo")
    edema = module.shape_features(raw["ed_shape"], "edema")
    baseline_features, _ = module.assemble_features(clinical, longitudinal, hemo, edema)
    labels = module.expansion_labels(clinical, longitudinal)
    return baseline_features.merge(
        labels[["patient_id", "expansion"]], on="patient_id", how="left"
    ).head(100)


def test_2023e_q1b_targeted_imbalance_protocol() -> None:
    module = _load_frozen_baseline_module()
    frame = _q1_training_frame(module).dropna(subset=["expansion"]).copy()
    y = frame["expansion"].astype(int).to_numpy()
    X = frame.drop(columns=["expansion"])
    preprocessor, feature_columns = module.make_preprocessor(frame, "expansion")

    assert len(y) == 100
    assert {int(label): int((y == label).sum()) for label in set(y)} == {0: 77, 1: 23}
    dimension = feature_sample_size_check(len(y), len(feature_columns))
    majority = majority_class_baseline(y, positive_label=1)
    assert majority["metrics"]["Accuracy"] == 0.77
    assert majority["metrics"]["Positive Class Recall"] == 0.0
    assert imbalanced_model_selection_check(
        majority["metrics"], majority_baseline=majority
    )["status"] == "REJECT"

    models = {
        "regularized_logistic": Pipeline(
            [
                ("prep", clone(preprocessor)),
                ("model", LogisticRegression(C=0.2, max_iter=3000, solver="liblinear")),
            ]
        ),
        "class_weighted_logistic": Pipeline(
            [
                ("prep", clone(preprocessor)),
                (
                    "model",
                    LogisticRegression(
                        C=0.2,
                        max_iter=3000,
                        solver="liblinear",
                        class_weight="balanced",
                    ),
                ),
            ]
        ),
        "shallow_random_forest": Pipeline(
            [
                ("prep", clone(preprocessor)),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=80,
                        max_depth=4,
                        min_samples_leaf=3,
                        class_weight="balanced_subsample",
                        random_state=42,
                        n_jobs=1,
                    ),
                ),
            ]
        ),
    }
    reports = {
        name: repeated_stratified_cv_metrics(
            model,
            X,
            y,
            n_splits=5,
            n_repeats=2,
            random_state=42,
            positive_label=1,
        )
        for name, model in models.items()
    }

    required = {
        "ROC-AUC",
        "PR-AUC",
        "Brier Score",
        "Positive Class Recall",
        "Positive Class Precision",
        "Positive Class F1",
        "Balanced Accuracy",
        "Specificity",
    }
    for report in reports.values():
        assert required <= set(report["metrics"])
        assert report["fold_count"] == 10
        assert report["class_distribution"]["positive_prevalence"] == 0.23

    # The protocol ranks by an imbalance-aware metric and exposes uncertainty;
    # it deliberately does not require an arbitrary target AUC.
    selected = max(reports, key=lambda name: reports[name]["metrics"]["PR-AUC"]["mean"])
    result = {
        "n": len(y),
        "class_counts": {"0": 77, "1": 23},
        "feature_dimension": dimension,
        "majority_baseline": {
            key: majority["metrics"][key]
            for key in ["Accuracy", "Positive Class Recall", "Balanced Accuracy"]
        },
        "selection_metric": "PR-AUC mean (not Accuracy)",
        "selected_candidate": selected,
        "models": {
            name: {
                metric: {
                    key: report["metrics"][metric][key]
                    for key in ["mean", "std", "median", "min", "max"]
                }
                for metric in required
            }
            for name, report in reports.items()
        },
        "test_labels_used": False,
    }
    print("2023E_Q1_TARGETED=" + json.dumps(result, ensure_ascii=True, sort_keys=True))
