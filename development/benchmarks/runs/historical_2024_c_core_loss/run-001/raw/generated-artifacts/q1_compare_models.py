"""Compare two genuinely different Q1 classifiers under the same protocol."""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


BASE = Path(r"C:\Users\aaa\Desktop\test\outputs\q1_baseline")
OUT = Path(r"C:\Users\aaa\Desktop\test\outputs\q1_model_comparison")
FEATURE_NAMES = [
    "wave_std",
    "wave_rms",
    "extreme_ratio",
    "slope_cv",
    "slope_q90_q50",
    "flat_slope_ratio",
    "second_diff_ratio",
    "slope_max_mean_ratio",
]
LABEL_NAMES = {1: "正弦波", 2: "三角波", 3: "梯形波"}


def read_csv(path: Path, label: bool):
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(row)
    X = np.asarray([[float(row[name]) for name in FEATURE_NAMES] for row in rows], dtype=float)
    y = np.asarray([int(row["label_id"]) for row in rows], dtype=int) if label else None
    materials = np.asarray([row["material"] for row in rows], dtype=object)
    sample_ids = np.asarray([int(row["sample_id"]) for row in rows], dtype=int) if not label else None
    return X, y, materials, sample_ids


def make_models():
    return {
        "rbf_svm": Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "svc",
                    SVC(C=10.0, kernel="rbf", gamma="scale", class_weight="balanced", random_state=2024),
                ),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_features="sqrt",
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            random_state=2024,
            n_jobs=-1,
        ),
    }


def evaluate_model(name, model, X, y, materials, split):
    train_idx, valid_idx = split
    t0 = time.perf_counter()
    model.fit(X[train_idx], y[train_idx])
    fit_seconds = time.perf_counter() - t0
    pred = model.predict(X[valid_idx])
    report = classification_report(
        y[valid_idx],
        pred,
        labels=[1, 2, 3],
        target_names=[LABEL_NAMES[i] for i in [1, 2, 3]],
        output_dict=True,
        zero_division=0,
    )

    # Strict generalization check: hold out each material entirely.
    leave_one = []
    for material in sorted(set(materials.tolist())):
        tr = materials != material
        va = materials == material
        grouped = make_models()[name]
        grouped.fit(X[tr], y[tr])
        grouped_pred = grouped.predict(X[va])
        leave_one.append(
            {
                "held_out_material": material,
                "samples": int(va.sum()),
                "accuracy": float(accuracy_score(y[va], grouped_pred)),
                "macro_f1": float(f1_score(y[va], grouped_pred, average="macro")),
                "confusion_matrix": confusion_matrix(y[va], grouped_pred, labels=[1, 2, 3]).tolist(),
            }
        )

    return {
        "fit_seconds": fit_seconds,
        "holdout_accuracy": float(accuracy_score(y[valid_idx], pred)),
        "holdout_macro_f1": float(f1_score(y[valid_idx], pred, average="macro")),
        "holdout_confusion_matrix": confusion_matrix(y[valid_idx], pred, labels=[1, 2, 3]).tolist(),
        "holdout_classification_report": report,
        "leave_one_material_out": leave_one,
        "holdout_pred": pred,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    X, y, materials, _ = read_csv(BASE / "train_features.csv", label=True)
    X_test, _, test_materials, test_ids = read_csv(BASE / "test_features.csv", label=False)
    idx = np.arange(len(y))
    train_idx, valid_idx = train_test_split(idx, test_size=0.20, random_state=2024, stratify=y)
    split = (train_idx, valid_idx)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=2024)

    all_results = {
        "protocol": {
            "features": FEATURE_NAMES,
            "train_samples": int(len(y)),
            "holdout_test_size": 0.20,
            "random_state": 2024,
            "labels": LABEL_NAMES,
            "note": "All models use only the same 8 waveform features; no temperature/frequency/material inputs.",
        },
        "models": {},
    }
    prediction_rows = {int(sample_id): {"sample_id": int(sample_id)} for sample_id in test_ids}
    for name, model in make_models().items():
        print(f"Evaluating {name}", flush=True)
        result = evaluate_model(name, model, X, y, materials, split)
        cv_acc = cross_val_score(model, X, y, cv=cv, scoring="accuracy", n_jobs=None)
        cv_f1 = cross_val_score(model, X, y, cv=cv, scoring="f1_macro", n_jobs=None)
        result.update(
            {
                "cv_accuracy_scores": cv_acc.tolist(),
                "cv_accuracy_mean": float(cv_acc.mean()),
                "cv_accuracy_std": float(cv_acc.std()),
                "cv_macro_f1_scores": cv_f1.tolist(),
                "cv_macro_f1_mean": float(cv_f1.mean()),
                "cv_macro_f1_std": float(cv_f1.std()),
            }
        )
        del result["holdout_pred"]

        final_model = make_models()[name]
        final_model.fit(X, y)
        pred = final_model.predict(X_test)
        for i, sample_id in enumerate(test_ids):
            prediction_rows[int(sample_id)][f"{name}_id"] = int(pred[i])
            prediction_rows[int(sample_id)][f"{name}_name"] = LABEL_NAMES[int(pred[i])]
        joblib.dump(final_model, OUT / f"{name}.joblib")
        all_results["models"][name] = result

    rows = list(prediction_rows.values())
    fields = ["sample_id"]
    for name in ["rbf_svm", "random_forest"]:
        fields += [f"{name}_id", f"{name}_name"]
    with (OUT / "attachment2_model_predictions.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    # Agreement is useful because Q1's test labels are not externally available.
    svm_pred = np.asarray([row["rbf_svm_id"] for row in rows])
    rf_pred = np.asarray([row["random_forest_id"] for row in rows])
    agreement = {
        "count": int(len(rows)),
        "same_count": int(np.sum(svm_pred == rf_pred)),
        "same_rate": float(np.mean(svm_pred == rf_pred)),
        "disagreements": [
            {"sample_id": int(rows[i]["sample_id"]), "rbf_svm_id": int(svm_pred[i]), "random_forest_id": int(rf_pred[i])}
            for i in range(len(rows))
            if svm_pred[i] != rf_pred[i]
        ],
    }
    all_results["test_prediction_agreement"] = agreement
    (OUT / "comparison.json").write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")

    # Human-readable comparison summary.
    lines = [
        "# Q1 candidate model comparison",
        "",
        "Both candidates use the same 8 waveform-only features and the same fixed splits.",
        "",
        "| model | holdout accuracy | holdout Macro-F1 | 5-fold accuracy | 5-fold Macro-F1 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, result in all_results["models"].items():
        lines.append(
            f"| {name} | {result['holdout_accuracy']:.6f} | {result['holdout_macro_f1']:.6f} | "
            f"{result['cv_accuracy_mean']:.6f} +/- {result['cv_accuracy_std']:.6f} | "
            f"{result['cv_macro_f1_mean']:.6f} +/- {result['cv_macro_f1_std']:.6f} |"
        )
    lines += [
        "",
        f"Test agreement: {agreement['same_count']}/{agreement['count']} = {agreement['same_rate']:.6f}",
        f"Disagreements: {len(agreement['disagreements'])}",
    ]
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(all_results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
