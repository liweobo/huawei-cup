"""Behavioral regression tests for generic intervention association analysis."""

from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import pytest

from skill.scripts.association_analysis import (
    AssociationAnalysisError, apply_association_gate, association_scope_errors,
    audit_exposures, build_association_contract, fit_crude_adjusted_association,
    propensity_diagnostics, require_association_contract, review_association_claim,
    validate_association_contract,
)
from skill.scripts.group_validation import assert_group_independence, group_cv_splits, group_structure_contract
from skill.scripts.runtime_provenance import apply_temporal_gate, validate_experiment_record, validate_paper_claim
from skill.scripts.temporal_availability import validate_temporal_availability


def data_example(n=160, repeats=1, seed=12):
    rng = np.random.default_rng(seed)
    severity = rng.normal(size=n)
    action = rng.binomial(1, 1 / (1 + np.exp(-1.8 * severity)))
    noise = rng.normal(scale=.35, size=n)
    entity = pd.DataFrame({"asset_id": np.arange(n), "severity": severity, "action": action,
                           "response": 4 * severity + noise})
    frame = entity.loc[entity.index.repeat(repeats)].reset_index(drop=True)
    frame["time"] = np.tile(np.arange(repeats, dtype=float), n)
    frame["response"] += .2 * frame["time"]
    return frame


def contract_for(frame, **overrides):
    settings = {
        "exposure": "action", "outcome": "response", "assignment_type": "OBSERVATIONAL",
        "exposure_time_known": True,
        "candidate_confounders": [{"name": "severity", "temporal_role": "PRE_EXPOSURE",
                                    "evidence": "condition recorded before maintenance assignment",
                                    "available_at": -1, "exposure_at": 0}],
        "post_exposure_variables": ["repair_response", "later_measurement"],
        "group_structure": group_structure_contract(frame, entity_key="asset_id", validation_unit="ENTITY"),
        "temporal_structure": {"status": "PASS", "purpose": "RETROSPECTIVE_ASSOCIATION",
                               "evidence": "measurement-time coordinates and pre-assignment records",
                               "future_information_used": False},
        "estimand": "between-action-group conditional mean response contrast",
        "claim_level": "ADJUSTED_ASSOCIATION",
    }
    settings.update(overrides)
    return build_association_contract(**settings)


def record_example():
    protocol = {"association_analysis": True, "model": "prespecified linear association"}
    return {"experiment_id": "synthetic", "run_id": "association-tests", "created_at": "2026-09-14",
            "problem": "generic", "question": "association", "status": "OBSERVED",
            "updated_by_workflow": "validate_model", "planned_protocol": protocol,
            "executed_protocol": copy.deepcopy(protocol), "protocol_changed": False,
            "change_reason": "", "comparable_to_original_plan": True, "input_artifacts": ["input"],
            "code_artifacts": ["code"], "output_artifacts": ["output"], "random_seed": 12,
            "metrics": {}, "evidence_ids": ["evidence"]}


def identification():
    return {"strategy": "RANDOMIZED_ASSIGNMENT", "review_status": "VERIFIED",
            "evidence_refs": ["randomization-log", "outcome-followup-audit"],
            "assumptions": ["verified assignment contrast, outcome followup, no interference"],
            "randomization_verified": True, "temporal_order_verified": True}


@pytest.mark.parametrize("assignment", ["OBSERVATIONAL", "UNKNOWN", "RANDOMIZED"])
def test_assignment_label_alone_is_not_causal_identification(assignment):
    contract = contract_for(data_example(), assignment_type=assignment, claim_level="CAUSAL_EFFECT")
    with pytest.raises(AssociationAnalysisError, match="UNSUPPORTED_CAUSAL_CLAIM"):
        require_association_contract(contract)


def test_verified_randomized_design_may_permit_causal_interpretation():
    contract = contract_for(data_example(), assignment_type="RANDOMIZED", claim_level="CAUSAL_EFFECT",
                            causal_identification=identification())
    assert require_association_contract(contract)["status"] == "PASS"
    assert review_association_claim("The intervention caused a reduction.", contract)["status"] == "PASS"
    contract["causal_identification"]["randomization_verified"] = False
    assert review_association_claim("The intervention caused a reduction.", contract)["status"] == "INVALIDATED"


