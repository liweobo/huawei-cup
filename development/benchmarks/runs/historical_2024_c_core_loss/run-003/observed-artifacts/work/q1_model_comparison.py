"""Compare two genuinely different Q1 classifiers under one protocol."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
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
from sklearn.svm import SVC

from q1_baseline import LABEL_NAME, extract_features, load_training


SEED = 42
LABELS = [1, 2, 3]


def score_model(model, X_train, y_train, X_valid, y_valid) -> tuple[dict, np.ndarray, float]:
    started = time.perf_counter()
    model.fit(X_train, y_train)
    fit_seconds = time.perf_counter() - started
    pred = model.predict(X_valid)
    report = classification_report(
        y_valid,
        pred,
        labels=LABELS,
        target_names=[LABEL_NAME[i] for i in LABELS],
        output_dict=True,
        zero_division=0,
    )
    metrics = {
        "accuracy": float(accuracy_score(y_valid, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_valid, pred)),
        "macro_precision": float(report["macro avg"]["precision"]),
        "macro_recall": float(report["macro avg"]["recall"]),
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "fit_seconds": float(fit_seconds),
        "per_class": {
            str(label): {
                "waveform": LABEL_NAME[label],
                "precision": float(report[LABEL_NAME[label]]["precision"]),
                "recall": float(report[LABEL_NAME[label]]["recall"]),
                "f1": float(report[LABEL_NAME[label]]["f1-score"]),
                "support": int(report[LABEL_NAME[label]]["support"]),
            }
            for label in LABELS
        },
    }
    return metrics, pred, fit_seconds


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--training", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    X, y, feature_names, _materials = load_training(args.training)
    X_train, X_valid, y_train, y_valid = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=SEED,
        stratify=y,
    )

    models = {
        # Existing baseline, included to make the comparison interpretable.
        "baseline_logistic": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("classifier", LogisticRegression(max_iter=1000, solver="lbfgs", random_state=SEED)),
            ]
        ),
        # Candidate 1: non-linear axis-aligned tree ensemble.
        "candidate_random_forest": RandomForestClassifier(
            n_estimators=300,
            max_features="sqrt",
            min_samples_leaf=1,
            random_state=SEED,
            n_jobs=-1,
        ),
        # Candidate 2: non-linear distance/kernel decision boundary.
        "candidate_rbf_svm": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("classifier", SVC(C=10.0, kernel="rbf", gamma="scale", cache_size=1024)),
            ]
        ),
    }

    all_metrics: dict[str, dict] = {}
    valid_predictions: dict[str, np.ndarray] = {}
    confusion_matrices: dict[str, list[list[int]]] = {}
    for name, model in models.items():
        metrics, pred, _fit_seconds = score_model(model, X_train, y_train, X_valid, y_valid)
        all_metrics[name] = metrics
        valid_predictions[name] = pred
        confusion_matrices[name] = confusion_matrix(y_valid, pred, labels=LABELS).tolist()

    test_frame = pd.read_excel(args.test, sheet_name=0)
    test_features, _ = extract_features(test_frame.iloc[:, 4:].to_numpy())
    test_predictions: dict[str, np.ndarray] = {}
    pred_frame = pd.DataFrame({"sample_id": test_frame.iloc[:, 0].astype(int)})
    for name, model in models.items():
        # Refit on all labelled training data after validation; attachment 2 remains unlabeled.
        model.fit(X, y)
        pred = model.predict(test_features).astype(int)
        test_predictions[name] = pred
        pred_frame[f"{name}_label"] = pred
        pred_frame[f"{name}_waveform"] = [LABEL_NAME[i] for i in pred]
    pred_frame = pred_frame.sort_values("sample_id")
    pred_frame.to_csv(args.output_dir / "attachment2_candidate_predictions.csv", index=False, encoding="utf-8-sig")

    disagreement_counts = {}
    names = list(test_predictions)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            disagreement_counts[f"{left}_vs_{right}"] = int(
                np.sum(test_predictions[left] != test_predictions[right])
            )

    comparison = {
        "experiment_id": "EXP-Q1-MODEL-COMP-003",
        "run_id": "run-003",
        "status": "OBSERVED",
        "seed": SEED,
        "feature_count": int(X.shape[1]),
        "training_rows": int(len(y)),
        "train_rows": int(len(y_train)),
        "validation_rows": int(len(y_valid)),
        "split": "one shared stratified random holdout, test_size=0.20",
        "models": {
            "baseline_logistic": "StandardScaler + LogisticRegression(lbfgs, max_iter=1000)",
            "candidate_random_forest": "RandomForestClassifier(n_estimators=300, max_features=sqrt, min_samples_leaf=1)",
            "candidate_rbf_svm": "StandardScaler + SVC(kernel=rbf, C=10, gamma=scale)",
        },
        "validation_metrics": all_metrics,
        "validation_confusion_matrices": confusion_matrices,
        "attachment2_prediction_counts": {
            name: {LABEL_NAME[label]: int((pred == label).sum()) for label in LABELS}
            for name, pred in test_predictions.items()
        },
        "attachment2_pairwise_disagreements": disagreement_counts,
        "notes": [
            "All three models use the same 26 B(t)-derived features and shared validation indices.",
            "Attachment 2 labels are unavailable; prediction accuracy and model winner on attachment 2 are NOT OBSERVED.",
            "The single random holdout is a preliminary comparison; grouped/material-held-out validation is NOT RUN.",
        ],
    }
    (args.output_dir / "comparison_metrics.json").write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    pd.DataFrame(
        [
            {
                "model": name,
                "accuracy": values["accuracy"],
                "balanced_accuracy": values["balanced_accuracy"],
                "macro_precision": values["macro_precision"],
                "macro_recall": values["macro_recall"],
                "macro_f1": values["macro_f1"],
                "fit_seconds": values["fit_seconds"],
            }
            for name, values in all_metrics.items()
        ]
    ).to_csv(args.output_dir / "model_comparison_table.csv", index=False, encoding="utf-8-sig")
    for name, matrix in confusion_matrices.items():
        pd.DataFrame(
            matrix,
            index=[f"actual_{i}_{LABEL_NAME[i]}" for i in LABELS],
            columns=[f"predicted_{i}_{LABEL_NAME[i]}" for i in LABELS],
        ).to_csv(args.output_dir / f"{name}_confusion_matrix.csv", encoding="utf-8-sig")
    print(json.dumps(comparison, ensure_ascii=False))


if __name__ == "__main__":
    main()
