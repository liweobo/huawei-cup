"""Fold-safe Q1-Q4 modeling for the 2021D graduation blind run.

All learned preprocessing and feature selection lives inside the relevant CV
pipeline. The 50 prediction rows are loaded only for final application and
outer-fold uncertainty proxies; their labels are absent and never consulted.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
import time
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    KFold,
    StratifiedKFold,
    cross_val_predict,
)
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


SEED = 20210922
RUN_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = RUN_ROOT / "source-provenance" / "original"
OUTPUT_DIR = RUN_ROOT / "outputs"
RECORD_DIR = RUN_ROOT / "experiment-records"
ENDPOINTS = ["Caco-2", "CYP3A4", "hERG", "HOB", "MN"]
PRIMARY_FAVORABLE = {"Caco-2": 1, "CYP3A4": 1, "hERG": 0, "HOB": 1, "MN": 0}
ALTERNATE_FAVORABLE = {**PRIMARY_FAVORABLE, "CYP3A4": 0}


class FoldSafeDescriptorFilter(BaseEstimator, TransformerMixin):
    """Drop fold-constant, extremely sparse, and exact-duplicate columns."""

    def __init__(self, near_constant_threshold: float = 0.995):
        self.near_constant_threshold = near_constant_threshold

    def fit(self, X: pd.DataFrame, y: Any = None):
        frame = self._frame(X)
        mode_frequency = frame.apply(lambda s: s.value_counts(dropna=False).iloc[0] / len(s))
        variable = mode_frequency < self.near_constant_threshold
        provisional = frame.loc[:, variable]
        duplicates = provisional.T.duplicated(keep="first")
        self.feature_names_in_ = np.asarray(frame.columns, dtype=object)
        self.kept_columns_ = np.asarray(provisional.columns[~duplicates], dtype=object)
        self.dropped_near_constant_ = np.asarray(frame.columns[~variable], dtype=object)
        self.dropped_duplicate_ = np.asarray(provisional.columns[duplicates], dtype=object)
        if len(self.kept_columns_) == 0:
            raise ValueError("descriptor filter removed every feature")
        return self

    def transform(self, X: pd.DataFrame):
        frame = self._frame(X)
        return frame.loc[:, self.kept_columns_]

    def get_feature_names_out(self, input_features=None):
        return self.kept_columns_

    @staticmethod
    def _frame(X: Any) -> pd.DataFrame:
        if isinstance(X, pd.DataFrame):
            return X
        raise TypeError("FoldSafeDescriptorFilter requires a pandas DataFrame")


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, float):
        return None if not math.isfinite(value) else value
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    return value


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(payload), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "mae": mean_absolute_error(y_true, y_pred),
        "rmse": math.sqrt(mean_squared_error(y_true, y_pred)),
        "r2": r2_score(y_true, y_pred),
    }


def expected_calibration_error(y_true: np.ndarray, probability: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    bucket = np.digitize(probability, edges[1:-1], right=True)
    ece = 0.0
    for idx in range(bins):
        mask = bucket == idx
        if mask.any():
            ece += mask.mean() * abs(y_true[mask].mean() - probability[mask].mean())
    return float(ece)


def classification_metrics(y_true: np.ndarray, probability: np.ndarray, threshold: float) -> dict[str, float]:
    prediction = (probability >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, prediction, labels=[0, 1]).ravel()
    return {
        "roc_auc": roc_auc_score(y_true, probability),
        "pr_auc": average_precision_score(y_true, probability),
        "accuracy": accuracy_score(y_true, prediction),
        "balanced_accuracy": balanced_accuracy_score(y_true, prediction),
        "recall": recall_score(y_true, prediction, zero_division=0),
        "precision": precision_score(y_true, prediction, zero_division=0),
        "f1": f1_score(y_true, prediction, zero_division=0),
        "macro_f1": f1_score(y_true, prediction, average="macro", zero_division=0),
        "specificity": tn / (tn + fp) if tn + fp else 0.0,
        "brier": brier_score_loss(y_true, probability),
        "ece_10bin": expected_calibration_error(y_true, probability),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def choose_threshold(y_true: np.ndarray, probability: np.ndarray) -> tuple[float, dict[str, float]]:
    candidates = np.unique(np.concatenate([np.linspace(0.05, 0.95, 91), [0.5]]))
    scored = []
    for threshold in candidates:
        prediction = (probability >= threshold).astype(int)
        score = balanced_accuracy_score(y_true, prediction)
        f1 = f1_score(y_true, prediction, zero_division=0)
        scored.append((score, f1, -abs(threshold - 0.5), float(threshold)))
    best = max(scored)
    return best[3], {"inner_balanced_accuracy": best[0], "inner_f1": best[1]}


def selected_features(estimator: Pipeline) -> list[str]:
    names = np.asarray(estimator.named_steps["descriptor_filter"].kept_columns_, dtype=object)
    support = estimator.named_steps["select"].get_support()
    return [str(name) for name in names[support]]


def selection_ranking(estimator: Pipeline) -> list[tuple[str, float, float]]:
    selector = estimator.named_steps["select"]
    names = np.asarray(estimator.named_steps["descriptor_filter"].kept_columns_, dtype=object)
    rows = [(str(name), float(score), float(pvalue)) for name, score, pvalue in zip(names, selector.scores_, selector.pvalues_)]
    return sorted(rows, key=lambda row: (-np.nan_to_num(row[1], nan=-np.inf), row[0]))


def summarize_fold_metrics(rows: list[dict[str, Any]], group_keys: list[str]) -> list[dict[str, Any]]:
    frame = pd.DataFrame(rows)
    metric_columns = [
        column
        for column in frame.columns
        if column not in set(group_keys + ["fold", "threshold", "best_params", "selected_features"])
        and pd.api.types.is_numeric_dtype(frame[column])
    ]
    output = []
    for keys, group in frame.groupby(group_keys, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        record = dict(zip(group_keys, keys))
        record["fold_count"] = len(group)
        for metric in metric_columns:
            values = group[metric].astype(float)
            record[f"{metric}_mean"] = values.mean()
            record[f"{metric}_std"] = values.std(ddof=1)
            record[f"{metric}_median"] = values.median()
            record[f"{metric}_min"] = values.min()
            record[f"{metric}_max"] = values.max()
        output.append(record)
    return output


def make_regression_pipeline(family: str) -> tuple[Pipeline, dict[str, list[Any]]]:
    if family == "ridge":
        model = Ridge()
        grid = {"model__alpha": [0.1, 1.0, 10.0, 100.0]}
        steps = [
            ("descriptor_filter", FoldSafeDescriptorFilter()),
            ("select", SelectKBest(f_regression, k=20)),
            ("scale", StandardScaler()),
            ("model", model),
        ]
    elif family == "extra_trees":
        model = ExtraTreesRegressor(n_estimators=160, random_state=SEED, n_jobs=-1)
        grid = {
            "model__max_features": [0.5, 1.0],
            "model__min_samples_leaf": [1, 4],
        }
        steps = [
            ("descriptor_filter", FoldSafeDescriptorFilter()),
            ("select", SelectKBest(f_regression, k=20)),
            ("model", model),
        ]
    else:
        raise ValueError(family)
    return Pipeline(steps), grid


def make_classification_pipeline(family: str) -> tuple[Pipeline, dict[str, list[Any]]]:
    if family == "logistic":
        model = LogisticRegression(max_iter=3000, solver="liblinear", random_state=SEED)
        grid = {
            "model__C": [0.1, 1.0, 10.0],
            "model__class_weight": [None, "balanced"],
        }
        steps = [
            ("descriptor_filter", FoldSafeDescriptorFilter()),
            ("select", SelectKBest(f_classif, k=30)),
            ("scale", StandardScaler()),
            ("model", model),
        ]
    elif family == "extra_trees":
        model = ExtraTreesClassifier(
            n_estimators=140,
            class_weight="balanced",
            random_state=SEED,
            n_jobs=-1,
        )
        grid = {
            "model__max_features": ["sqrt", 0.3],
            "model__min_samples_leaf": [1, 5],
        }
        steps = [
            ("descriptor_filter", FoldSafeDescriptorFilter()),
            ("select", SelectKBest(f_classif, k=30)),
            ("model", model),
        ]
    else:
        raise ValueError(family)
    return Pipeline(steps), grid


def descriptor_audit(X: pd.DataFrame, X_test: pd.DataFrame) -> dict[str, Any]:
    values = X.to_numpy(dtype=float)
    mode_frequency = X.apply(lambda s: s.value_counts(dropna=False).iloc[0] / len(s))
    unique = X.nunique(dropna=False)
    duplicate_mask = X.T.duplicated(keep="first")
    nonconstant = X.loc[:, unique > 1]
    correlation = nonconstant.corr().abs()
    array = correlation.to_numpy()
    upper = np.triu_indices_from(array, k=1)
    correlations = array[upper]
    order = np.argsort(np.nan_to_num(correlations, nan=-1.0))[-50:][::-1]
    top_pairs = [
        {
            "left": str(nonconstant.columns[upper[0][idx]]),
            "right": str(nonconstant.columns[upper[1][idx]]),
            "absolute_correlation": float(correlations[idx]),
        }
        for idx in order
    ]
    median = X.median()
    mad = (X - median).abs().median()
    valid_mad = mad > 0
    robust_z = (X.loc[:, valid_mad] - median[valid_mad]).abs().divide(1.4826 * mad[valid_mad])
    extreme_counts = (robust_z > 10).sum().sort_values(ascending=False)
    std = X.std(ddof=0)
    test_range_violations = ((X_test < X.min()) | (X_test > X.max())).sum(axis=1)
    return {
        "training_shape": list(X.shape),
        "prediction_shape": list(X_test.shape),
        "numeric_columns": int(X.shape[1]),
        "missing_training_cells": int(X.isna().sum().sum()),
        "missing_prediction_cells": int(X_test.isna().sum().sum()),
        "nonfinite_training_cells": int((~np.isfinite(values)).sum()),
        "constant_count": int((unique <= 1).sum()),
        "constant_columns": list(map(str, unique[unique <= 1].index)),
        "near_constant_99_count": int((mode_frequency >= 0.99).sum()),
        "near_constant_995_count": int((mode_frequency >= 0.995).sum()),
        "exact_duplicate_column_count": int(duplicate_mask.sum()),
        "exact_duplicate_columns": list(map(str, X.columns[duplicate_mask])),
        "absolute_correlation_ge_095_pairs": int(np.nansum(correlations >= 0.95)),
        "absolute_correlation_ge_099_pairs": int(np.nansum(correlations >= 0.99)),
        "top_correlated_pairs": top_pairs,
        "scale_std_min_nonzero": float(std[std > 0].min()),
        "scale_std_max": float(std.max()),
        "scale_std_ratio": float(std.max() / std[std > 0].min()),
        "robust_z_gt_10_cell_count": int((robust_z > 10).sum().sum()),
        "robust_z_gt_10_top_columns": {str(k): int(v) for k, v in extreme_counts.head(20).items()},
        "prediction_rows_with_any_full_descriptor_range_violation": int((test_range_violations > 0).sum()),
        "prediction_full_descriptor_range_violation_summary": {
            "min": int(test_range_violations.min()),
            "median": float(test_range_violations.median()),
            "max": int(test_range_violations.max()),
        },
        "audit_interpretation": "Extreme candidates are flags, not automatic deletions. Constant, near-constant, and exact-duplicate removal is re-fit inside every training fold.",
    }


def regression_run(X: pd.DataFrame, y: pd.Series, X_test: pd.DataFrame, ids: list[str]):
    outer = KFold(n_splits=5, shuffle=True, random_state=SEED)
    folds = []
    fold_rows = []
    prediction_rows = []
    test_by_family: dict[str, list[np.ndarray]] = {"ridge": [], "extra_trees": []}
    features_by_family: dict[str, list[list[str]]] = {"ridge": [], "extra_trees": []}
    oof = {name: np.full(len(y), np.nan) for name in ["mean", "median", "ridge", "extra_trees"]}
    for fold, (train_idx, valid_idx) in enumerate(outer.split(X), 1):
        print(f"Q2 fold {fold}/5", flush=True)
        folds.append(
            {
                "fold": fold,
                "train_ids": [ids[i] for i in train_idx],
                "validation_ids": [ids[i] for i in valid_idx],
            }
        )
        X_train, X_valid = X.iloc[train_idx], X.iloc[valid_idx]
        y_train, y_valid = y.iloc[train_idx], y.iloc[valid_idx]
        for strategy in ("mean", "median"):
            dummy = DummyRegressor(strategy=strategy).fit(X_train, y_train)
            valid_pred = dummy.predict(X_valid)
            train_pred = dummy.predict(X_train)
            oof[strategy][valid_idx] = valid_pred
            record = {"model": strategy, "fold": fold, **regression_metrics(y_valid, valid_pred)}
            record.update({f"train_{k}": v for k, v in regression_metrics(y_train, train_pred).items()})
            record["search_candidates"] = 1
            fold_rows.append(record)
        inner = KFold(n_splits=3, shuffle=True, random_state=SEED + fold)
        for family in ("ridge", "extra_trees"):
            pipeline, grid = make_regression_pipeline(family)
            search = GridSearchCV(
                pipeline,
                grid,
                scoring="neg_root_mean_squared_error",
                cv=inner,
                n_jobs=1,
                refit=True,
                return_train_score=False,
            ).fit(X_train, y_train)
            valid_pred = search.predict(X_valid)
            train_pred = search.predict(X_train)
            oof[family][valid_idx] = valid_pred
            test_by_family[family].append(search.predict(X_test))
            selected = selected_features(search.best_estimator_)
            features_by_family[family].append(selected)
            record = {
                "model": family,
                "fold": fold,
                **regression_metrics(y_valid, valid_pred),
                **{f"train_{k}": v for k, v in regression_metrics(y_train, train_pred).items()},
                "best_inner_rmse": -float(search.best_score_),
                "best_params": json.dumps(search.best_params_, sort_keys=True),
                "selected_features": json.dumps(selected, ensure_ascii=False),
                "search_candidates": len(search.cv_results_["params"]),
            }
            fold_rows.append(record)
    summary = summarize_fold_metrics(fold_rows, ["model"])
    summary_by_model = {row["model"]: row for row in summary}
    candidate_order = sorted(
        ["ridge", "extra_trees"], key=lambda name: summary_by_model[name]["rmse_mean"]
    )
    best = candidate_order[0]
    if abs(summary_by_model["ridge"]["rmse_mean"] - summary_by_model["extra_trees"]["rmse_mean"]) <= 0.02:
        best = "ridge"
    final_pipeline, final_grid = make_regression_pipeline(best)
    final_search = GridSearchCV(
        final_pipeline,
        final_grid,
        scoring="neg_root_mean_squared_error",
        cv=KFold(n_splits=5, shuffle=True, random_state=SEED + 99),
        n_jobs=1,
        refit=True,
    ).fit(X, y)
    final_estimator = final_search.best_estimator_
    test_point = final_search.predict(X_test)
    test_outer = np.vstack(test_by_family[best])
    test_uncertainty = test_outer.std(axis=0, ddof=1)
    final_features = selected_features(final_estimator)
    ranking = selection_ranking(final_estimator)
    feature_sets = features_by_family[best]
    pairwise_jaccard = []
    for left, right in combinations(feature_sets, 2):
        a, b = set(left), set(right)
        pairwise_jaccard.append(len(a & b) / len(a | b))
    frequency = pd.Series([item for group in feature_sets for item in group]).value_counts() / len(feature_sets)
    stability = {
        "fold_selected_features": feature_sets,
        "selection_frequency": {str(k): float(v) for k, v in frequency.items()},
        "pairwise_jaccard_mean": float(np.mean(pairwise_jaccard)),
        "pairwise_jaccard_min": float(np.min(pairwise_jaccard)),
        "pairwise_jaccard_max": float(np.max(pairwise_jaccard)),
        "stable_at_60pct": list(map(str, frequency[frequency >= 0.6].index)),
    }
    for model, preds in oof.items():
        for idx, prediction in enumerate(preds):
            prediction_rows.append(
                {
                    "compound_id": f"TRAIN{idx + 1:04d}",
                    "SMILES": ids[idx],
                    "model": model,
                    "observed_pIC50": float(y.iloc[idx]),
                    "predicted_pIC50": float(prediction),
                }
            )
    result = {
        "target": "pIC50",
        "target_type": "continuous; provided transformation verified against IC50_nM",
        "outer_protocol": "5-fold shuffled KFold, fixed seed; same rows and folds for every model",
        "inner_protocol": "3-fold KFold grid search inside each outer training fold",
        "selection_rule": "lowest mean outer-fold RMSE; choose Ridge when candidate means differ by <=0.02",
        "selected_model": best,
        "fold_metrics": fold_rows,
        "summary": summary,
        "final_best_params": final_search.best_params_,
        "final_inner_best_rmse": -float(final_search.best_score_),
        "final_selected_features": final_features,
        "final_feature_ranking": [
            {"descriptor": name, "f_score": score, "p_value": pvalue, "selected": name in final_features}
            for name, score, pvalue in ranking
        ],
        "feature_stability": stability,
        "search_budget": {
            "mean_baseline_candidates": 1,
            "median_baseline_candidates": 1,
            "ridge_candidates_per_inner_search": 4,
            "extra_trees_candidates_per_inner_search": 4,
            "outer_folds": 5,
        },
    }
    test_output = pd.DataFrame(
        {
            "candidate_id": [f"TEST{i + 1:03d}" for i in range(len(X_test))],
            "SMILES": list(X_test.index.astype(str)),
            "predicted_pIC50": test_point,
            "predicted_IC50_nM": np.power(10.0, 9.0 - test_point),
            "activity_uncertainty_outer_fold_sd": test_uncertainty,
        }
    )
    return result, pd.DataFrame(prediction_rows), test_output, folds, final_estimator, oof[best]


def classification_run(X: pd.DataFrame, labels: pd.DataFrame, X_test: pd.DataFrame, ids: list[str]):
    all_results: dict[str, Any] = {}
    all_fold_rows = []
    all_oof_rows = []
    folds_by_endpoint = {}
    final_estimators = {}
    test_output = pd.DataFrame(
        {
            "candidate_id": [f"TEST{i + 1:03d}" for i in range(len(X_test))],
            "SMILES": list(X_test.index.astype(str)),
        }
    )
    selected_oof = {}
    for endpoint_index, endpoint in enumerate(ENDPOINTS):
        print(f"Q3 endpoint {endpoint}", flush=True)
        y = labels[endpoint].astype(int)
        outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED + endpoint_index)
        fold_rows = []
        endpoint_folds = []
        oof = {name: np.full(len(y), np.nan) for name in ["majority", "logistic", "extra_trees"]}
        oof_threshold = {name: np.full(len(y), np.nan) for name in ["majority", "logistic", "extra_trees"]}
        test_by_family: dict[str, list[np.ndarray]] = {"logistic": [], "extra_trees": []}
        for fold, (train_idx, valid_idx) in enumerate(outer.split(X, y), 1):
            print(f"  fold {fold}/5", flush=True)
            endpoint_folds.append(
                {
                    "fold": fold,
                    "train_ids": [ids[i] for i in train_idx],
                    "validation_ids": [ids[i] for i in valid_idx],
                }
            )
            X_train, X_valid = X.iloc[train_idx], X.iloc[valid_idx]
            y_train, y_valid = y.iloc[train_idx], y.iloc[valid_idx]
            majority = DummyClassifier(strategy="prior").fit(X_train, y_train)
            majority_probability = majority.predict_proba(X_valid)[:, list(majority.classes_).index(1)]
            majority_class = int(y_train.value_counts().idxmax())
            majority_threshold = 0.5 if majority_class == 1 else 1.0
            oof["majority"][valid_idx] = majority_probability
            oof_threshold["majority"][valid_idx] = majority_threshold
            metrics = classification_metrics(y_valid.to_numpy(), majority_probability, majority_threshold)
            fold_rows.append(
                {
                    "endpoint": endpoint,
                    "model": "majority",
                    "fold": fold,
                    "threshold": majority_threshold,
                    "threshold_scope": "training-fold majority rule",
                    "search_candidates": 1,
                    **metrics,
                }
            )
            inner = StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED + fold + endpoint_index * 10)
            for family in ("logistic", "extra_trees"):
                pipeline, grid = make_classification_pipeline(family)
                search = GridSearchCV(
                    pipeline,
                    grid,
                    scoring="average_precision",
                    cv=inner,
                    n_jobs=1,
                    refit=True,
                ).fit(X_train, y_train)
                inner_probability = cross_val_predict(
                    clone(search.best_estimator_),
                    X_train,
                    y_train,
                    cv=inner,
                    method="predict_proba",
                    n_jobs=1,
                )[:, 1]
                threshold, threshold_metrics = choose_threshold(y_train.to_numpy(), inner_probability)
                valid_probability = search.predict_proba(X_valid)[:, 1]
                oof[family][valid_idx] = valid_probability
                oof_threshold[family][valid_idx] = threshold
                test_by_family[family].append(search.predict_proba(X_test)[:, 1])
                metrics = classification_metrics(y_valid.to_numpy(), valid_probability, threshold)
                fold_rows.append(
                    {
                        "endpoint": endpoint,
                        "model": family,
                        "fold": fold,
                        "threshold": threshold,
                        "threshold_scope": "inner validation only",
                        "inner_threshold_balanced_accuracy": threshold_metrics["inner_balanced_accuracy"],
                        "inner_threshold_f1": threshold_metrics["inner_f1"],
                        "best_inner_pr_auc": float(search.best_score_),
                        "best_params": json.dumps(search.best_params_, sort_keys=True),
                        "selected_features": json.dumps(selected_features(search.best_estimator_), ensure_ascii=False),
                        "search_candidates": len(search.cv_results_["params"]),
                        **metrics,
                    }
                )
        summary = summarize_fold_metrics(fold_rows, ["endpoint", "model"])
        summary_map = {row["model"]: row for row in summary}
        if abs(summary_map["logistic"]["pr_auc_mean"] - summary_map["extra_trees"]["pr_auc_mean"]) <= 0.01:
            selected = "logistic"
        else:
            selected = max(("logistic", "extra_trees"), key=lambda name: summary_map[name]["pr_auc_mean"])
        if summary_map[selected]["balanced_accuracy_mean"] < 0.5 or summary_map[selected]["recall_mean"] == 0:
            selected = "logistic"
        pipeline, grid = make_classification_pipeline(selected)
        final_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED + 100 + endpoint_index)
        final_search = GridSearchCV(
            pipeline,
            grid,
            scoring="average_precision",
            cv=final_cv,
            n_jobs=1,
            refit=True,
        ).fit(X, y)
        final_estimator = final_search.best_estimator_
        threshold_oof = cross_val_predict(
            clone(final_estimator), X, y, cv=final_cv, method="predict_proba", n_jobs=1
        )[:, 1]
        final_threshold, final_threshold_metrics = choose_threshold(y.to_numpy(), threshold_oof)
        test_probability = final_estimator.predict_proba(X_test)[:, 1]
        test_class = (test_probability >= final_threshold).astype(int)
        test_outer = np.vstack(test_by_family[selected])
        test_output[f"{endpoint}_probability"] = test_probability
        test_output[f"{endpoint}_probability_outer_fold_sd"] = test_outer.std(axis=0, ddof=1)
        test_output[f"{endpoint}_threshold"] = final_threshold
        test_output[f"{endpoint}_class"] = test_class
        selected_oof[endpoint] = {
            "probability": oof[selected],
            "threshold": oof_threshold[selected],
            "class": (oof[selected] >= oof_threshold[selected]).astype(int),
        }
        for family in ("majority", "logistic", "extra_trees"):
            for idx in range(len(y)):
                all_oof_rows.append(
                    {
                        "compound_id": f"TRAIN{idx + 1:04d}",
                        "SMILES": ids[idx],
                        "endpoint": endpoint,
                        "model": family,
                        "observed": int(y.iloc[idx]),
                        "probability": float(oof[family][idx]),
                        "threshold": float(oof_threshold[family][idx]),
                        "predicted": int(oof[family][idx] >= oof_threshold[family][idx]),
                    }
                )
        counts = y.value_counts().sort_index()
        endpoint_result = {
            "target_type": "binary",
            "class_counts": {str(label): int(count) for label, count in counts.items()},
            "positive_prevalence": float(y.mean()),
            "majority_class": int(counts.idxmax()),
            "majority_prevalence": float(counts.max() / counts.sum()),
            "outer_protocol": "5-fold endpoint-specific stratified CV",
            "inner_protocol": "3-fold stratified model selection and threshold tuning inside outer training folds",
            "selection_rule": "highest mean outer PR-AUC; choose logistic within 0.01; reject zero-recall or sub-0.5 balanced-accuracy candidate",
            "selected_model": selected,
            "fold_metrics": fold_rows,
            "summary": summary,
            "final_best_params": final_search.best_params_,
            "final_inner_pr_auc": float(final_search.best_score_),
            "final_threshold": final_threshold,
            "final_threshold_provenance": "5-fold out-of-fold probabilities on legal training rows after family freeze",
            "final_threshold_inner_metrics": final_threshold_metrics,
            "final_selected_features": selected_features(final_estimator),
            "search_budget": {
                "majority_candidates": 1,
                "logistic_candidates_per_inner_search": 6,
                "extra_trees_candidates_per_inner_search": 4,
                "outer_folds": 5,
            },
        }
        all_results[endpoint] = endpoint_result
        all_fold_rows.extend(fold_rows)
        folds_by_endpoint[endpoint] = endpoint_folds
        final_estimators[endpoint] = final_estimator
    return (
        all_results,
        pd.DataFrame(all_oof_rows),
        test_output,
        folds_by_endpoint,
        final_estimators,
        selected_oof,
    )


def applicability_domain(
    X: pd.DataFrame, X_test: pd.DataFrame, features: list[str]
) -> tuple[dict[str, Any], pd.DataFrame]:
    train = X.loc[:, features].astype(float)
    test = X_test.loc[:, features].astype(float)
    mean = train.mean()
    std = train.std(ddof=0).replace(0, 1.0)
    train_z = (train - mean) / std
    test_z = (test - mean) / std
    nn = NearestNeighbors(n_neighbors=2, metric="euclidean").fit(train_z)
    train_dist = nn.kneighbors(train_z, return_distance=True)[0][:, 1] / math.sqrt(len(features))
    test_dist = nn.kneighbors(test_z, n_neighbors=1, return_distance=True)[0][:, 0] / math.sqrt(len(features))
    thresholds = {f"q{q}": float(np.quantile(train_dist, q / 100)) for q in (90, 95, 99)}
    violations = ((test < train.min()) | (test > train.max())).sum(axis=1).astype(int)
    detail = pd.DataFrame(
        {
            "nearest_neighbor_rms_z_distance": test_dist,
            "selected_feature_range_violations": violations.to_numpy(),
            "pass_q90": (test_dist <= thresholds["q90"]) & (violations.to_numpy() == 0),
            "pass_q95": (test_dist <= thresholds["q95"]) & (violations.to_numpy() == 0),
            "pass_q99": (test_dist <= thresholds["q99"]) & (violations.to_numpy() == 0),
        },
        index=X_test.index,
    )
    summary = {
        "features": features,
        "dimension": len(features),
        "distance": "nearest training compound RMS standardized Euclidean distance",
        "training_reference": "leave-one-out nearest-neighbor distribution",
        "thresholds": thresholds,
        "range_gate": "all selected descriptors within training min/max",
        "test_pass_counts": {name: int(detail[name].sum()) for name in ["pass_q90", "pass_q95", "pass_q99"]},
    }
    return summary, detail


def search_candidates(candidate_frame: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]], str | None]:
    incumbent_id = None
    incumbent_value = -np.inf
    trace = []
    for row in candidate_frame.sort_values("candidate_id").itertuples(index=False):
        feasible = bool(row.hard_feasibility)
        objective = float(row.conservative_activity_objective)
        before = incumbent_value if np.isfinite(incumbent_value) else None
        accepted = feasible and objective > incumbent_value
        if accepted:
            incumbent_value = objective
            incumbent_id = row.candidate_id
        trace.append(
            {
                "iteration": len(trace) + 1,
                "candidate_id": row.candidate_id,
                "source_design_type": row.source_design_type,
                "feasible": feasible,
                "objective": objective,
                "incumbent_before": before,
                "incumbent_after": incumbent_value if np.isfinite(incumbent_value) else None,
                "accepted": accepted,
                "reason": "FEASIBLE_OBJECTIVE_IMPROVEMENT" if accepted else ("HARD_GATE_FAILED" if not feasible else "NO_IMPROVEMENT"),
            }
        )
    ranked = candidate_frame[candidate_frame["hard_feasibility"]].sort_values(
        ["conservative_activity_objective", "candidate_id"], ascending=[False, True]
    )
    return ranked, trace, incumbent_id


def synthetic_optimization_check() -> dict[str, Any]:
    frame = pd.DataFrame(
        [
            {"candidate_id": "HIGH_BUT_ADMET_FAIL", "source_design_type": "SYNTHETIC", "hard_feasibility": False, "conservative_activity_objective": 10.0},
            {"candidate_id": "HIGH_BUT_OOD", "source_design_type": "SYNTHETIC", "hard_feasibility": False, "conservative_activity_objective": 9.0},
            {"candidate_id": "FEASIBLE_BEST", "source_design_type": "SYNTHETIC", "hard_feasibility": True, "conservative_activity_objective": 7.0},
            {"candidate_id": "FEASIBLE_LOWER", "source_design_type": "SYNTHETIC", "hard_feasibility": True, "conservative_activity_objective": 6.0},
        ]
    )
    ranked, trace, incumbent = search_candidates(frame)
    checks = {
        "hard_gate_excludes_high_infeasible": "HIGH_BUT_ADMET_FAIL" not in set(ranked.candidate_id),
        "surrogate_boundary_excludes_ood": "HIGH_BUT_OOD" not in set(ranked.candidate_id),
        "candidate_update_keeps_best_feasible": incumbent == "FEASIBLE_BEST",
        "objective_order_correct": list(ranked.candidate_id) == ["FEASIBLE_BEST", "FEASIBLE_LOWER"],
    }
    return {"checks": checks, "trace": trace, "status": "PASS" if all(checks.values()) else "FAIL"}


def build_q4(
    X: pd.DataFrame,
    X_test: pd.DataFrame,
    activity: pd.Series,
    labels: pd.DataFrame,
    q2_test: pd.DataFrame,
    q3_test: pd.DataFrame,
    activity_estimator: Pipeline,
    endpoint_estimators: dict[str, Pipeline],
    q2_result: dict[str, Any],
    q3_result: dict[str, Any],
    dictionary: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], pd.DataFrame]:
    ad_summaries = {}
    ad_details = {}
    activity_features = selected_features(activity_estimator)
    ad_summaries["activity"], ad_details["activity"] = applicability_domain(X, X_test, activity_features)
    for endpoint in ENDPOINTS:
        features = selected_features(endpoint_estimators[endpoint])
        ad_summaries[endpoint], ad_details[endpoint] = applicability_domain(X, X_test, features)
    candidates = q2_test.merge(q3_test, on=["candidate_id", "SMILES"], validate="one_to_one")
    candidates["source_design_type"] = "OBSERVED_TEST_COMPOUND"
    candidates["descriptor_valid"] = np.isfinite(X_test.to_numpy(dtype=float)).all(axis=1)
    for model, detail in ad_details.items():
        safe = model.replace("-", "_")
        candidates[f"ad_{safe}_distance"] = detail["nearest_neighbor_rms_z_distance"].to_numpy()
        candidates[f"ad_{safe}_range_violations"] = detail["selected_feature_range_violations"].to_numpy()
        candidates[f"ad_{safe}_pass_q95"] = detail["pass_q95"].to_numpy()
    ad_columns = [column for column in candidates if column.endswith("_pass_q95")]
    candidates["applicability_domain_status"] = np.where(candidates[ad_columns].all(axis=1), "PASS", "FAIL")
    for endpoint in ENDPOINTS:
        candidates[f"{endpoint}_favorable_primary"] = (
            candidates[f"{endpoint}_class"] == PRIMARY_FAVORABLE[endpoint]
        )
        candidates[f"{endpoint}_favorable_alternate"] = (
            candidates[f"{endpoint}_class"] == ALTERNATE_FAVORABLE[endpoint]
        )
    candidates["favorable_count_primary"] = candidates[
        [f"{endpoint}_favorable_primary" for endpoint in ENDPOINTS]
    ].sum(axis=1)
    candidates["favorable_count_cyp3a4_alternate"] = candidates[
        [f"{endpoint}_favorable_alternate" for endpoint in ENDPOINTS]
    ].sum(axis=1)
    candidates["admet_hard_gate_primary"] = candidates["favorable_count_primary"] >= 3
    candidates["admet_hard_gate_cyp3a4_alternate"] = candidates["favorable_count_cyp3a4_alternate"] >= 3
    candidates["hard_feasibility"] = (
        candidates["descriptor_valid"]
        & candidates["admet_hard_gate_primary"]
        & (candidates["applicability_domain_status"] == "PASS")
    )
    candidates["conservative_activity_objective"] = (
        candidates["predicted_pIC50"] - candidates["activity_uncertainty_outer_fold_sd"]
    )
    ranked, trace, incumbent = search_candidates(candidates)
    candidates["final_disposition"] = "FEASIBLE_NOT_SELECTED"
    candidates.loc[~candidates["admet_hard_gate_primary"], "final_disposition"] = "FAIL_ADMET_HARD_GATE"
    candidates.loc[candidates["applicability_domain_status"] != "PASS", "final_disposition"] = "OUTSIDE_APPLICABILITY_DOMAIN"
    if incumbent is not None:
        candidates.loc[candidates["candidate_id"] == incumbent, "final_disposition"] = "SELECTED_SURROGATE_BEST"
    observed_favorable = pd.DataFrame(
        {endpoint: labels[endpoint].eq(PRIMARY_FAVORABLE[endpoint]) for endpoint in ENDPOINTS}
    ).sum(axis=1)
    observed_favorable_alt = pd.DataFrame(
        {endpoint: labels[endpoint].eq(ALTERNATE_FAVORABLE[endpoint]) for endpoint in ENDPOINTS}
    ).sum(axis=1)
    observed_eligible = observed_favorable >= 3
    best_index = activity[observed_eligible].idxmax()
    baseline_position = int(activity.index.get_loc(best_index))
    baseline = {
        "candidate_id": f"TRAIN{baseline_position + 1:04d}",
        "source_design_type": "OBSERVED_TRAINING_COMPOUND",
        "SMILES": str(best_index),
        "observed_pIC50": float(activity.loc[best_index]),
        "observed_IC50_nM": float(10 ** (9 - activity.loc[best_index])),
        "observed_favorable_count_primary": int(observed_favorable.loc[best_index]),
        "observed_favorable_count_cyp3a4_alternate": int(observed_favorable_alt.loc[best_index]),
        "scope": "best observed training compound satisfying at least three primary favorable labels",
    }
    robust_observed_eligible = (observed_favorable >= 3) & (observed_favorable_alt >= 3)
    robust_index = activity[robust_observed_eligible].idxmax()
    robust_position = int(activity.index.get_loc(robust_index))
    robust_baseline = {
        "candidate_id": f"TRAIN{robust_position + 1:04d}",
        "source_design_type": "OBSERVED_TRAINING_COMPOUND",
        "SMILES": str(robust_index),
        "observed_pIC50": float(activity.loc[robust_index]),
        "observed_IC50_nM": float(10 ** (9 - activity.loc[robust_index])),
        "observed_favorable_count_primary": int(observed_favorable.loc[robust_index]),
        "observed_favorable_count_cyp3a4_alternate": int(observed_favorable_alt.loc[robust_index]),
        "scope": "best observed training compound satisfying at least three favorable labels under both CYP3A4 direction assumptions",
    }
    elite_cutoff = float(activity[observed_eligible].quantile(0.75))
    elite_mask = observed_eligible & (activity >= elite_cutoff)
    profile_rows = []
    final_ranking = {row["descriptor"]: row for row in q2_result["final_feature_ranking"]}
    for descriptor in activity_features:
        global_values = X[descriptor]
        elite_values = X.loc[elite_mask, descriptor]
        info = dictionary.get(descriptor.casefold(), {})
        profile_rows.append(
            {
                "descriptor": descriptor,
                "description": info.get("description"),
                "descriptor_class": info.get("class"),
                "q1_f_score": final_ranking[descriptor]["f_score"],
                "elite_q10": elite_values.quantile(0.10),
                "elite_median": elite_values.median(),
                "elite_q90": elite_values.quantile(0.90),
                "training_q10": global_values.quantile(0.10),
                "training_median": global_values.median(),
                "training_q90": global_values.quantile(0.90),
                "standardized_median_shift": (elite_values.median() - global_values.median()) / (global_values.std(ddof=0) or 1.0),
                "claim": "empirical association within observed feasible training compounds; not a causal or synthesis rule",
            }
        )
    profile = pd.DataFrame(profile_rows).sort_values("q1_f_score", ascending=False)
    profile.to_csv(OUTPUT_DIR / "q4-descriptor-profiles.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(trace).to_csv(OUTPUT_DIR / "q4-search-trace.csv", index=False, encoding="utf-8-sig")
    sensitivity = []
    for cyp_direction_name, favorable_col in [
        ("CYP3A4_1_ASSUMED_FAVORABLE", "favorable_count_primary"),
        ("CYP3A4_0_ALTERNATE_FAVORABLE", "favorable_count_cyp3a4_alternate"),
    ]:
        for penalty in (0.0, 1.0, 2.0):
            feasible = (
                (candidates[favorable_col] >= 3)
                & (candidates["applicability_domain_status"] == "PASS")
                & candidates["descriptor_valid"]
            )
            objective = candidates["predicted_pIC50"] - penalty * candidates["activity_uncertainty_outer_fold_sd"]
            if feasible.any():
                idx = objective.where(feasible).idxmax()
                sensitivity.append(
                    {
                        "cyp3a4_direction": cyp_direction_name,
                        "uncertainty_penalty": penalty,
                        "feasible_count": int(feasible.sum()),
                        "top_candidate": candidates.loc[idx, "candidate_id"],
                        "objective": float(objective.loc[idx]),
                    }
                )
            else:
                sensitivity.append(
                    {
                        "cyp3a4_direction": cyp_direction_name,
                        "uncertainty_penalty": penalty,
                        "feasible_count": 0,
                        "top_candidate": None,
                        "objective": None,
                    }
                )
    synthetic = synthetic_optimization_check()
    result = {
        "evaluation_contract": {
            "evaluation_object": "the 50 source-provided prediction compounds",
            "decision_question": "which in-domain compound satisfying at least three predicted favorable ADMET endpoints has the highest uncertainty-penalized predicted pIC50",
            "output_semantics": "RANK",
            "absolute_or_relative": "RELATIVE_TO_FIXED_50_COMPOUND_SET",
            "threshold_provenance": "endpoint-specific validation thresholds from Q3",
            "allowed_claim": "surrogate ranking within the fixed observed candidate set; requires experimental verification",
            "status": "EVALUATION_SEMANTICS_VERIFIED",
        },
        "design_variable": "choice among 50 source-provided compounds; descriptors are observed attributes, not independently editable coordinates",
        "optimization_domain": "finite observed candidate set of 50 prediction compounds",
        "hard_constraints": [
            "source descriptor row is finite",
            "at least three of five endpoint classes are favorable under the declared direction map",
            "candidate passes every target-specific q95 nearest-neighbor and selected-feature range applicability gate",
        ],
        "soft_objective": "maximize predicted pIC50 minus one outer-fold prediction standard deviation",
        "weight_provenance": "DERIVED one-standard-deviation uncertainty penalty; sensitivity at 0, 1, and 2",
        "favorable_direction_primary": PRIMARY_FAVORABLE,
        "favorable_direction_note": "CYP3A4=1 is ASSUMED because the problem defines metabolizability but no monotone desirable state; alternate direction is reported.",
        "applicability_domain": ad_summaries,
        "baseline_existing_compound": baseline,
        "direction_robust_baseline_existing_compound": robust_baseline,
        "elite_profile_definition": {
            "observed_admet_gate": "at least 3 primary favorable labels",
            "activity_cutoff": elite_cutoff,
            "elite_count": int(elite_mask.sum()),
            "range": "10th-90th percentile for each final Q1 descriptor",
        },
        "search_budget": {"candidate_count": len(candidates), "evaluated_candidates": len(candidates), "method": "exhaustive enumeration"},
        "solver_status": "OPTIMAL" if incumbent is not None else "UNKNOWN",
        "solver_status_scope": "exact only within the fixed 50-compound surrogate-ranking domain",
        "selected_candidate": incumbent,
        "feasible_candidate_count": int(candidates["hard_feasibility"].sum()),
        "sensitivity": sensitivity,
        "synthetic_optimization_check": synthetic,
        "claim_boundary": "SURROGATE; no new molecule, structure reconstruction, synthesis feasibility, true activity, or true ADMET is claimed",
    }
    return result, candidates


def load_dictionary() -> dict[str, dict[str, Any]]:
    dictionary = pd.read_excel(SOURCE_DIR / "分子描述符含义解释.xlsx", sheet_name="Detailed")
    mapping = {}
    for row in dictionary.itertuples(index=False):
        descriptor = getattr(row, "Descriptor", None)
        if isinstance(descriptor, str):
            mapping[descriptor.casefold()] = {
                "description": getattr(row, "Description", None),
                "class": getattr(row, "Class", None),
            }
    return mapping


def main() -> None:
    start = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RECORD_DIR.mkdir(parents=True, exist_ok=True)
    descriptor_train = pd.read_excel(SOURCE_DIR / "Molecular_Descriptor.xlsx", sheet_name="training", index_col="SMILES")
    descriptor_test = pd.read_excel(SOURCE_DIR / "Molecular_Descriptor.xlsx", sheet_name="test", index_col="SMILES")
    activity_frame = pd.read_excel(SOURCE_DIR / "ERα_activity.xlsx", sheet_name="training", index_col="SMILES")
    labels = pd.read_excel(SOURCE_DIR / "ADMET.xlsx", sheet_name="training", index_col="SMILES")
    if not descriptor_train.index.equals(activity_frame.index) or not descriptor_train.index.equals(labels.index):
        raise RuntimeError("training entity alignment changed")
    if descriptor_train.index.intersection(descriptor_test.index).size:
        raise RuntimeError("training/prediction overlap")
    X = descriptor_train.astype(float)
    X_test = descriptor_test.astype(float)
    y = activity_frame["pIC50"].astype(float)
    ids = list(X.index.astype(str))
    audit = descriptor_audit(X, X_test)
    write_json(OUTPUT_DIR / "descriptor-audit.json", audit)
    print("Starting Q1/Q2 regression", flush=True)
    q2, q2_oof, q2_test, q2_folds, activity_estimator, selected_q2_oof = regression_run(X, y, X_test, ids)
    q2_oof.to_csv(OUTPUT_DIR / "q2-oof-predictions.csv", index=False, encoding="utf-8-sig")
    q2_test.to_csv(OUTPUT_DIR / "q2-test-predictions.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(q2["fold_metrics"]).to_csv(OUTPUT_DIR / "q2-fold-metrics.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(q2["summary"]).to_csv(OUTPUT_DIR / "q2-model-summary.csv", index=False, encoding="utf-8-sig")
    write_json(OUTPUT_DIR / "q2-results.json", q2)
    write_json(OUTPUT_DIR / "fold-ids-q2.json", q2_folds)
    print("Starting Q3 classification", flush=True)
    q3, q3_oof, q3_test, q3_folds, endpoint_estimators, selected_q3_oof = classification_run(X, labels, X_test, ids)
    q3_oof.to_csv(OUTPUT_DIR / "q3-oof-predictions.csv", index=False, encoding="utf-8-sig")
    q3_test.to_csv(OUTPUT_DIR / "q3-test-predictions.csv", index=False, encoding="utf-8-sig")
    q3_fold_metrics = pd.concat([pd.DataFrame(q3[e]["fold_metrics"]) for e in ENDPOINTS], ignore_index=True)
    q3_summary = pd.concat([pd.DataFrame(q3[e]["summary"]) for e in ENDPOINTS], ignore_index=True)
    q3_fold_metrics.to_csv(OUTPUT_DIR / "q3-fold-metrics.csv", index=False, encoding="utf-8-sig")
    q3_summary.to_csv(OUTPUT_DIR / "q3-model-summary.csv", index=False, encoding="utf-8-sig")
    write_json(OUTPUT_DIR / "q3-results.json", q3)
    write_json(OUTPUT_DIR / "fold-ids-q3.json", q3_folds)
    print("Starting Q4 fixed-domain search", flush=True)
    dictionary = load_dictionary()
    q4, candidates = build_q4(
        X,
        X_test,
        y,
        labels,
        q2_test,
        q3_test,
        activity_estimator,
        endpoint_estimators,
        q2,
        q3,
        dictionary,
    )
    candidates.to_csv(OUTPUT_DIR / "candidate-ledger.csv", index=False, encoding="utf-8-sig")
    write_json(OUTPUT_DIR / "q4-results.json", q4)
    outputs_for_hash = [
        OUTPUT_DIR / "q2-test-predictions.csv",
        OUTPUT_DIR / "q3-test-predictions.csv",
        OUTPUT_DIR / "candidate-ledger.csv",
        OUTPUT_DIR / "q2-oof-predictions.csv",
        OUTPUT_DIR / "q3-oof-predictions.csv",
    ]
    environment = {
        "random_seed": SEED,
        "python": sys.version,
        "platform": platform.platform(),
        "libraries": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
            "joblib": joblib.__version__,
        },
        "runtime_seconds": time.time() - start,
        "output_sha256": {path.name: file_sha256(path) for path in outputs_for_hash},
    }
    write_json(OUTPUT_DIR / "runtime-provenance.json", environment)
    experiment_records = {
        "Q1_Q2": {
            "status": "OBSERVED",
            "target": "pIC50",
            "sample_ids": ids,
            "fold_file": "outputs/fold-ids-q2.json",
            "selection_scope": "TRAIN_FOLD",
            "selected_feature_ids": q2["final_selected_features"],
            "models": ["mean", "median", "ridge", "extra_trees"],
            "selected_model": q2["selected_model"],
            "seed": SEED,
        },
        "Q3": {
            "status": "OBSERVED",
            "targets": ENDPOINTS,
            "sample_ids": ids,
            "fold_file": "outputs/fold-ids-q3.json",
            "selection_scope": "TRAIN_FOLD",
            "threshold_scope": "INNER_VALIDATION",
            "selected_models": {endpoint: q3[endpoint]["selected_model"] for endpoint in ENDPOINTS},
            "selected_feature_ids": {endpoint: q3[endpoint]["final_selected_features"] for endpoint in ENDPOINTS},
            "seed": SEED,
        },
        "Q4": {
            "status": "OBSERVED",
            "domain": "50 observed prediction compounds",
            "surrogate": True,
            "search_budget": 50,
            "solver_status": q4["solver_status"],
            "synthetic_check": q4["synthetic_optimization_check"]["status"],
        },
    }
    for name, record in experiment_records.items():
        write_json(RECORD_DIR / f"{name.lower()}-experiment.json", record)
    print(f"Completed in {time.time() - start:.1f} seconds", flush=True)


if __name__ == "__main__":
    main()