def test_propensity_software_success_is_not_an_identification_design():
    evidence = identification()
    evidence["strategy"] = "IPTW"
    contract = contract_for(data_example(), claim_level="CAUSAL_EFFECT", causal_identification=evidence)
    assert "CAUSAL_EFFECT" not in contract["allowed_claim_levels"]


@pytest.mark.parametrize("name,role,expected", [
    ("repair_response", "POST_EXPOSURE", "POST_EXPOSURE_ADJUSTMENT"),
    ("first_measurement", "UNKNOWN", "CONFOUNDER_TIME_UNVERIFIED"),
    ("response", "PRE_EXPOSURE", "OUTCOME_LEAKAGE"),
])
def test_post_exposure_and_unknown_variables_are_not_ordinary_confounders(name, role, expected):
    contract = contract_for(data_example(), candidate_confounders=[
        {"name": name, "temporal_role": role, "evidence": "recorded in the source table"}])
    with pytest.raises(AssociationAnalysisError, match=expected):
        require_association_contract(contract, adjustment_variables=[name])


def test_timestamps_override_an_incorrect_pre_exposure_label():
    contract = contract_for(data_example())
    contract["candidate_confounders"][0]["available_at"] = 2
    with pytest.raises(AssociationAnalysisError, match="FUTURE_INFORMATION_LEAKAGE"):
        require_association_contract(contract, adjustment_variables=["severity"])


def test_unknown_exposure_timing_allows_association_only_even_if_randomized():
    frame = data_example(repeats=3)
    contract = contract_for(frame, exposure_time_known=False)
    result = fit_crude_adjusted_association(frame, contract, adjustment_variables=["severity"],
                                          time_column="time", time_interaction=True)
    assert "EXPOSURE_TIME_UNVERIFIED" in result["warnings"]
    assert result["time_interaction_interpretation"] == "TRAJECTORY_ASSOCIATION"
    contract.update(assignment_type="RANDOMIZED", claim_level="CAUSAL_EFFECT", causal_identification=identification())
    with pytest.raises(AssociationAnalysisError, match="UNSUPPORTED_CAUSAL_CLAIM"):
        require_association_contract(contract)


def test_confounding_by_indication_attenuates_after_severity_adjustment():
    # Maintenance has zero true effect: higher-risk assets are assigned action
    # more often, and severity itself causes the poorer response.
    frame = data_example(n=600)
    result = fit_crude_adjusted_association(frame, contract_for(frame), adjustment_variables=["severity"])
    crude, adjusted = result["comparison"]["action"]["crude"], result["comparison"]["action"]["adjusted"]
    assert crude > 3
    assert abs(adjusted) < .1 and abs(adjusted) < abs(crude) / 20
    assert result["causal_identification_established_by_model"] is False
    assert review_association_claim("维修措施与较差的结果相关，调整初始严重程度后关联明显减弱。", contract_for(frame))["status"] == "PASS"
    assert review_association_claim("干预导致结果更差。", contract_for(frame))["status"] == "INVALIDATED"


def test_crude_and_adjusted_share_the_same_complete_case_sample():
    frame = data_example()
    frame.loc[[0, 1, 2], "severity"] = np.nan
    result = fit_crude_adjusted_association(frame, contract_for(frame), adjustment_variables=["severity"])
    assert result["crude"]["n_rows"] == result["adjusted"]["n_rows"] == len(frame) - 3
    assert result["scope"]["dropped_row_ids"] == [0, 1, 2]


def test_exposure_audit_counts_entities_and_preserves_missing_values():
    frame = data_example(n=80, repeats=4)
    frame["action"] = (frame["asset_id"] < 3).astype(float)
    frame.loc[frame["asset_id"] == 79, "action"] = np.nan
    report = audit_exposures(frame, ["action"], outcome="response", baseline_variables=["severity"], entity_key="asset_id")
    exposure = report["exposures"]["action"]
    assert (report["n_entities"], report["n_rows"]) == (80, 320)
    assert (exposure["treated_n"], exposure["untreated_n"], exposure["missing_exposure_n"]) == (3, 76, 1)
    assert exposure["status"] == "ESTIMATE_UNSTABLE"
    assert exposure["outcome"]["treated"]["n"] == 3
    assert "standardized_mean_difference" in exposure["baseline"]["severity"]


