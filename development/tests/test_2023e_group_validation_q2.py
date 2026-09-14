"""Read-only 2023E Q2a and minimal Q2b tests; never run Q2c/Q2d.

Reproduce the targeted evidence with:
python -B development/tests/test_2023e_group_validation_q2.py --output <development-artifacts-dir>
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

PROJECT = Path(__file__).resolve().parents[2]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from skill.scripts.group_validation import (
    GroupValidationError, audit_group_cv_splits, group_cv_splits,
    group_structure_contract, validate_unsupervised_scope,
)
from skill.scripts.metrics import regression_metrics
from skill.scripts.runtime_provenance import apply_group_gate, validate_experiment_record

RAW = PROJECT / "development/benchmarks/problems/2023/E/raw"
BASELINE_SCRIPT = PROJECT / "development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke/run-001/code/clinical_baseline.py"
INPUT_FILES = [
    RAW / "表1-患者列表及临床信息.xlsx",
    RAW / "表2-患者影像信息血肿及水肿的体积及位置.xlsx",
    RAW / "附表1-检索表格-流水号vs时间.xlsx",
]
RUN_ID = "grouped-longitudinal-q2-targeted"


class TimeQuadraticRidge(RegressorMixin, BaseEstimator):
    """The existing Q2 curve, with all centering/scaling fitted in the fold."""

    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha

    def fit(self, X, y):
        self.fit_row_ids_ = X.index.tolist()
        values = X["onset_to_imaging_h"].to_numpy(float)
        self.center_ = float(np.median(values))
        self.scale_ = float(np.std(values) or 1.0)
        z = (values - self.center_) / self.scale_
        self.model_ = Ridge(alpha=self.alpha).fit(np.c_[z, z**2], np.asarray(y, dtype=float))
        return self

    def predict(self, X):
        z = (X["onset_to_imaging_h"].to_numpy(float) - self.center_) / self.scale_
        return self.model_.predict(np.c_[z, z**2])


def _observations():
    spec = importlib.util.spec_from_file_location("historical_q2_readonly", BASELINE_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Import only the source reader/row expansion; do not call q2_curves(),
    # which also executes the out-of-scope treatment association analysis.
    clinical = module.prepare_clinical(pd.read_excel(INPUT_FILES[0], dtype=str))
    lookup, _ = module.make_lookup(pd.read_excel(INPUT_FILES[2], dtype=str))
    longitudinal = module.expand_volume_table(pd.read_excel(INPUT_FILES[1], dtype=str), lookup, clinical)
    ids = set(clinical.head(100)["patient_id"])
    obs = longitudinal[longitudinal["patient_id"].isin(ids)].dropna(
        subset=["onset_to_imaging_h", "ED_volume"]
    ).reset_index(drop=True)
    assert len(obs) == 450 and obs["patient_id"].nunique() == 100
    baseline = obs[obs["visit_index"] == 0]
    assert len(baseline) == 100 and baseline["patient_id"].is_unique
    assert baseline.set_index("patient_id")["onset_to_imaging_h"].sort_index().equals(
        obs.groupby("patient_id")["onset_to_imaging_h"].min().sort_index()
    )
    return obs


def _plain(value):
    def convert(item):
        if isinstance(item, (np.ndarray, pd.Index)):
            return item.tolist()
        if hasattr(item, "item"):
            return item.item()
        raise TypeError(type(item).__name__)
    return json.loads(json.dumps(value, default=convert, allow_nan=False))


def _write(path, value):
    path.write_text(json.dumps(_plain(value), ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def _metrics(true, predicted):
    all_metrics = regression_metrics(true, predicted)
    return {name: all_metrics[name] for name in ("MAE", "RMSE", "R2")}


def _record(experiment, protocol):
    return {
        "experiment_id": experiment, "run_id": RUN_ID,
        "created_at": datetime.now(timezone.utc).isoformat(), "problem": "2023E", "question": "Q2",
        "status": "RUNNING", "updated_by_workflow": "validate_model",
        "planned_protocol": protocol, "executed_protocol": copy.deepcopy(protocol),
        "protocol_changed": False, "change_reason": "", "comparable_to_original_plan": True,
        "input_artifacts": ["clinical-input", "volume-input", "time-lookup-input"],
        "code_artifacts": ["targeted-test-code", "group-gate-code", "experiment-gate-code", "metrics-code", "source-row-expansion"],
        "output_artifacts": [experiment + "-output"], "random_seed": 42,
        "metrics": {}, "evidence_ids": [experiment + "-evidence"],
    }


def _cv_curve(obs, splits, report, *, formal):
    X, y = obs[["onset_to_imaging_h"]], obs["ED_volume"].to_numpy(float)
    predicted, fold_ids = np.empty(len(obs)), np.zeros(len(obs), dtype=int)
    metrics = []
    for fold, (train, valid) in zip(report["folds"], splits):
        model = TimeQuadraticRidge().fit(X.iloc[train], y[train])
        predicted[valid] = model.predict(X.iloc[valid])
        fold_ids[valid] = fold["fold"]
        preprocessing = validate_unsupervised_scope(operation="time_center_scale",
            fit_row_ids=model.fit_row_ids_, train_row_ids=train, validation_row_ids=valid)
        fold["preprocessing"] = [preprocessing]
        fold["metrics"] = _metrics(y[valid], predicted[valid])
        metrics.append(fold["metrics"])
    assert (fold_ids > 0).all()
    result = {
        "status": "OBSERVED" if formal else "INVALIDATED",
        "role": "FORMAL_GROUPED_VALIDATION" if formal else "LEAKAGE_DIAGNOSTIC_ONLY",
        "eligible_for_model_selection": formal, "error_scope": "VALIDATION_ERROR",
        "metric_weighting": "observation-weighted pooled out-of-fold predictions",
        "pooled_metrics": _metrics(y, predicted),
        "fold_metrics": {name: {"mean": float(np.mean([m[name] for m in metrics])),
                                "std": float(np.std([m[name] for m in metrics], ddof=1))}
                         for name in ("MAE", "RMSE", "R2")},
        "fold_variation_is_confidence_interval": False,
        "entity_overlap_per_fold": [fold["overlap_count"] for fold in report["folds"]],
        "group_validation": report,
    }
    rows = obs[["patient_id", "visit_index", "onset_to_imaging_h", "ED_volume"]].copy()
    rows["fold"] = fold_ids
    rows["held_out_prediction"] = predicted
    rows["validation_error"] = y - predicted
    rows["validation_status"] = result["status"]
    return result, rows


def _fit_subgroups(obs, train):
    training = obs.iloc[train]
    baseline = training[training["visit_index"] == 0]
    boundaries = np.quantile(baseline["ED_volume"], [1 / 3, 2 / 3])
    subgroup_by_id = dict(zip(baseline["patient_id"], np.digitize(baseline["ED_volume"], boundaries, right=True)))
    models = {}
    for group_id in range(3):
        members = training[training["patient_id"].map(subgroup_by_id) == group_id]
        assert members["onset_to_imaging_h"].nunique() >= 3
        models[group_id] = TimeQuadraticRidge().fit(members[["onset_to_imaging_h"]], members["ED_volume"])
    return boundaries, models, baseline.index.tolist()


def _q2b_check(obs, splits, report):
    rows, folds = [], []
    for fold, (train, valid) in zip(report["folds"], splits):
        boundaries, models, fit_rows = _fit_subgroups(obs, train)
        provenance = validate_unsupervised_scope(operation="baseline_quantile_subgroup_discovery",
            fit_row_ids=fit_rows, train_row_ids=train, validation_row_ids=valid)
        fold["preprocessing"] = [provenance]
        for group_id, model in models.items():
            fold["preprocessing"].append(validate_unsupervised_scope(operation=f"subgroup_{group_id}_curve_scaling",
                fit_row_ids=model.fit_row_ids_, train_row_ids=train, validation_row_ids=valid))
        validation = obs.iloc[valid]
        baseline = validation[validation["visit_index"] == 0].set_index("patient_id")
        labels = np.digitize(baseline["ED_volume"], boundaries, right=True)
        assignment = dict(zip(baseline.index, labels))
        followup = validation[validation["visit_index"] > 0].copy()
        assert (followup["onset_to_imaging_h"] > followup["patient_id"].map(baseline["onset_to_imaging_h"])).all()
        followup["subgroup"] = followup["patient_id"].map(assignment)
        followup["prediction"] = np.nan
        for group_id, model in models.items():
            selected = followup["subgroup"] == group_id
            if selected.any():
                followup.loc[selected, "prediction"] = model.predict(followup.loc[selected, ["onset_to_imaging_h"]])
        assert np.isfinite(followup["prediction"]).all()
        # This deliberately contaminated fit provenance must fail for every fold.
        try:
            validate_unsupervised_scope(operation="global_baseline_quantiles",
                fit_row_ids=obs[obs["visit_index"] == 0].index, train_row_ids=train, validation_row_ids=valid)
        except GroupValidationError as error:
            assert "UNSUPERVISED_PREPROCESSING_LEAKAGE" in str(error)
        else:
            raise AssertionError("global subgroup discovery was not rejected")
        # Perturb held-out baseline and later outcomes; fitted training subgroup
        # rules and curves must be unchanged, including preprocessing parameters.
        modified = obs.copy()
        modified.loc[valid, "ED_volume"] += 1e8
        other_boundaries, other_models, other_rows = _fit_subgroups(modified, train)
        np.testing.assert_array_equal(boundaries, other_boundaries)
        assert fit_rows == other_rows
        for group_id, model in models.items():
            np.testing.assert_array_equal(model.model_.coef_, other_models[group_id].model_.coef_)
            assert model.model_.intercept_ == other_models[group_id].model_.intercept_
        followup["fold"] = fold["fold"]
        rows.append(followup)
        folds.append({"fold": fold["fold"], "training_entities": fold["train_groups"],
                      "validation_entities": fold["validation_groups"], "overlap_count": fold["overlap_count"],
                      "training_boundaries": boundaries.tolist(), "training_baseline_fit_rows": fit_rows,
                      "validation_followup_rows": len(followup), "global_discovery_rejected": True,
                      "heldout_perturbation_changes_training_fit": False})
    return {
        "status": "PASS", "discovery_scope": "TRAINING_ENTITIES_ONLY",
        "subgroups": 3, "subgroup_count_optimized": False,
        "validation_assignment_features": "each held-out entity's observed baseline only",
        "baseline_feature_cutoff_verified": True,
        "baseline_rows_scored": 0, "validation_followup_rows": sum(len(frame) for frame in rows),
        "folds": folds, "group_validation": report,
    }, pd.concat(rows).sort_index()


def run_targeted(output):
    output = Path(output).resolve()
    if any(output.is_relative_to(PROJECT / area) for area in ("skill", "development/benchmarks")):
        raise ValueError("targeted outputs must not enter Skill or historical evidence")
    output.mkdir(parents=True, exist_ok=True)
    _write(output / "workspace-manifest.json", {
        "run_id": RUN_ID, "active_run_id": RUN_ID, "purpose": "development Q2a/Q2b targeted test",
        "allowed_write_root": str(output), "allowed_read_roots": [str(RAW), str(BASELINE_SCRIPT)],
        "frozen_sources_read_only": True, "clean_room_claim": False,
    })
    obs = _observations()
    structure = group_structure_contract(obs, entity_key="patient_id", prediction_setting="NEW_ENTITY",
                                         task="time_to_outcome_curve", target="ED_volume")
    assert structure["status"] == "PASS" and structure["repeated_entities"] == 100
    X, groups = obs[["onset_to_imaging_h"]], obs["patient_id"].to_numpy()
    row_splits = list(KFold(5, shuffle=True, random_state=42).split(X))
    grouped_splits = group_cv_splits(X, groups, n_splits=5, prediction_setting="NEW_ENTITY")
    row_report = audit_group_cv_splits(row_splits, groups, group_key="patient_id", split_strategy="KFold(shuffle=True,seed=42)")
    group_report = audit_group_cv_splits(grouped_splits, groups, group_key="patient_id", split_strategy="GroupKFold")
    protocol = {
        "group_validation": True, "validation_unit": "ENTITY", "prediction_setting": "NEW_ENTITY",
        "model": "quadratic time-only Ridge", "alpha": 1.0, "features": ["onset_to_imaging_h"],
        "n_splits": 5, "preprocessing": "fold-local median centering and standard-deviation scaling",
        "temporal_scope": "time is the curve coordinate; no future-dependent covariate or longitudinal aggregate",
        "scope_excludes": ["calendar-time forecasting", "treatment effects", "robustness/sensitivity"],
    }
    row_record = apply_group_gate(_record("Q2A-ROW", {**protocol, "split_strategy": "KFold", "diagnostic_only": True}), structure, row_report)
    group_record = apply_group_gate(_record("Q2A-GROUP", {**protocol, "split_strategy": "GroupKFold"}), structure, group_report)
    _write(output / "Q2A-ROW-record.json", row_record)
    _write(output / "Q2A-GROUP-record.json", group_record)
    row_result, row_predictions = _cv_curve(obs, row_splits, row_report, formal=False)
    group_result, group_predictions = _cv_curve(obs, grouped_splits, group_report, formal=True)
    row_record = apply_group_gate(row_record, structure, row_report)
    group_record = apply_group_gate(group_record, structure, group_report)
    row_record["metrics"] = row_result["pooled_metrics"]
    group_record.update(status="OBSERVED", metrics=group_result["pooled_metrics"])
    _write(output / "Q2A-ROW-record.json", row_record)
    _write(output / "Q2A-GROUP-record.json", group_record)

    # Final fitting is a separate operation, after the grouped protocol is run.
    final_record = _record("Q2A-FINAL", {"purpose": "FINAL_FIT", "error_scope": "FIT_RESIDUAL",
        "model_selection_evidence": "Q2A-GROUP-evidence", "fit_scope": "all 100 available training entities",
        "method": "pre-specified quadratic Ridge; no hyperparameter search"})
    _write(output / "Q2A-FINAL-record.json", final_record)
    model = TimeQuadraticRidge().fit(X, obs["ED_volume"])
    final_rows = obs[["patient_id", "onset_to_imaging_h", "ED_volume"]].copy()
    final_rows["fitted"] = model.predict(X)
    final_rows["fit_residual"] = obs["ED_volume"] - final_rows["fitted"]
    final = {
        "purpose": "FINAL_FIT", "error_scope": "FIT_RESIDUAL", "n_entities": 100, "n_rows": 450,
        "eligible_for_model_selection": False,
        "formula": "f(t) = intercept + b1*z + b2*z^2; z=(t-center_h)/scale_h",
        "intercept": model.model_.intercept_, "coefficients": model.model_.coef_,
        "center_h": model.center_, "scale_h": model.scale_,
        "residual_metrics": _metrics(obs["ED_volume"], final_rows["fitted"]),
    }
    final_record.update(status="OBSERVED", metrics=final["residual_metrics"])

    subgroup_report = audit_group_cv_splits(grouped_splits, groups, group_key="patient_id", split_strategy="GroupKFold")
    q2b_record = apply_group_gate(_record("Q2B-SCOPE", {"group_validation": True, "validation_unit": "ENTITY",
        "split_strategy": "GroupKFold", "n_splits": 5, "discovery": "training baseline tertiles",
        "prediction_setting": "NEW_ENTITY", "subgroup_count": 3, "optimize": False}), structure, subgroup_report)
    _write(output / "Q2B-SCOPE-record.json", q2b_record)
    q2b_result, q2b_predictions = _q2b_check(obs, grouped_splits, subgroup_report)
    q2b_record = apply_group_gate(q2b_record, structure, subgroup_report)
    q2b_record["status"] = "OBSERVED"

    difference = {name: group_result["pooled_metrics"][name] - row_result["pooled_metrics"][name]
                  for name in ("MAE", "RMSE", "R2")}
    summary = {
        "run_id": RUN_ID, "group_structure": structure,
        "Q2a": {"row_random": row_result, "patient_grouped": group_result, "final_fit": final,
                "group_minus_row_pooled_metrics": difference,
                "rmse_optimism_fraction": difference["RMSE"] / group_result["pooled_metrics"]["RMSE"],
                "formal_evaluation": "patient_grouped only",
                "volume_scale": "original attachment values, no conversion",
                "comparison_interpretation": "fixed model/features; protocol difference only, not causal attribution or model ranking"},
        "Q2b": q2b_result,
        "remaining_modeling_risks": ["treatment association analysis", "robustness / sensitivity"],
    }
    row_predictions.to_csv(output / "Q2A-ROW-predictions.csv", index=True, index_label="row_id")
    group_predictions.to_csv(output / "Q2A-GROUP-predictions.csv", index=True, index_label="row_id")
    final_rows.to_csv(output / "Q2A-FINAL-residuals.csv", index=True, index_label="row_id")
    q2b_predictions.to_csv(output / "Q2B-SCOPE-predictions.csv", index=True, index_label="row_id")
    for record in (row_record, group_record, final_record, q2b_record):
        errors = validate_experiment_record(record)
        assert errors == [], errors
        _write(output / f"{record['experiment_id']}-record.json", record)
    _write(output / "results.json", summary)
    _write(output / "active-evidence-set.json", {
        "run_id": RUN_ID, "Q2a_validation": "Q2A-GROUP-evidence", "Q2a_fit_residual": "Q2A-FINAL-evidence",
        "Q2b_subgroup_scope": "Q2B-SCOPE-evidence", "excluded_from_selection": ["Q2A-ROW-evidence"],
    })
    paths = dict(zip(("clinical-input", "volume-input", "time-lookup-input"), INPUT_FILES))
    paths.update({"targeted-test-code": Path(__file__), "group-gate-code": PROJECT / "skill/scripts/group_validation.py",
                  "experiment-gate-code": PROJECT / "skill/scripts/runtime_provenance.py",
                  "metrics-code": PROJECT / "skill/scripts/metrics.py",
                  "source-row-expansion": BASELINE_SCRIPT})
    for name in ("workspace-manifest", "results", "active-evidence-set"):
        paths[name] = output / (name + ".json")
    for record in (row_record, group_record, final_record, q2b_record):
        name = record["experiment_id"]
        paths[name + "-output"] = output / (name + "-residuals.csv" if name == "Q2A-FINAL" else name + "-predictions.csv")
        paths[name + "-record"] = output / (name + "-record.json")
    _write(output / "evidence-ledger.json", {
        "run_id": RUN_ID,
        "artifacts": [{"artifact_id": key, "path": str(path.resolve()),
                       "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for key, path in paths.items()],
        "evidence": [{"evidence_id": record["evidence_ids"][0], "experiment_id": record["experiment_id"],
                      "run_id": RUN_ID, "artifact_id": record["output_artifacts"][0], "status": record["status"]}
                     for record in (row_record, group_record, final_record, q2b_record)],
    })
    return _plain(summary)


@pytest.fixture(scope="module")
def targeted(tmp_path_factory):
    output = tmp_path_factory.mktemp("grouped-q2-targeted")
    return run_targeted(output), output


def test_q2a_same_model_row_vs_grouped_and_final_residual_scope(targeted):
    result, output = targeted
    structure = result["group_structure"]
    assert (structure["n_rows"], structure["n_entities"], structure["repeated_entities"]) == (450, 100, 100)
    q2a = result["Q2a"]
    assert all(value > 0 for value in q2a["row_random"]["entity_overlap_per_fold"])
    assert q2a["row_random"]["status"] == "INVALIDATED"
    assert q2a["row_random"]["eligible_for_model_selection"] is False
    assert q2a["patient_grouped"]["entity_overlap_per_fold"] == [0] * 5
    assert all(fold["train_groups"] == 80 and fold["validation_groups"] == 20
               for fold in q2a["patient_grouped"]["group_validation"]["folds"])
    assert q2a["final_fit"]["error_scope"] == "FIT_RESIDUAL"
    assert q2a["patient_grouped"]["error_scope"] == "VALIDATION_ERROR"
    residuals = pd.read_csv(output / "Q2A-FINAL-residuals.csv")
    np.testing.assert_allclose(residuals["fit_residual"], residuals["ED_volume"] - residuals["fitted"])
    print("2023E_Q2A_GROUP_TARGETED=" + json.dumps({key: q2a[key]["pooled_metrics"] for key in ("row_random", "patient_grouped")}))


def test_q2b_training_discovery_and_known_baseline_assignment(targeted):
    result, _ = targeted
    q2b = result["Q2b"]
    assert q2b["status"] == "PASS"
    assert q2b["validation_followup_rows"] == 350
    assert q2b["baseline_rows_scored"] == 0
    for fold in q2b["folds"]:
        assert fold["global_discovery_rejected"] is True
        assert fold["heldout_perturbation_changes_training_fit"] is False
        assert len(fold["training_baseline_fit_rows"]) == 80


def test_targeted_evidence_records_and_hashes_are_traceable(targeted):
    _, output = targeted
    ledger = json.loads((output / "evidence-ledger.json").read_text(encoding="utf-8"))
    for artifact in ledger["artifacts"]:
        assert hashlib.sha256(Path(artifact["path"]).read_bytes()).hexdigest() == artifact["sha256"]
    for path in output.glob("*-record.json"):
        assert validate_experiment_record(json.loads(path.read_text(encoding="utf-8"))) == []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = run_targeted(args.output)
    print(json.dumps({"rows": result["group_structure"]["n_rows"], "entities": result["group_structure"]["n_entities"],
        "row_random": result["Q2a"]["row_random"]["pooled_metrics"],
        "grouped": result["Q2a"]["patient_grouped"]["pooled_metrics"],
        "group_minus_row": result["Q2a"]["group_minus_row_pooled_metrics"],
        "Q2b": result["Q2b"]["status"], "output": str(args.output.resolve())}, indent=2))
