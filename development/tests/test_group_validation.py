"""Generic regressions for repeated-entity and group-aware validation."""

from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from skill.scripts.group_validation import (
    GroupValidationError,
    assert_group_independence,
    audit_group_cv_splits,
    error_scope_report,
    group_cv_evaluate,
    group_cv_splits,
    group_structure_contract,
    review_group_validation,
    validate_bootstrap_scope,
    validate_group_cv_feasibility,
    validate_group_cv_splits,
    validate_unsupervised_scope,
)
from skill.scripts.metrics import regression_metrics
from skill.scripts.runtime_provenance import (
    apply_group_gate, apply_temporal_gate, observed_result_errors, validate_experiment_record,
)
from skill.scripts.temporal_availability import (
    TemporalAvailabilityError, assert_temporal_aggregation_input, filter_before_aggregation,
    validate_temporal_availability,
)


def test_repeated_entity_structure_is_detected_and_requires_confirmation() -> None:
    frame = pd.DataFrame({"patient_id": ["a", "a", "b"], "value": [1, 2, 3]})
    contract = group_structure_contract(frame)
    assert contract["status"] == "UNVERIFIED"
    assert contract["validation_unit"] == "UNVERIFIED"
    assert "patient_id" in contract["candidate_entity_keys"]
    assert contract["n_entities"] == 2
    assert contract["n_rows"] == 3
    confirmed = group_structure_contract(frame, entity_key="patient_id", prediction_setting="NEW_ENTITY")
    assert confirmed["status"] == "PASS"
    assert confirmed["validation_unit"] == "ENTITY"
    assert confirmed["n_entities"] == 2
    assert confirmed["repeated_entities"] == 1
    assert confirmed["pseudoreplication_risk"] is True


def test_basic_group_overlap_is_a_hard_failure() -> None:
    with pytest.raises(GroupValidationError, match="GROUP_LEAKAGE"):
        assert_group_independence(["a", "b"], ["b", "c"])


def test_valid_group_cv_has_zero_entity_overlap() -> None:
    groups = ["a", "a", "b", "b", "c", "c"]
    splits = group_cv_splits(np.zeros((6, 1)), groups, n_splits=3)
    report = validate_group_cv_splits(splits, groups)
    assert report["status"] == "PASS"
    assert report["overlap_count"] == 0
    assert all(fold["overlap_count"] == 0 for fold in report["folds"])


def test_group_cv_is_more_conservative_than_row_random_for_entity_signal() -> None:
    rng = np.random.default_rng(7)
    n_groups, rows_per_group = 30, 3
    group_values = np.repeat(np.arange(n_groups), rows_per_group)
    group_labels = rng.integers(0, 2, size=n_groups)
    y = group_labels[group_values]
    X = pd.DataFrame({"entity_code": group_values + rng.normal(0, 0.01, len(group_values))})
    model = KNeighborsClassifier(n_neighbors=1)
    row_splits = list(KFold(5, shuffle=True, random_state=42).split(X))
    group_splits = group_cv_splits(X, group_values, y=y, n_splits=5)

    def score(splits):
        values = []
        for train, test in splits:
            fitted = model.fit(X.iloc[train], y[train])
            values.append(accuracy_score(y[test], fitted.predict(X.iloc[test])))
        return float(np.mean(values))

    row_score = score(row_splits)
    group_score = score(group_splits)
    assert row_score > group_score + 0.2
    diagnostic = audit_group_cv_splits(row_splits, group_values)
    assert diagnostic["validation_result_status"] == "INVALIDATED"
    assert diagnostic["violations"] == ["GROUP_LEAKAGE"]
    assert validate_group_cv_splits(group_splits, group_values)["validation_result_status"] == "VALIDATED"


def test_group_classification_preserves_groups_before_stratification() -> None:
    groups = np.repeat(np.arange(12), 2)
    y = np.repeat([0, 1] * 6, 2)
    splits = group_cv_splits(np.zeros((len(groups), 1)), groups, y=y, n_splits=4, stratified=True)
    report = validate_group_cv_splits(splits, groups)
    assert report["overlap_count"] == 0
    feasibility = validate_group_cv_feasibility(groups, y=y, n_splits=4, stratified=True)
    assert feasibility["stratification_status"] == "STRATIFIED_GROUP_FEASIBLE"


