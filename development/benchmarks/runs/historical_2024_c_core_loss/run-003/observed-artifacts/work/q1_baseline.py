"""Minimal runnable waveform-classification baseline for 2024 C Q1.

The classifier uses only the 1024 magnetic-flux-density samples per cycle.
Features are intentionally small and interpretable: normalized distribution
statistics, derivative/curvature summaries, and plateau/slope proportions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


LABEL_MAP = {"正弦波": 1, "三角波": 2, "梯形波": 3}
LABEL_NAME = {value: key for key, value in LABEL_MAP.items()}
SEED = 42


def extract_features(values: np.ndarray) -> tuple[np.ndarray, list[str]]:
    """Extract a compact, mostly scale-invariant feature vector per cycle."""
    x = np.asarray(values, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != 1024:
        raise ValueError(f"expected a 2-D array with 1024 samples, got {x.shape}")
    if not np.isfinite(x).all():
        raise ValueError("magnetic-flux-density data contain non-finite values")

    eps = 1e-12
    x_min = x.min(axis=1)
    x_max = x.max(axis=1)
    span = np.maximum(x_max - x_min, eps)
    z = (x - x_min[:, None]) / span[:, None]
    d = np.diff(z, axis=1)
    dd = np.diff(d, axis=1)
    ad = np.abs(d)
    add = np.abs(dd)

    qx = np.quantile(z, [0.05, 0.25, 0.50, 0.75, 0.95], axis=1).T
    qd = np.quantile(ad, [0.05, 0.50, 0.95], axis=1).T
    scale_d = np.maximum(qd[:, 2], eps)

    feature_values = np.column_stack(
        [
            # Distribution / amplitude descriptors.
            x_min,
            x_max,
            span,
            x.mean(axis=1),
            x.std(axis=1),
            np.sqrt(np.mean(x * x, axis=1)),
            z.mean(axis=1),
            z.std(axis=1),
            qx,
            # First- and second-difference shape descriptors.
            ad.mean(axis=1),
            ad.std(axis=1),
            ad.max(axis=1),
            qd,
            add.mean(axis=1),
            add.std(axis=1),
            # Geometry and plateau indicators.
            np.mean(d > 0, axis=1),
            np.mean(d < 0, axis=1),
            np.mean(ad < 0.05 * scale_d[:, None], axis=1),
            np.mean(ad > 0.80 * scale_d[:, None], axis=1),
            np.abs(z[:, 0] - z[:, -1]),
        ]
    )
    names = [
        "b_min",
        "b_max",
        "b_span",
        "b_mean",
        "b_std",
        "b_rms",
        "z_mean",
        "z_std",
        "z_q05",
        "z_q25",
        "z_q50",
        "z_q75",
        "z_q95",
        "abs_d_mean",
        "abs_d_std",
        "abs_d_max",
        "abs_d_q05",
        "abs_d_q50",
        "abs_d_q95",
        "abs_dd_mean",
        "abs_dd_std",
        "positive_slope_fraction",
        "negative_slope_fraction",
        "plateau_fraction",
        "high_slope_fraction",
        "endpoint_gap_normalized",
    ]
    return feature_values, names


def load_training(path: Path) -> tuple[np.ndarray, np.ndarray, list[str], list[int]]:
    """Load all four material sheets and retain material IDs for diagnostics."""
    sheets = pd.read_excel(path, sheet_name=None)
    feature_blocks: list[np.ndarray] = []
    labels: list[int] = []
    materials: list[int] = []
    names: list[str] | None = None
    for material_index, (_sheet_name, frame) in enumerate(sheets.items(), start=1):
        if frame.shape[1] != 1028:
            raise ValueError(f"training sheet {material_index} has {frame.shape[1]} columns")
        waveform = frame.iloc[:, 3].astype(str).str.strip()
        unknown = sorted(set(waveform) - set(LABEL_MAP))
        if unknown:
            raise ValueError(f"unknown waveform labels in material {material_index}: {unknown}")
        features, feature_names = extract_features(frame.iloc[:, 4:].to_numpy())
        if names is None:
            names = feature_names
        elif names != feature_names:
            raise RuntimeError("feature-name mismatch across sheets")
        feature_blocks.append(features)
        labels.extend(waveform.map(LABEL_MAP).astype(int).tolist())
        materials.extend([material_index] * len(frame))
    return np.vstack(feature_blocks), np.asarray(labels), names or [], materials


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--training", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    X, y, feature_names, materials = load_training(args.training)
    X_train, X_valid, y_train, y_valid = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=SEED,
        stratify=y,
    )
    model = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    solver="lbfgs",
                    random_state=SEED,
                ),
            ),
        ]
    )
    model.fit(X_train, y_train)
    valid_pred = model.predict(X_valid)
    labels = [1, 2, 3]
    report = classification_report(
        y_valid,
        valid_pred,
        labels=labels,
        target_names=[LABEL_NAME[i] for i in labels],
        output_dict=True,
        zero_division=0,
    )
    metrics = {
        "status": "OBSERVED",
        "seed": SEED,
        "feature_count": int(X.shape[1]),
        "training_rows": int(len(y)),
        "train_rows": int(len(y_train)),
        "validation_rows": int(len(y_valid)),
        "split": "stratified random holdout, test_size=0.20",
        "accuracy": float(accuracy_score(y_valid, valid_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_valid, valid_pred)),
        "macro_precision": float(report["macro avg"]["precision"]),
        "macro_recall": float(report["macro avg"]["recall"]),
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "per_class": {
            str(label): {
                "waveform": LABEL_NAME[label],
                "precision": float(report[LABEL_NAME[label]]["precision"]),
                "recall": float(report[LABEL_NAME[label]]["recall"]),
                "f1": float(report[LABEL_NAME[label]]["f1-score"]),
                "support": int(report[LABEL_NAME[label]]["support"]),
            }
            for label in labels
        },
    }
    cm = confusion_matrix(y_valid, valid_pred, labels=labels)
    pd.DataFrame(
        cm,
        index=[f"actual_{i}_{LABEL_NAME[i]}" for i in labels],
        columns=[f"predicted_{i}_{LABEL_NAME[i]}" for i in labels],
    ).to_csv(args.output_dir / "validation_confusion_matrix.csv", encoding="utf-8-sig")

    test_frame = pd.read_excel(args.test, sheet_name=0)
    if test_frame.shape[1] != 1028:
        raise ValueError(f"test sheet has {test_frame.shape[1]} columns")
    test_features, _ = extract_features(test_frame.iloc[:, 4:].to_numpy())
    test_pred = model.predict(test_features).astype(int)
    test_output = pd.DataFrame(
        {
            "sample_id": test_frame.iloc[:, 0].astype(int),
            "predicted_label": test_pred,
            "predicted_waveform": [LABEL_NAME[i] for i in test_pred],
        }
    ).sort_values("sample_id")
    test_output.to_csv(args.output_dir / "attachment2_predictions.csv", index=False, encoding="utf-8-sig")

    prediction_counts = {
        LABEL_NAME[label]: int((test_pred == label).sum()) for label in labels
    }
    metadata = {
        "experiment_id": "EXP-Q1-BASELINE-002",
        "run_id": "run-003",
        "training_source": str(args.training),
        "test_source": str(args.test),
        "feature_names": feature_names,
        "material_row_counts": {
            str(material): int(materials.count(material)) for material in sorted(set(materials))
        },
        "validation_metrics": metrics,
        "attachment2_prediction_counts": prediction_counts,
        "notes": [
            "Only B(t) samples were used; temperature, frequency, material, and loss were excluded from Q1 baseline features.",
            "The holdout is preliminary and may be optimistic if near-duplicate cycles cross the split.",
            "Attachment 2 has no ground-truth waveform labels, so its prediction accuracy is not observed.",
        ],
    }
    (args.output_dir / "metrics.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.output_dir / "feature_names.json").write_text(
        json.dumps(feature_names, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"metrics": metrics, "prediction_counts": prediction_counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