def test_cooccurrence_and_high_correlation_use_entity_counts():
    frame = data_example(n=80, repeats=3)
    frame["policy"] = frame["action"]
    audit = audit_exposures(frame, ["action", "policy"], outcome="response", entity_key="asset_id")
    pair = audit["cooccurrence"][0]
    assert pair["complete_entity_n"] == 80
    assert pair["both_exposed_n"] == frame.drop_duplicates("asset_id")["action"].sum()
    assert pair["phi"] == pytest.approx(1) and pair["highly_correlated"]
    contract = contract_for(frame, exposure=["action", "policy"])
    with pytest.raises(AssociationAnalysisError, match="NOT_IDENTIFIED"):
        fit_crude_adjusted_association(frame, contract, adjustment_variables=["severity"])


def test_time_varying_exposures_cannot_be_silently_flattened():
    frame = data_example(n=80, repeats=3)
    frame.loc[0, "action"] = 1 - frame.loc[0, "action"]
    with pytest.raises(AssociationAnalysisError, match="TIME_VARYING_EXPOSURE"):
        audit_exposures(frame, ["action"], outcome="response", entity_key="asset_id")


def test_propensity_overlap_failure_prevents_weighted_association_claim():
    frame = data_example()
    scores = np.where(frame["action"] == 1, .8, .2)
    audit = propensity_diagnostics(frame, contract_for(frame), scores, covariates=["severity"])
    assert "PROPENSITY_OVERLAP_FAILURE" in audit["errors"]
    assert not audit["eligible_for_weighted_association"]
    assert not audit["causal_identification_established"]
    assert audit["balance"]["severity"]["before_smd"] == pytest.approx(audit["balance"]["severity"]["after_smd"])


def test_extreme_iptw_weights_have_ess_and_balance_diagnostics():
    frame = data_example()
    scores = np.full(len(frame), .5)
    scores[np.flatnonzero(frame["action"] == 1)[0]] = .001
    audit = propensity_diagnostics(frame, contract_for(frame), scores, covariates=["severity"])
    assert audit["max_weight"] == pytest.approx(1000)
    assert "EXTREME_IPTW_WEIGHTS" in audit["warnings"]
    assert audit["effective_sample_size"]["treated"] < 10
    assert "after_smd" in audit["balance"]["severity"]


def test_balanced_overlap_is_not_automatically_a_causal_effect():
    frame = pd.DataFrame({"asset_id": range(80), "severity": np.tile([-1, 1, -1, 1], 20),
                          "action": np.tile([0, 0, 1, 1], 20), "response": np.arange(80)})
    audit = propensity_diagnostics(frame, contract_for(frame), np.full(80, .5), covariates=["severity"])
    assert audit["status"] == "PASS" and audit["eligible_for_weighted_association"]
    assert audit["effective_sample_size"]["total"] == pytest.approx(80)
    assert audit["causal_identification_established"] is False


@pytest.mark.parametrize("score", [0, 1])
def test_exact_propensity_boundaries_fail_positivity(score):
    frame = data_example()
    audit = propensity_diagnostics(frame, contract_for(frame), np.full(len(frame), score), covariates=["severity"])
    assert audit["errors"] == ["POSITIVITY_FAILURE"]


@pytest.mark.parametrize("variable", ["response", "later_measurement"])
def test_propensity_never_uses_outcome_or_future_features(variable):
    frame = data_example()
    frame["later_measurement"] = frame["response"] + 1
    with pytest.raises(AssociationAnalysisError, match="OUTCOME_LEAKAGE|POST_EXPOSURE_ADJUSTMENT"):
        propensity_diagnostics(frame, contract_for(frame), np.full(len(frame), .5), covariates=[variable])