def test_group_count_feasibility_fails_before_splitter() -> None:
    with pytest.raises(GroupValidationError, match="FOLD_INFEASIBLE"):
        group_cv_splits(np.zeros((8, 1)), np.repeat(["a", "b", "c", "d"], 2), n_splits=5)


def test_unsupervised_preprocessing_must_be_fitted_inside_fold() -> None:
    with pytest.raises(GroupValidationError, match="UNSUPERVISED_PREPROCESSING_LEAKAGE"):
        validate_unsupervised_scope(fitted_inside_fold=False, operation="PCA")
    assert validate_unsupervised_scope(fitted_inside_fold=True, operation="clustering")["status"] == "UNVERIFIED"
    assert validate_unsupervised_scope(operation="clustering", fit_row_ids=[0, 1],
                                       train_row_ids=[0, 1], validation_row_ids=[2, 3])["status"] == "PASS"


def test_repeated_entity_bootstrap_uses_entity_unit() -> None:
    with pytest.raises(GroupValidationError, match="ROW_BOOTSTRAP_DEPENDENCE"):
        validate_bootstrap_scope("ROW", repeated_entities=True)
    report = validate_bootstrap_scope("ENTITY", repeated_entities=True)
    assert report["status"] == "PASS"
    assert report["independent_uncertainty_estimate"] is True


def test_entity_aggregate_can_use_entity_as_explicit_analysis_unit() -> None:
    frame = pd.DataFrame({"entity_id": ["a", "b", "c"], "peak": [1.0, 2.0, 3.0]})
    contract = group_structure_contract(frame, entity_key="entity_id", prediction_setting="NEW_ENTITY",
        aggregated_from_repeated=True, aggregation_provenance={
            "within_entity_only": True, "temporal_gate_status": "PASS", "learned_preprocessing_scope": "NONE",
        })
    assert contract["status"] == "PASS"
    assert contract["repeated_entities"] == 0
    assert contract["validation_unit"] == "ENTITY"
    assert contract["unit_of_analysis"] == "ENTITY"
    # This is genuinely ordinary row CV, equivalent to entity splitting only
    # because the verified aggregate has exactly one row per entity.
    splits = list(KFold(3).split(frame))
    assert validate_group_cv_splits(splits, frame["entity_id"])["status"] == "PASS"


def test_group_and_temporal_gates_are_independent() -> None:
    frame = pd.DataFrame(
        {"entity": ["a", "a", "b", "b"], "time": [1, 40, 2, 50], "value": [1, 999, 2, 888]}
    )
    filtered, temporal = filter_before_aggregation(
        frame, time_column="time", entity_key="entity", target_time=30
    )
    assert temporal["post_horizon_records"] == 2
    group_report = group_structure_contract(filtered, entity_key="entity", prediction_setting="NEW_ENTITY")
    assert group_report["status"] == "PASS"
    assert group_report["repeated_entities"] == 0


def test_static_independent_rows_can_explicitly_use_row_validation() -> None:
    frame = pd.DataFrame({"x": [1, 2, 3, 4], "label": [0, 1, 0, 1]})
    contract = group_structure_contract(frame)
    assert contract["status"] == "PASS"
    assert contract["validation_unit"] == "ROW"
    splits = group_cv_splits(frame[["x"]], np.arange(4), y=frame["label"], n_splits=2, stratified=True, validation_unit="ROW")
    assert len(splits) == 2


def test_fit_residual_and_validation_error_are_distinct_scopes() -> None:
    report = error_scope_report(fit_residual_count=10, validation_error_count=4)
    assert report["status"] == "PASS"
    assert report["fit_residual"]["scope"] == "FIT_RESIDUAL"
    assert report["validation_error"]["scope"] == "VALIDATION_ERROR"


def test_group_cv_evaluate_records_group_metadata() -> None:
    X = pd.DataFrame({"x": [0.0, 0.1, 1.0, 1.1, 2.0, 2.1]})
    y = np.array([0, 0, 1, 1, 0, 0])
    groups = ["a", "a", "b", "b", "c", "c"]
    result = group_cv_evaluate(
        Ridge(), X, y, groups,
        scorer=lambda true, pred: regression_metrics(true, pred)["RMSE"], n_splits=3,
        group_key="device_key", prediction_setting="NEW_ENTITY",
    )
    assert result["status"] == "PASS"
    assert result["group_validation"]["overlap_count"] == 0
    assert result["group_validation"]["group_key"] == "device_key"
    assert result["split_strategy"] == "GroupKFold"
    assert result["eligible_for_model_selection"] is True


