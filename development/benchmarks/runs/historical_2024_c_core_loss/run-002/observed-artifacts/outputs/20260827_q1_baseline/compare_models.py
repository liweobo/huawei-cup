import csv
import json
import os
import time

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

import q1_baseline as base


OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def evaluate_model(name, estimator, X_train, y_train, X_valid, y_valid):
    t0 = time.perf_counter()
    estimator.fit(X_train, y_train)
    fit_seconds = time.perf_counter() - t0
    t0 = time.perf_counter()
    pred = estimator.predict(X_valid)
    predict_seconds = time.perf_counter() - t0
    result = base.metrics(y_valid, pred)
    result.update(
        {
            "fit_seconds": float(fit_seconds),
            "predict_seconds": float(predict_seconds),
            "model": name,
        }
    )
    return result, pred


def predict_with_score(estimator, X):
    pred = estimator.predict(X)
    if hasattr(estimator, "decision_function"):
        raw = estimator.decision_function(X)
        if raw.ndim == 1:
            raw = np.column_stack([-raw, raw])
        order = np.argsort(raw, axis=1)
        margin = raw[np.arange(len(raw)), order[:, -1]] - raw[
            np.arange(len(raw)), order[:, -2]
        ]
    else:
        probs = estimator.predict_proba(X)
        order = np.argsort(probs, axis=1)
        margin = probs[np.arange(len(probs)), order[:, -1]] - probs[
            np.arange(len(probs)), order[:, -2]
        ]
    return pred.astype(int), margin.astype(float)


def leave_one_material_out(estimator_factory, X, y, groups):
    folds = {}
    all_true, all_pred = [], []
    total_fit = 0.0
    total_predict = 0.0
    for material in sorted(set(groups)):
        valid = groups == material
        estimator = estimator_factory()
        t0 = time.perf_counter()
        estimator.fit(X[~valid], y[~valid])
        total_fit += time.perf_counter() - t0
        t0 = time.perf_counter()
        pred = estimator.predict(X[valid])
        total_predict += time.perf_counter() - t0
        fold = base.metrics(y[valid], pred)
        folds[material] = fold
        all_true.append(y[valid])
        all_pred.append(pred)
    aggregate = base.metrics(np.concatenate(all_true), np.concatenate(all_pred))
    aggregate.update(
        {"fit_seconds": float(total_fit), "predict_seconds": float(total_predict)}
    )
    return {"folds": folds, "aggregate": aggregate}


def main():
    X, y, groups, duplicate_removed = base.read_train()
    test_ids, X_test = base.read_test()
    train_idx, valid_idx = base.stratified_split(y)

    # The two models deliberately use different inductive biases:
    # RBF-SVM learns a smooth nonlinear boundary; RF is a bagged tree ensemble.
    factories = {
        "rbf_svm": lambda: make_pipeline(
            StandardScaler(),
            SVC(C=10.0, gamma="scale", kernel="rbf", cache_size=2048),
        ),
        "random_forest": lambda: RandomForestClassifier(
            n_estimators=300,
            max_features="sqrt",
            min_samples_leaf=1,
            random_state=base.SEED,
            n_jobs=-1,
        ),
    }

    validation = {}
    fitted = {}
    predictions = {}
    for name, factory in factories.items():
        estimator = factory()
        result, pred = evaluate_model(
            name, estimator, X[train_idx], y[train_idx], X[valid_idx], y[valid_idx]
        )
        validation[name] = result
        fitted[name] = estimator
        predictions[name] = pred

    loo = {
        name: leave_one_material_out(factory, X, y, groups)
        for name, factory in factories.items()
    }

    # Fit on all training data for test predictions and compare with the baseline.
    test_prediction_rows = []
    test_predictions = {}
    for name, factory in factories.items():
        estimator = factory()
        t0 = time.perf_counter()
        estimator.fit(X, y)
        fit_seconds = time.perf_counter() - t0
        t0 = time.perf_counter()
        pred, margin = predict_with_score(estimator, X_test)
        predict_seconds = time.perf_counter() - t0
        test_predictions[name] = pred
        for i, sample_id in enumerate(test_ids):
            test_prediction_rows.append(
                {
                    "序号": int(sample_id),
                    "模型": name,
                    "分类编号": int(pred[i]),
                    "分类": base.LABELS[pred[i] - 1],
                    "置信间隔": float(margin[i]),
                    "fit_seconds": float(fit_seconds),
                    "predict_seconds": float(predict_seconds),
                }
            )

    baseline_estimator = base.fit_gaussian_nb(X, y)
    baseline_pred, _ = base.predict_gaussian_nb(X_test, baseline_estimator)

    agreement = {}
    for name, pred in test_predictions.items():
        agreement[name] = {
            "with_gaussian_naive_bayes": float(np.mean(pred == baseline_pred)),
            "disagreements": int(np.sum(pred != baseline_pred)),
            "with_other_candidate": None,
        }
    agreement["rbf_svm"]["with_other_candidate"] = float(
        np.mean(test_predictions["rbf_svm"] == test_predictions["random_forest"])
    )
    agreement["random_forest"]["with_other_candidate"] = agreement["rbf_svm"][
        "with_other_candidate"
    ]

    summary = {
        "feature_pipeline": "same as q1_baseline.py: de-mean/peak-to-peak normalization + FFT/quantile/slope features",
        "seed": base.SEED,
        "training_rows_after_duplicate_removal": int(len(y)),
        "duplicate_removed": duplicate_removed,
        "validation_split": {
            "type": "same stratified holdout as baseline",
            "train_rows": int(len(train_idx)),
            "valid_rows": int(len(valid_idx)),
        },
        "candidates": {
            "rbf_svm": {
                "description": "RBF-kernel support vector machine; standardized features; C=10, gamma=scale",
                "inductive_bias": "smooth nonlinear decision boundary",
            },
            "random_forest": {
                "description": "300-tree random forest; sqrt feature subsampling",
                "inductive_bias": "bagged axis-aligned decision trees",
            },
        },
        "validation_metrics": validation,
        "leave_one_material_out_metrics": loo,
        "test_prediction_counts": {
            name: {
                base.LABELS[c - 1]: int(np.sum(pred == c)) for c in (1, 2, 3)
            }
            for name, pred in test_predictions.items()
        },
        "test_agreement": agreement,
    }

    with open(os.path.join(OUT_DIR, "model_comparison.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with open(
        os.path.join(OUT_DIR, "model_comparison_predictions.csv"),
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=test_prediction_rows[0].keys())
        writer.writeheader()
        writer.writerows(test_prediction_rows)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
