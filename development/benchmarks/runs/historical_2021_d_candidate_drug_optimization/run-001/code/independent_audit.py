"""Independently recompute Q2, Q3, and Q4 evidence from saved records."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
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


RUN_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = RUN_ROOT / "outputs"
ENDPOINTS = ["Caco-2", "CYP3A4", "hERG", "HOB", "MN"]
PRIMARY_FAVORABLE = {"Caco-2": 1, "CYP3A4": 1, "hERG": 0, "HOB": 1, "MN": 0}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def ece(y: np.ndarray, probability: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0.0, 1.0, bins + 1)
    bucket = np.digitize(probability, edges[1:-1], right=True)
    result = 0.0
    for idx in range(bins):
        mask = bucket == idx
        if mask.any():
            result += mask.mean() * abs(y[mask].mean() - probability[mask].mean())
    return float(result)


def classification_metrics(y: np.ndarray, probability: np.ndarray, threshold: float) -> dict[str, float]:
    pred = (probability >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "roc_auc": roc_auc_score(y, probability),
        "pr_auc": average_precision_score(y, probability),
        "accuracy": accuracy_score(y, pred),
        "balanced_accuracy": balanced_accuracy_score(y, pred),
        "recall": recall_score(y, pred, zero_division=0),
        "precision": precision_score(y, pred, zero_division=0),
        "f1": f1_score(y, pred, zero_division=0),
        "macro_f1": f1_score(y, pred, average="macro", zero_division=0),
        "specificity": tn / (tn + fp) if tn + fp else 0.0,
        "brier": brier_score_loss(y, probability),
        "ece_10bin": ece(y, probability),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def map_folds(fold_records: list[dict], endpoint: str | None = None) -> dict[str, int]:
    records = fold_records[endpoint] if endpoint is not None else fold_records
    mapping = {}
    for record in records:
        for identifier in record["validation_ids"]:
            if identifier in mapping:
                raise AssertionError("validation entity repeated across folds")
            mapping[identifier] = int(record["fold"])
    return mapping


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def main() -> None:
    q2 = json.loads((OUTPUT_DIR / "q2-results.json").read_text(encoding="utf-8"))
    q3 = json.loads((OUTPUT_DIR / "q3-results.json").read_text(encoding="utf-8"))
    q4 = json.loads((OUTPUT_DIR / "q4-results.json").read_text(encoding="utf-8"))
    q2_oof = pd.read_csv(OUTPUT_DIR / "q2-oof-predictions.csv")
    q3_oof = pd.read_csv(OUTPUT_DIR / "q3-oof-predictions.csv")
    q2_folds = json.loads((OUTPUT_DIR / "fold-ids-q2.json").read_text(encoding="utf-8"))
    q3_folds = json.loads((OUTPUT_DIR / "fold-ids-q3.json").read_text(encoding="utf-8"))
    q2_fold_map = map_folds(q2_folds)
    q2_oof["fold"] = q2_oof["SMILES"].map(q2_fold_map)
    q2_saved = {(row["model"], int(row["fold"])): row for row in q2["fold_metrics"]}
    q2_checks = []
    for (model, fold), frame in q2_oof.groupby(["model", "fold"]):
        y = frame["observed_pIC50"].to_numpy()
        pred = frame["predicted_pIC50"].to_numpy()
        metrics = {
            "mae": mean_absolute_error(y, pred),
            "rmse": math.sqrt(mean_squared_error(y, pred)),
            "r2": r2_score(y, pred),
        }
        saved = q2_saved[(model, int(fold))]
        differences = {metric: abs(metrics[metric] - saved[metric]) for metric in metrics}
        q2_checks.append(
            {
                "model": model,
                "fold": int(fold),
                "recomputed": metrics,
                "max_absolute_difference": max(differences.values()),
                "status": "PASS" if max(differences.values()) <= 1e-12 else "FAIL",
            }
        )
    q3_checks = []
    for endpoint in ENDPOINTS:
        fold_map = map_folds(q3_folds, endpoint)
        endpoint_frame = q3_oof[q3_oof["endpoint"] == endpoint].copy()
        endpoint_frame["fold"] = endpoint_frame["SMILES"].map(fold_map)
        saved_rows = {
            (row["model"], int(row["fold"])): row for row in q3[endpoint]["fold_metrics"]
        }
        for (model, fold), frame in endpoint_frame.groupby(["model", "fold"]):
            thresholds = frame["threshold"].unique()
            if len(thresholds) != 1:
                raise AssertionError("threshold changed within a held-out fold")
            recomputed = classification_metrics(
                frame["observed"].to_numpy(dtype=int),
                frame["probability"].to_numpy(dtype=float),
                float(thresholds[0]),
            )
            saved = saved_rows[(model, int(fold))]
            differences = {metric: abs(recomputed[metric] - saved[metric]) for metric in recomputed}
            q3_checks.append(
                {
                    "endpoint": endpoint,
                    "model": model,
                    "fold": int(fold),
                    "recomputed": recomputed,
                    "max_absolute_difference": max(differences.values()),
                    "status": "PASS" if max(differences.values()) <= 1e-12 else "FAIL",
                }
            )
    candidates = pd.read_csv(OUTPUT_DIR / "candidate-ledger.csv")
    favorable = pd.DataFrame(
        {
            endpoint: candidates[f"{endpoint}_class"].eq(PRIMARY_FAVORABLE[endpoint])
            for endpoint in ENDPOINTS
        }
    ).sum(axis=1)
    ad_columns = [column for column in candidates if column.endswith("_pass_q95")]
    recomputed_ad = candidates[ad_columns].all(axis=1)
    recomputed_feasible = (
        candidates["descriptor_valid"].astype(bool)
        & (favorable >= 3)
        & recomputed_ad
    )
    recomputed_objective = (
        candidates["predicted_pIC50"] - candidates["activity_uncertainty_outer_fold_sd"]
    )
    if recomputed_feasible.any():
        selected_index = recomputed_objective.where(recomputed_feasible).idxmax()
        selected_candidate = candidates.loc[selected_index, "candidate_id"]
    else:
        selected_candidate = None
    q4_checks = {
        "favorable_counts_match": bool((favorable == candidates["favorable_count_primary"]).all()),
        "applicability_status_match": bool(
            (recomputed_ad == candidates["applicability_domain_status"].eq("PASS")).all()
        ),
        "hard_feasibility_match": bool(
            (recomputed_feasible == candidates["hard_feasibility"].astype(bool)).all()
        ),
        "objective_max_abs_difference": float(
            np.max(np.abs(recomputed_objective - candidates["conservative_activity_objective"]))
        ),
        "selected_candidate_recomputed": selected_candidate,
        "selected_candidate_saved": q4["selected_candidate"],
        "selected_candidate_match": selected_candidate == q4["selected_candidate"],
        "feasible_count_recomputed": int(recomputed_feasible.sum()),
        "feasible_count_saved": int(q4["feasible_candidate_count"]),
        "synthetic_check_saved": q4["synthetic_optimization_check"]["status"],
    }
    provenance = json.loads((OUTPUT_DIR / "runtime-provenance.json").read_text(encoding="utf-8"))
    hash_checks = {}
    for filename, expected in provenance["output_sha256"].items():
        actual = sha256(OUTPUT_DIR / filename)
        hash_checks[filename] = {"expected": expected, "actual": actual, "status": "PASS" if actual == expected else "FAIL"}
    q4_pass = (
        q4_checks["favorable_counts_match"]
        and q4_checks["applicability_status_match"]
        and q4_checks["hard_feasibility_match"]
        and q4_checks["objective_max_abs_difference"] <= 1e-12
        and q4_checks["selected_candidate_match"]
        and q4_checks["feasible_count_recomputed"] == q4_checks["feasible_count_saved"]
        and q4_checks["synthetic_check_saved"] == "PASS"
    )
    result = {
        "q2": {
            "checks": q2_checks,
            "pass_count": sum(row["status"] == "PASS" for row in q2_checks),
            "total": len(q2_checks),
            "status": "PASS" if all(row["status"] == "PASS" for row in q2_checks) else "FAIL",
        },
        "q3": {
            "checks": q3_checks,
            "pass_count": sum(row["status"] == "PASS" for row in q3_checks),
            "total": len(q3_checks),
            "status": "PASS" if all(row["status"] == "PASS" for row in q3_checks) else "FAIL",
        },
        "q4": {"checks": q4_checks, "status": "PASS" if q4_pass else "FAIL"},
        "hashes": {
            "checks": hash_checks,
            "status": "PASS" if all(row["status"] == "PASS" for row in hash_checks.values()) else "FAIL",
        },
    }
    result["overall_status"] = (
        "PASS"
        if all(result[section]["status"] == "PASS" for section in ["q2", "q3", "q4", "hashes"])
        else "FAIL"
    )
    (OUTPUT_DIR / "independent-audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: result[k]["status"] for k in ["q2", "q3", "q4", "hashes"]} | {"overall": result["overall_status"]}, indent=2))


if __name__ == "__main__":
    main()