def _record():
    protocol = {"group_validation": True, "validation_unit": "ENTITY"}
    return {
        "experiment_id": "EXP-GROUP", "run_id": "test", "created_at": "2026-09-14T00:00:00Z",
        "problem": "synthetic", "question": "trajectory", "status": "OBSERVED",
        "updated_by_workflow": "validate_model", "planned_protocol": protocol,
        "executed_protocol": copy.deepcopy(protocol), "protocol_changed": False,
        "change_reason": "", "comparable_to_original_plan": True,
        "input_artifacts": ["input"], "code_artifacts": ["code"], "output_artifacts": ["result"],
        "random_seed": 42, "metrics": {"RMSE": 0.1}, "evidence_ids": ["EV-GROUP"],
    }


def test_overlap_invalidates_experiment_and_cannot_be_relabelled_observed():
    groups = ["A", "A", "B", "B"]
    contract = group_structure_contract(groups, entity_key="entity_id", prediction_setting="NEW_ENTITY")
    report = audit_group_cv_splits([([0, 2], [1, 3])], groups, group_key="entity_id", split_strategy="random_80_20_rows")
    invalid = apply_group_gate(_record(), contract, report)
    assert invalid["status"] == "INVALIDATED"
    assert "GROUP_LEAKAGE" in invalid["invalidation_reason"]
    assert validate_experiment_record(invalid) == []
    assert observed_result_errors("validate_model", invalid)
    forged = copy.deepcopy(invalid)
    forged["status"] = "OBSERVED"
    forged["group_scope"]["group_gate_status"] = "PASS"
    forged["group_scope"]["overlap_count"] = 0
    forged["group_scope"]["folds"][0]["overlap_count"] = 0
    assert any("GROUP_LEAKAGE" in error for error in validate_experiment_record(forged))


def test_group_record_requires_actual_folds_and_confirmed_contract():
    assert any("group_structure" in error for error in validate_experiment_record(_record()))
    groups = ["A", "A", "B", "B", "C", "C"]
    contract = group_structure_contract(groups, entity_key="entity_id", prediction_setting="NEW_ENTITY")
    report = audit_group_cv_splits([([0, 1, 2, 3], [4, 5])], groups, group_key="entity_id")
    valid = apply_group_gate(_record(), contract, report)
    assert observed_result_errors("validate_model", valid) == []
    unknown = {**contract, "status": "UNVERIFIED"}
    assert observed_result_errors("validate_model", apply_group_gate(_record(), unknown, report))
    broken = copy.deepcopy(valid)
    del broken["group_scope"]["folds"][0]["validation_group_ids"]
    assert validate_experiment_record(broken)


def test_replacing_entity_ids_with_unique_row_ids_cannot_bypass_record_gate():
    contract = group_structure_contract(["a", "a", "b", "b"], entity_key="entity_id", prediction_setting="NEW_ENTITY")
    disguised = audit_group_cv_splits([([0, 2], [1, 3])], np.arange(4), group_key="entity_id")
    record = apply_group_gate(_record(), contract, disguised)
    assert record["status"] == "INVALIDATED"
    assert "do not substitute row IDs" in record["invalidation_reason"]


def test_preprocessing_fit_ids_checked_against_actual_fold_not_self_authored_metadata():
    groups = ["a", "a", "b", "b"]
    contract = group_structure_contract(groups, entity_key="entity_id", prediction_setting="NEW_ENTITY")
    report = audit_group_cv_splits([([0, 1], [2, 3])], groups, group_key="entity_id")
    report["folds"][0]["preprocessing"] = [{"operation": "PCA", "fit_row_ids": [0, 1, 2, 3],
                                            "train_row_ids": [0, 1, 2, 3], "validation_row_ids": [99], "status": "PASS"}]
    record = apply_group_gate(_record(), contract, report)
    assert record["status"] == "INVALIDATED"
    assert "UNSUPERVISED_PREPROCESSING_LEAKAGE" in record["invalidation_reason"]
    assert validate_experiment_record(record) == []
    assert observed_result_errors("validate_model", record)
    findings = review_group_validation(contract, record["group_scope"])
    assert any(finding["code"] == "UNSUPERVISED_PREPROCESSING_LEAKAGE" for finding in findings)


