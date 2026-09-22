"""Artifact-level integration checks for the 2021D graduation run."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


RUN_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = RUN_ROOT / "outputs"


def load(name: str):
    return json.loads((OUTPUTS / name).read_text(encoding="utf-8"))


def test_feature_selection_is_bounded_stable_and_fold_recorded():
    q2 = load("q2-results.json")
    folds = load("fold-ids-q2.json")
    assert len(q2["final_selected_features"]) == 20
    assert all(len(features) == 20 for features in q2["feature_stability"]["fold_selected_features"])
    assert q2["feature_stability"]["pairwise_jaccard_mean"] > 0.5
    assert len(folds) == 5
    validation_ids = [identifier for fold in folds for identifier in fold["validation_ids"]]
    assert len(validation_ids) == len(set(validation_ids)) == 1974


def test_classification_endpoints_keep_separate_metrics_and_thresholds():
    q3 = load("q3-results.json")
    required = {
        "roc_auc_mean",
        "pr_auc_mean",
        "balanced_accuracy_mean",
        "recall_mean",
        "precision_mean",
        "f1_mean",
        "specificity_mean",
        "brier_mean",
    }
    assert set(q3) == {"Caco-2", "CYP3A4", "hERG", "HOB", "MN"}
    for endpoint, result in q3.items():
        selected = result["selected_model"]
        selected_summary = next(row for row in result["summary"] if row["model"] == selected)
        assert required <= set(selected_summary)
        assert result["final_threshold_provenance"].startswith("5-fold out-of-fold")
        assert 0 < result["final_threshold"] < 1
        assert sum(result["class_counts"].values()) == 1974


def test_optimization_gates_precede_objective_and_synthetic_check_passes():
    q4 = load("q4-results.json")
    candidates = pd.read_csv(OUTPUTS / "candidate-ledger.csv")
    assert q4["synthetic_optimization_check"]["status"] == "PASS"
    assert q4["search_budget"]["evaluated_candidates"] == 50
    assert q4["feasible_candidate_count"] == int(candidates["hard_feasibility"].sum())
    selected = candidates[candidates["candidate_id"] == q4["selected_candidate"]].iloc[0]
    assert bool(selected["hard_feasibility"])
    assert selected["applicability_domain_status"] == "PASS"
    assert selected["favorable_count_primary"] >= 3
    assert selected["final_disposition"] == "SELECTED_SURROGATE_BEST"


def test_cross_task_outputs_align_and_independent_audit_passes():
    q2 = pd.read_csv(OUTPUTS / "q2-test-predictions.csv")
    q3 = pd.read_csv(OUTPUTS / "q3-test-predictions.csv")
    candidates = pd.read_csv(OUTPUTS / "candidate-ledger.csv")
    assert q2["candidate_id"].tolist() == q3["candidate_id"].tolist() == candidates["candidate_id"].tolist()
    assert q2["SMILES"].tolist() == q3["SMILES"].tolist() == candidates["SMILES"].tolist()
    assert load("independent-audit.json")["overall_status"] == "PASS"


def test_required_narrative_artifacts_and_completion_gate_exist():
    required = [
        "problem-facts.md",
        "data-ledger.md",
        "entity-alignment.md",
        "q1-feature-analysis.md",
        "q2-activity-model.md",
        "q2-results.md",
        "q3-admet-models.md",
        "q3-results.md",
        "q4-optimization-model.md",
        "q4-results.md",
        "candidate-ledger.md",
        "validation.md",
        "independent-audit.md",
        "reviewer-report.md",
        "REPORT.md",
        "completion.json",
    ]
    assert all((RUN_ROOT / name).is_file() for name in required)
    completion = json.loads((RUN_ROOT / "completion.json").read_text(encoding="utf-8"))
    assert completion["completion_marker"] == "TENTH_PROBLEM_GRADUATION_BLIND_RUN_COMPLETE"
    assert completion["final_result_status"] == "VALID"
    assert completion["failure_level"] == "NONE"
    assert completion["graduation_verdict"] == "PASS"