def test_longitudinal_fit_uses_clustered_uncertainty_and_group_cv_is_still_separate():
    frame = data_example(n=120, repeats=6)
    contract = contract_for(frame)
    result = fit_crude_adjusted_association(frame, contract, adjustment_variables=["severity"], time_column="time")
    estimate = result["adjusted"]
    assert estimate["n_entities"] == 120 and estimate["n_rows"] == 720
    assert estimate["uncertainty_unit"] == "ENTITY" and estimate["df"] == 119
    assert estimate["fit_residual_scope"] == "FIT_RESIDUAL"
    assert not estimate["predictive_validation_performed"]
    x = np.c_[np.ones(len(frame)), frame[["time", "action", "severity"]]]
    beta = np.linalg.lstsq(x, frame["response"], rcond=None)[0]
    iid_covariance = np.linalg.inv(x.T @ x) * np.sum((frame["response"] - x @ beta) ** 2) / (len(frame) - x.shape[1])
    assert estimate["coefficients"]["action"]["se"] > 2 * np.sqrt(iid_covariance[2, 2])
    splits = group_cv_splits(frame, frame["asset_id"], n_splits=5, prediction_setting="NEW_ENTITY")
    for train, valid in splits:
        assert assert_group_independence(frame.iloc[train]["asset_id"], frame.iloc[valid]["asset_id"])["overlap_count"] == 0
    bad_scope = {**result["scope"], "dependence_handling": "INDEPENDENT_ROWS"}
    assert any("PSEUDOREPLICATION" in error for error in association_scope_errors(contract, bad_scope))


def test_temporal_and_association_failures_are_preserved_independently():
    frame = data_example(repeats=3)
    contract = contract_for(frame)
    result = fit_crude_adjusted_association(frame, contract, adjustment_variables=["severity"], time_column="time")
    time_gate = validate_temporal_availability([0, 3], cutoff=1, target_time=2)
    record = apply_temporal_gate(record_example(), time_gate, future_rows_entered_aggregation=True)
    contract["claim_level"] = "CAUSAL_EFFECT"
    scope = {**result["scope"], "claim_level": "CAUSAL_EFFECT"}
    invalid = apply_association_gate(record, contract, scope)
    assert invalid["status"] == "INVALIDATED"
    assert "FUTURE_INFORMATION_LEAKAGE" in invalid["invalidation_reason"]
    assert "UNSUPPORTED_CAUSAL_CLAIM" in invalid["invalidation_reason"]


@pytest.mark.parametrize("text", [
    "治疗导致水肿减轻。", "治疗使得结果改善。", "该治疗有效降低结局指标。", "该治疗增加风险。",
    "The intervention caused lower losses.", "The policy reduces risk.", "Matching established a causal effect.",
])
def test_reviewer_rejects_unsupported_causal_language(text):
    result = review_association_claim(text, contract_for(data_example()))
    assert result["status"] == "INVALIDATED"
    assert result["findings"][0]["code"] == "UNSUPPORTED_CAUSAL_CLAIM"


@pytest.mark.parametrize("text", [
    "治疗与较小的结局值相关。", "调整后仍观察到轨迹差异，但不能证明治疗导致变化。",
    "Action is associated with outcome; this is not a causal effect.",
    "We cannot conclude that the policy caused the difference.",
])
def test_reviewer_accepts_association_language_and_negated_causal_claims(text):
    assert review_association_claim(text, contract_for(data_example()))["status"] == "PASS"


def test_experiment_and_paper_gates_recheck_the_new_contract():
    frame = data_example()
    contract = contract_for(frame)
    fitted = fit_crude_adjusted_association(frame, contract, adjustment_variables=["severity"])
    missing = validate_experiment_record(record_example())
    assert any("association_contract" in item for item in missing)
    record = apply_association_gate(record_example(), contract, fitted["scope"])
    assert validate_experiment_record(record) == []
    record["association_scope"]["adjustment_variables"] = ["repair_response"]
    record["association_scope"]["gate_status"] = "PASS"
    assert any("POST_EXPOSURE_ADJUSTMENT" in item for item in validate_experiment_record(record))
    claim = {"question": "association", "text": "干预导致损失下降。", "association_contract": contract,
             "evidence_ref": {"run_id": "association-tests", "experiment_id": "synthetic",
                              "artifact": "output", "json_path": "$.adjusted"}}
    active = {"active_evidence_set": {"association": {"run_id": "association-tests", "experiment_id": "synthetic"}}}
    assert "UNSUPPORTED_CAUSAL_CLAIM" in validate_paper_claim(claim, active, "association-tests")