@pytest.mark.parametrize("scope,unit", [
    ("SAME_ENTITY_RECORD", "ROW"), ("NEW_ENTITY", "ENTITY"),
    ("SAME_ENTITY_FUTURE", "TIME"), ("NEW_ENTITY_FUTURE", "ENTITY_TIME"),
])
def test_four_prediction_settings_are_explicit(scope, unit):
    contract = group_structure_contract(["x", "x", "y", "y"], entity_key="asset_key", prediction_setting=scope)
    assert contract["status"] == "PASS"
    assert contract["validation_unit"] == unit
    assert contract["group_independence_required"] == scope.startswith("NEW_ENTITY")
    assert contract["temporal_gate_required"] == scope.endswith("FUTURE")


def test_repeated_rows_need_scope_and_row_split_is_not_a_backdoor():
    groups = np.repeat(["a", "b"], 6)
    contract = group_structure_contract(groups, entity_key="entity_id")
    assert contract["status"] == "UNVERIFIED"
    assert contract["validation_unit"] != "ROW"
    for options in ({"validation_unit": "ROW"},
                    {"validation_unit": "ROW", "prediction_setting": "NEW_ENTITY"},
                    {"prediction_setting": "INDEPENDENT_ROWS"}):
        with pytest.raises(GroupValidationError, match="SCOPE"):
            group_cv_splits(np.zeros((12, 1)), groups, n_splits=2, **options)
    splits = group_cv_splits(np.zeros((12, 1)), groups, n_splits=2, prediction_setting="SAME_ENTITY_RECORD")
    report = validate_group_cv_splits(splits, groups, prediction_setting="SAME_ENTITY_RECORD")
    assert report["status"] == "PASS"
    assert report["overlap_count"] > 0
    assert report["validation_unit"] == "ROW"


@pytest.mark.parametrize("scope", ["SAME_ENTITY_FUTURE", "NEW_ENTITY_FUTURE"])
def test_plain_group_cv_does_not_claim_to_be_a_temporal_split(scope):
    with pytest.raises(GroupValidationError, match="TEMPORAL_SPLITTER_REQUIRED"):
        group_cv_splits(np.zeros((4, 1)), ["a", "a", "b", "b"], n_splits=2, prediction_setting=scope)


@pytest.mark.parametrize("kind,n_levels", [("binary", 2), ("multiclass", 3), ("ordinal", 4)])
def test_target_types_keep_whole_entities_and_actual_class_coverage(kind, n_levels):
    groups = np.repeat(np.arange(16), n_levels)
    labels = np.tile(np.arange(n_levels), 16)
    splits = group_cv_splits(np.zeros((len(groups), 1)), groups, y=iter(labels), n_splits=4,
                            stratified=True, target_type=kind)
    for train, valid in splits:
        assert not set(groups[train]) & set(groups[valid])
        assert set(labels[train]) == set(labels[valid]) == set(range(n_levels))


def test_stratification_falls_back_without_splitting_rare_class_groups():
    groups = np.repeat(np.arange(8), 3)
    labels = np.repeat([1, 1, 0, 0, 0, 0, 0, 0], 3)
    feasibility = validate_group_cv_feasibility(groups, y=labels, n_splits=4, stratified=True)
    assert feasibility["class_group_counts"]["1"] == 2
    assert feasibility["class_groups"]["1"] == [0, 1]
    assert feasibility["stratification_status"] == "FALLBACK_GROUP_ONLY"
    splits = group_cv_splits(np.zeros((24, 1)), groups, y=labels, n_splits=4, stratified=True)
    assert validate_group_cv_splits(splits, groups)["overlap_count"] == 0
    assert all(set(labels[train]) == {0, 1} for train, _ in splits)


def test_single_group_target_level_rejected_before_sklearn(monkeypatch):
    import skill.scripts.group_validation as module
    monkeypatch.setattr(module, "GroupKFold", lambda *args, **kwargs: pytest.fail("splitter constructed before preflight"))
    with pytest.raises(GroupValidationError, match="CLASS_COVERAGE_INFEASIBLE"):
        group_cv_splits(np.zeros((12, 1)), np.repeat(np.arange(4), 3),
                        y=[1] * 3 + [0] * 9, n_splits=3, stratified=True)
    with pytest.raises(GroupValidationError, match="FOLD_INFEASIBLE"):
        group_cv_splits(np.zeros((8, 1)), np.repeat(np.arange(4), 2), n_splits=5)


