"""Behavioral regressions for feature attribution, including executed synthetic CV."""
from copy import deepcopy

import numpy as np
import pandas as pd
import pytest
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.linear_model import Ridge
from sklearn.model_selection import RepeatedKFold
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error

from skill.scripts.feature_sets import (
    audit_feature_comparison, feature_set_errors, paired_metric_summary,
    apply_feature_set_gate, review_feature_claim, ORDINAL_METRICS, IMBALANCE_METRICS,
    METRIC_DIRECTIONS,
)
from skill.scripts.runtime_provenance import validate_experiment_record, validate_paper_claim


def group(name, columns):
    return dict(name=name, description=f"Measurements from {name}", source=f"sensor/{name}",
        columns_or_builder={"columns": columns}, availability="VERIFIED", temporal_role="BASELINE",
        entity_level="ENTITY", dimension=len(columns), domain_rationale="shared measurement source",
        required_or_optional="OPTIONAL")


def record(selected=("base",), name="B", parent=None, ids=None, folds=None):
    ids = ids or [f"unit{i}" for i in range(20)]
    folds = folds or [dict(fold_id="r1f1", train_ids=ids[:10], validation_ids=ids[10:]),
                      dict(fold_id="r1f2", train_ids=ids[10:], validation_ids=ids[:10])]
    groups = [group("base", ["a", "b", "c"]), group("extra", ["d", "e"]), group("noise", ["n1", "n2"])]
    contract = dict(task="predict response", prediction_setting="NEW_ENTITY", unit_of_analysis="ENTITY", target="y",
        feature_groups=groups, baseline_feature_groups=["base"], candidate_incremental_groups=["extra", "noise"],
        required_groups=[], optional_groups=["base", "extra", "noise"], excluded_groups=[], exclusion_reason={},
        temporal_scope={"status": "NOT_APPLICABLE", "rationale": "static measurements available before response"},
        group_scope={"status": "PASS", "independence_required": True}, selection_method="NONE", selection_scope="NONE",
        comparison_protocol={"planned_candidates": ["B", "BG", "BN", "FULL", "DROP", "ALT"],
            "design_source": "PROBLEM_STRUCTURE", "search_strategy": "PLANNED_SMALL", "selection_validation": "FIXED_CV",
            "rationale": "base state then additional sensor, with noise negative control", "practical_deltas": {"MAE": .05, "RMSE": .05},
            "minimum_consistency": .75}, status="PASS")
    columns = [c for g in groups if g["name"] in selected for c in g["columns_or_builder"]["columns"]]
    scope = dict(feature_set_id=name, feature_groups=list(selected), feature_columns=columns, baseline_feature_set="B",
        incremental_groups=[g for g in selected if g != "base"], removed_groups=[], removals=[], selection_method="NONE",
        selection_scope="NONE", sample_ids=ids, entity_ids=ids.copy(), fold_ids=folds, model_family="Ridge",
        comparison_parent=parent, comparison_reason="preplanned information contrast",
        protocol=dict(target="y", target_definition="measured response", target_values=[0]*len(ids), temporal_cutoff="static",
            random_seeds=[42], model_family="Ridge", hyperparameter_policy={"alpha": 1},
            preprocessing_policy="training pipeline only", metric_definitions={m: {"higher_is_better": False, "definition": m} for m in ("MAE", "RMSE")},
            primary_metric="RMSE", target_type="regression"))
    return dict(status="PLANNED", feature_set_contract=contract, feature_set=scope)


def test_baseline_columns_are_preserved_or_explicitly_removed():
    a, b = record(), record(("base", "extra"), "BG", "B")
    assert audit_feature_comparison(a, b)["status"] == "PASS"
    b["feature_set"]["feature_columns"] = ["a", "d", "e"]
    assert "UNCONTROLLED_FEATURE_SET_COMPARISON" in " ".join(feature_set_errors(b))
    b["feature_set"]["removals"] = [dict(column=c, status="REMOVED_FROM_BASELINE", removal_reason="diagnostic omission") for c in ("b", "c")]
    assert feature_set_errors(b) == []
    assert audit_feature_comparison(a, b)["status"] == "FAIL"  # disclosure does not restore pure increment
    assert audit_feature_comparison(a, b, contrast="composition_diagnostic")["status"] == "PASS"


@pytest.mark.parametrize("change", ["samples", "folds", "model", "target", "seed", "cutoff", "hyperparameters"])
def test_confounded_comparisons_fail(change):
    a, b = record(), record(("base", "extra"), "BG", "B")
    s = b["feature_set"]
    if change == "samples":
        s["sample_ids"] = s["sample_ids"][:-3]
    elif change == "folds":
        s["fold_ids"] = list(reversed(s["fold_ids"]))
    elif change == "model":
        s["protocol"]["model_family"] = s["model_family"] = "Tree"
    else:
        key = {"target": "target_definition", "seed": "random_seeds", "cutoff": "temporal_cutoff", "hyperparameters": "hyperparameter_policy"}[change]
        s["protocol"][key] = "changed"
    checked = audit_feature_comparison(a, b)
    assert checked["status"] == "FAIL"
    assert "UNCONTROLLED_FEATURE_SET_COMPARISON" in " ".join(checked["errors"])