def test_joint_measurement_is_never_an_ordinary_confounder():
    frame = data_example()
    frame["measurement"] = np.random.default_rng(4).normal(size=len(frame))
    joint = [{"name": "measurement", "role": "JOINT_ASSOCIATION_VARIABLE",
              "availability": "AT_OR_BEFORE_OUTCOME", "evidence": "matched concurrent observation"}]
    contract = contract_for(frame, joint_variables=joint)
    result = fit_crude_adjusted_association(frame, contract, adjustment_variables=["severity"])
    assert "measurement" in result["adjusted"]["coefficients"]
    assert any("JOINT_CONDITIONING_ONLY" in item for item in result["warnings"])
    with pytest.raises(AssociationAnalysisError, match="confounder"):
        require_association_contract(contract, adjustment_variables=["severity", "measurement"])


def test_derived_outcome_cannot_enter_propensity_even_with_a_pre_label():
    frame = data_example()
    contract = contract_for(frame, candidate_confounders=[{
        "name": "hidden_target_copy", "temporal_role": "PRE_EXPOSURE", "evidence": "misleading label",
        "derived_from": ["response"],
    }])
    with pytest.raises(AssociationAnalysisError, match="OUTCOME_LEAKAGE"):
        require_association_contract(contract, propensity_features=["hidden_target_copy"])


def test_empty_adjustment_cannot_produce_an_adjusted_association():
    frame = data_example()
    with pytest.raises(AssociationAnalysisError):
        fit_crude_adjusted_association(frame, contract_for(frame), adjustment_variables=[])


@pytest.mark.parametrize("broken", [None, "PASS", {"group_structure": None}])
def test_malformed_contract_is_reported_instead_of_crashing_the_record_validator(broken):
    record = record_example()
    record.update(association_contract=broken, association_scope="PASS")
    assert validate_experiment_record(record)


def test_forged_row_ids_do_not_become_independent_entities():
    frame = data_example(n=80, repeats=3)
    contract = contract_for(frame)
    result = fit_crude_adjusted_association(frame, contract, adjustment_variables=["severity"], time_column="time")
    scope = copy.deepcopy(result["scope"])
    scope.update(analyzed_entity_ids=list(range(len(frame))), n_entities=len(frame))
    assert any("substitute row IDs" in error for error in association_scope_errors(contract, scope))


def test_independent_rows_do_not_require_a_grouped_model_or_cv():
    frame = data_example().drop(columns=["asset_id", "time"])
    structure = group_structure_contract(frame)
    contract = build_association_contract(exposure="action", outcome="response", assignment_type="OBSERVATIONAL",
        group_structure=structure, temporal_structure={"status": "PASS", "purpose": "STATIC_ASSOCIATION", "evidence": "independent records"},
        candidate_confounders=[{"name": "severity", "temporal_role": "PRE_EXPOSURE", "evidence": "recorded before action"}],
        estimand="between-action mean contrast", claim_level="ADJUSTED_ASSOCIATION")
    result = fit_crude_adjusted_association(frame, contract, adjustment_variables=["severity"])
    assert result["adjusted"]["uncertainty_unit"] == "ROW"
    assert result["adjusted"]["covariance"] == "HC1"


def test_paper_gate_requires_the_actual_sentence_and_keeps_independent_failures():
    contract = contract_for(data_example())
    errors = validate_paper_claim({"association_contract": contract}, {}, "run")
    assert any("CLAIM_TEXT_REQUIRED" in error for error in errors)
    errors = validate_paper_claim({"association_contract": contract, "text": "治疗导致改善。"}, {}, "run")
    assert "UNSUPPORTED_CAUSAL_CLAIM" in errors
    assert "paper claim requires structured evidence_ref" in errors