@pytest.mark.parametrize("n_splits", [0, 1, 2.5, True, 5])
def test_invalid_fold_count_rejected_by_own_gate(n_splits):
    with pytest.raises(GroupValidationError, match="FOLD_INFEASIBLE"):
        validate_group_cv_feasibility(["a", "a", "b", "c", "d"], n_splits=n_splits)


@pytest.mark.parametrize("bad", [None, np.nan, pd.NA, ""])
def test_unknown_entity_id_cannot_pass(bad):
    contract = group_structure_contract(["a", bad], entity_key="entity_id", prediction_setting="NEW_ENTITY")
    assert contract["status"] == "UNVERIFIED"
    with pytest.raises(GroupValidationError, match="GROUP_KEY_MISSING"):
        assert_group_independence(["a"], [bad])


@pytest.mark.parametrize("indices", [[-1], [4], [0, 0], [0.5], []])
def test_bad_split_indices_fail_closed(indices):
    with pytest.raises(GroupValidationError, match="INVALID_SPLIT_INDEX"):
        validate_group_cv_splits([(indices, [2, 3])], ["a", "a", "b", "b"])


def test_empty_validation_is_not_vacuously_valid():
    with pytest.raises(GroupValidationError, match="EMPTY_VALIDATION"):
        validate_group_cv_splits([], ["a", "b"])


class FitRowsRecorder(TransformerMixin, BaseEstimator):
    fits = []

    def fit(self, X, y=None):
        self.fit_rows_ = X.index.tolist()
        self.fits.append(self.fit_rows_)
        return self

    def transform(self, X):
        return X


def test_complete_unsupervised_pipeline_is_cloned_and_fit_on_training_rows_only():
    rng = np.random.default_rng(4)
    X = pd.DataFrame(rng.normal(size=(40, 4)))
    groups = np.repeat(np.arange(10), 4)
    y = X[0].to_numpy() + rng.normal(size=40)
    FitRowsRecorder.fits.clear()
    model = Pipeline([("trace", FitRowsRecorder()), ("scale", StandardScaler()),
                      ("pca", PCA(n_components=2)), ("model", Ridge())])
    result = group_cv_evaluate(model, X, y, groups, n_splits=5,
                              scorer=lambda a, b: regression_metrics(a, b)["RMSE"])
    assert not hasattr(model["trace"], "fit_rows_")
    for fit_rows, fold in zip(FitRowsRecorder.fits, result["folds"]):
        assert set(fit_rows) == set(fold["train_row_ids"])
        assert validate_unsupervised_scope(operation="scale/PCA", fit_row_ids=fit_rows,
            train_row_ids=fold["train_row_ids"], validation_row_ids=fold["validation_row_ids"])["status"] == "PASS"


@pytest.mark.parametrize("transformer", [PCA(n_components=1), KMeans(n_clusters=2, n_init=1, random_state=3)])
def test_actual_global_unsupervised_fit_fails_but_fold_fit_passes(transformer):
    X = pd.DataFrame({"x": [0.0, 1.0, 2.0, 3.0, 200.0, 300.0], "z": [0, 3, 2, 1, 20, 30]})
    pipeline = Pipeline([("trace", FitRowsRecorder()), ("operation", transformer)])
    pipeline.fit(X)
    with pytest.raises(GroupValidationError, match="UNSUPERVISED_PREPROCESSING_LEAKAGE"):
        validate_unsupervised_scope(operation=type(transformer).__name__,
            fit_row_ids=pipeline["trace"].fit_rows_, train_row_ids=[0, 1, 2, 3], validation_row_ids=[4, 5])
    pipeline.fit(X.iloc[:4])
    assert validate_unsupervised_scope(operation=type(transformer).__name__,
        fit_row_ids=pipeline["trace"].fit_rows_, train_row_ids=[0, 1, 2, 3], validation_row_ids=[4, 5])["status"] == "PASS"


def test_aggregate_uniqueness_does_not_hide_unsafe_source_processing():
    frame = pd.DataFrame({"entity_id": ["a", "b"], "peak": [1, 2]})
    assert group_structure_contract(frame, entity_key="entity_id", prediction_setting="NEW_ENTITY",
                                    aggregated_from_repeated=True)["status"] == "UNVERIFIED"
    for provenance in ({"within_entity_only": False}, {"temporal_gate_status": "FAIL"},
                       {"learned_preprocessing_scope": "ALL_DATA"}):
        with pytest.raises(GroupValidationError, match="LEAKAGE"):
            group_structure_contract(frame, entity_key="entity_id", prediction_setting="NEW_ENTITY",
                                      aggregated_from_repeated=True, aggregation_provenance=provenance)