def test_group_mapping_cannot_be_replaced_by_row_ids():
    b = record(("base", "extra"), "BG", "B")
    b["feature_set"]["entity_ids"][10] = b["feature_set"]["entity_ids"][0]
    assert "GROUP_LEAKAGE" in " ".join(feature_set_errors(b))


@pytest.mark.parametrize("method", ["PCA", "LASSO", "CORRELATION", "RFE", "VARIANCE", "MUTUAL_INFORMATION"])
def test_global_feature_selection_never_passes(method):
    b = record()
    for obj in (b["feature_set"], b["feature_set_contract"]):
        obj.update(selection_method=method, selection_scope="ALL_DATA")
    assert apply_feature_set_gate(b)["status"] == "INVALIDATED"
    assert "FEATURE_SELECTION_LEAKAGE" in " ".join(feature_set_errors(b))


def test_future_group_independent_of_better_score():
    b = record(("base", "extra"), "BG", "B")
    b["feature_set_contract"]["temporal_scope"] = {"status": "FAIL"}
    b["metrics"] = {"RMSE": .001}
    assert "FUTURE_INFORMATION_LEAKAGE" in " ".join(feature_set_errors(b))
    b["feature_set_contract"]["temporal_scope"] = {"status": "PASS"}
    b["temporal_scope"] = dict(target_horizon=10, feature_cutoff=11, post_horizon_records_excluded=0, temporal_gate_status="PASS")
    assert feature_set_errors(b)  # cannot self-assert PASS past the actual cutoff


@pytest.mark.parametrize("kind", ["ordinal", "imbalanced"])
def test_existing_metric_system_is_preserved(kind):
    b = record()
    p = b["feature_set"]["protocol"]
    p.update(target_type="ordinal" if kind == "ordinal" else "binary", imbalanced=kind == "imbalanced")
    p["metric_definitions"] = {"Accuracy": {"definition": "accuracy", "higher_is_better": True}}
    p["primary_metric"] = "Accuracy"
    assert feature_set_errors(b)
    names = ORDINAL_METRICS if kind == "ordinal" else IMBALANCE_METRICS
    p["metric_definitions"] = {m: {"definition": m, "higher_is_better": METRIC_DIRECTIONS[m]} for m in names}
    p["primary_metric"] = "MAE" if kind == "ordinal" else "PR-AUC"
    assert not feature_set_errors(b)


def test_unplanned_search_and_outcome_designed_groups_are_reviewed():
    b = record()
    plan = b["feature_set_contract"]["comparison_protocol"]
    plan["search_strategy"] = "POWERSET"
    assert "FEATURE_SET_SEARCH_OVERFIT_RISK" in " ".join(review_feature_claim("model uses features", candidate=b)["findings"])
    plan["search_strategy"] = "PLANNED_SMALL"
    plan["design_source"] = "FULL_DATA_TARGET_ASSOCIATION"
    assert "FEATURE_SELECTION_LEAKAGE" in " ".join(feature_set_errors(b))


def test_provenance_requires_derived_formula_source_and_availability():
    b = record()
    g = b["feature_set_contract"]["feature_groups"][0]
    g["columns_or_builder"]["derived"] = True
    assert "FEATURE_PROVENANCE_INCOMPLETE" in " ".join(feature_set_errors(b))
    g["columns_or_builder"].update(inputs=["raw_a"], formula="documented builder", units="unitless")
    assert not feature_set_errors(b)
    g["availability"] = "UNKNOWN"
    assert feature_set_errors(b)


def test_metric_direction_and_missing_fold_cannot_silently_reverse_claim():
    a = [dict(fold_id=str(i), metrics={"MAE": v}) for i, v in enumerate([1., 2., 1., 2.])]
    b = [dict(fold_id=str(i), metrics={"MAE": v}) for i, v in enumerate([.5, 1.5, .5, 1.5])]
    result = paired_metric_summary(a, b, metric="MAE", higher_is_better=False, practical_delta=.05)
    assert result["mean_delta"] == -.5 and result["status"] == "SUPPORTED_INCREMENTAL_VALUE"
    with pytest.raises(ValueError, match="DIRECTION"):
        paired_metric_summary(a, b, metric="MAE", higher_is_better=True, practical_delta=.05)
    with pytest.raises(ValueError):
        paired_metric_summary(a, b[:-1], metric="MAE", higher_is_better=False, practical_delta=.05)