@pytest.mark.parametrize("group_first", [True, False])
def test_both_leakage_gates_fail_independently_and_preserve_reasons(group_first):
    frame = pd.DataFrame({"entity_id": ["a", "a", "b", "b"], "time": [1, 90, 2, 100], "x": [1, 999, 2, 999]})
    contract = group_structure_contract(frame, entity_key="entity_id", prediction_setting="NEW_ENTITY_FUTURE")
    split = audit_group_cv_splits([([0, 2], [1, 3])], frame["entity_id"], group_key="entity_id",
                                  prediction_setting="NEW_ENTITY_FUTURE")
    temporal = validate_temporal_availability(frame["time"], cutoff=30, target_time=60, time_column="time")
    with pytest.raises(TemporalAvailabilityError, match="FUTURE_INFORMATION_LEAKAGE"):
        assert_temporal_aggregation_input(frame, temporal)
    with pytest.raises(GroupValidationError, match="GROUP_LEAKAGE"):
        validate_group_cv_splits([([0, 2], [1, 3])], frame["entity_id"])
    base = _record()
    if group_first:
        result = apply_temporal_gate(apply_group_gate(base, contract, split), temporal,
                                     future_rows_entered_aggregation=True)
    else:
        result = apply_group_gate(apply_temporal_gate(base, temporal,
                                 future_rows_entered_aggregation=True), contract, split)
    assert result["status"] == "INVALIDATED"
    assert result["group_scope"]["group_gate_status"] == "FAIL"
    assert result["temporal_scope"]["temporal_gate_status"] == "FAIL"
    assert "GROUP_LEAKAGE" in result["invalidation_reason"]
    assert "FUTURE_INFORMATION_LEAKAGE" in result["invalidation_reason"]
    assert validate_experiment_record(result) == []


def test_entity_time_requires_both_gates_even_when_entities_do_not_overlap():
    groups = ["a", "a", "b", "b"]
    contract = group_structure_contract(groups, entity_key="entity_id", prediction_setting="NEW_ENTITY_FUTURE")
    report = audit_group_cv_splits([([0, 1], [2, 3])], groups, group_key="entity_id",
                                  prediction_setting="NEW_ENTITY_FUTURE", split_strategy="heldout_entities_forward")
    assert report["group_gate_status"] == "PASS"
    assert report["validation_result_status"] == "UNVERIFIED"
    record = apply_group_gate(_record(), contract, report)
    assert any("temporal_scope" in error for error in validate_experiment_record(record))
    # A separate time-aware protocol establishes past training / future holdout.
    times = np.array([1, 2, 5, 6])
    assert max(times[:2]) < min(times[2:])
    record = apply_temporal_gate(record, validate_temporal_availability(times[:2], cutoff=2, target_time=5))
    assert validate_experiment_record(record) == []


def test_reviewer_reports_row_leakage_and_pseudoreplication_separately():
    groups = np.repeat(np.arange(100), [5] * 50 + [4] * 50)
    contract = group_structure_contract(groups, entity_key="entity_id", prediction_setting="NEW_ENTITY")
    splits = list(KFold(5, shuffle=True, random_state=42).split(groups))
    report = audit_group_cv_splits(splits, groups, group_key="entity_id", split_strategy="random_rows")
    findings = review_group_validation(contract, report, claimed_independent_n=450,
                                      claimed_generalization=True, error_scope="FIT_RESIDUAL")
    assert {item["code"] for item in findings} == {"GROUP_LEAKAGE", "PSEUDOREPLICATION", "FIT_RESIDUAL_AS_VALIDATION"}
    assert next(item for item in findings if item["code"] == "GROUP_LEAKAGE")["status"] == "INVALIDATED"


def test_iid_column_names_do_not_masquerade_as_entity_keys():
    frame = pd.DataFrame({"humidity": [2, 2, 4, 4], "width": [1, 1, 3, 3], "class": [0, 1, 0, 1]})
    contract = group_structure_contract(frame)
    assert contract["candidate_entity_keys"] == []
    assert contract["validation_unit"] == "ROW"
    assert contract["status"] == "PASS"