class RecordFitRows(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        self.fit_ids_ = X.index.tolist()
        return self

    def transform(self, X):
        return X


def test_executed_increment_noise_drop_and_fold_safe_selection():
    rng = np.random.default_rng(23)
    n = 240
    X = pd.DataFrame(rng.normal(size=(n, 7)), columns=["a", "b", "c", "d", "e", "n1", "n2"], index=[f"unit{i}" for i in range(n)])
    y = .3 * X.a + 5 * X.d + rng.normal(0, .3, n)
    splits = list(RepeatedKFold(n_splits=4, n_repeats=2, random_state=42).split(X))
    folds = [dict(fold_id=str(i), train_ids=X.index[t].tolist(), validation_ids=X.index[v].tolist()) for i, (t, v) in enumerate(splits)]
    records = {}
    for name, groups, parent in [("B", ("base",), None), ("BN", ("base", "noise"), "B"), ("BG", ("base", "extra"), "B")]:
        r = record(groups, name, parent, X.index.tolist(), folds)
        for obj in (r["feature_set"], r["feature_set_contract"]):
            obj.update(selection_method="F_REGRESSION", selection_scope="TRAIN_FOLD")
        s = r["feature_set"]
        s["protocol"]["target_values"] = y.tolist()
        s["fit_log"], s["fold_metrics"] = [], []
        for i, (train, valid) in enumerate(splits):
            estimator = Pipeline([("rows", RecordFitRows()), ("select", SelectKBest(f_regression, k=3)), ("reg", Ridge(alpha=1))])
            estimator.fit(X[s["feature_columns"]].iloc[train], y.iloc[train])
            pred = estimator.predict(X[s["feature_columns"]].iloc[valid])
            s["fit_log"].append(dict(fold_id=str(i), scope="TRAIN_FOLD", operation="entire pipeline", fit_ids=estimator.named_steps["rows"].fit_ids_))
            s["fold_metrics"].append(dict(fold_id=str(i), metrics={"MAE": mean_absolute_error(y.iloc[valid], pred), "RMSE": np.sqrt(mean_squared_error(y.iloc[valid], pred))}))
        r["status"] = "OBSERVED"
        assert not feature_set_errors(r)
        records[name] = r
    base, useful, noise = records["B"], records["BG"], records["BN"]
    assert audit_feature_comparison(base, useful)["status"] == "PASS"
    def paired(a, b, contrast="increment"):
        return paired_metric_summary(a["feature_set"]["fold_metrics"], b["feature_set"]["fold_metrics"], metric="RMSE", higher_is_better=False, practical_delta=.05, contrast=contrast)
    evidence = paired(base, useful)
    assert evidence["status"] == "SUPPORTED_INCREMENTAL_VALUE"
    assert paired(base, noise)["status"] == "NO_CLEAR_INCREMENTAL_VALUE"
    assert review_feature_claim("新增噪声组没有明确提升", candidate=noise, parent=base, paired_evidence=paired(base, noise))["status"] == "PASS"
    assert review_feature_claim("added sensor improves prediction", candidate=useful, parent=base, paired_evidence=evidence)["status"] == "PASS"
    dropped = deepcopy(base)
    dropped["feature_set"]["comparison_parent"] = "BG"
    assert audit_feature_comparison(useful, dropped, contrast="drop")["status"] == "PASS"
    assert paired(useful, dropped, "drop")["status"] == "SUPPORTED_CONTRIBUTION"
    contaminated = deepcopy(useful)
    contaminated["feature_set"]["fit_log"][0]["fit_ids"] = X.index.tolist()
    assert "FEATURE_SELECTION_LEAKAGE" in " ".join(feature_set_errors(contaminated))
    fake = dict(evidence, mean_delta=-999)
    assert review_feature_claim("improves prediction", candidate=useful, parent=base, paired_evidence=fake)["status"] == "FAIL"


def test_provenance_integration_does_not_allow_missing_feature_contract():
    errors = validate_experiment_record({"planned_protocol": {"feature_set_comparison": True}})
    assert any("FEATURE_PROVENANCE_INCOMPLETE" in e for e in errors)


def test_static_independent_rows_and_malformed_entity_mapping():
    b = record()
    b["feature_set_contract"].update(prediction_setting="INDEPENDENT_ROWS", unit_of_analysis="ROW")
    b["feature_set_contract"]["group_scope"]["independence_required"] = False
    b["feature_set"].pop("entity_ids")
    assert not feature_set_errors(b)
    b["feature_set_contract"].update(prediction_setting="NEW_ENTITY", unit_of_analysis="ENTITY")
    b["feature_set_contract"]["group_scope"]["independence_required"] = True
    b["feature_set"]["entity_ids"] = ["missing mapping"]
    assert "GROUP_SCOPE_UNVERIFIED" in " ".join(feature_set_errors(b))
    errors = validate_paper_claim({"text": "features improve performance", "feature_set_evidence": {}}, {}, "r")
    assert any("FEATURE_PROVENANCE_INCOMPLETE" in e for e in errors)
