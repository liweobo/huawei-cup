from __future__ import annotations

from copy import deepcopy

from skill.scripts.evaluation_semantics import (
    assess_contract,
    reviewer_codes,
    should_activate,
)


NA_SCOPE = {
    "object": "current alternatives",
    "population": "not applicable",
    "geography": "declared comparison set",
    "time": "current evaluation period",
    "category": "declared alternatives",
}


def base_contract(
    semantics: str = "RELATIVE_SCORE",
    *,
    relation: str = "RELATIVE",
    unit: str = "dimensionless score",
    allowed: list[str] | None = None,
) -> dict:
    return {
        "evaluation_contract": {
            "evaluation_object": "declared decision alternative",
            "decision_question": "compare declared alternatives",
            "output_semantics": semantics,
            "output_method": "weighted normalized score",
            "absolute_or_relative": relation,
            "output_unit": unit,
            "output_scope": deepcopy(NA_SCOPE),
            "comparator": {
                "used": False,
                "value": None,
                "unit": "",
                "provenance": "",
                "source": "",
                "scope": {},
                "version_or_date": "",
            },
            "output_conversion": None,
            "hard_gate": "NONE",
            "allowed_claim": "relative result for the declared comparison set",
            "allowed_claim_semantics": allowed or [semantics],
            "status": "EVALUATION_SEMANTICS_VERIFIED",
        }
    }


def body(contract: dict) -> dict:
    return contract["evaluation_contract"]


def matched_threshold_contract() -> dict:
    contract = base_contract(
        "QUANTILE",
        relation="ABSOLUTE",
        unit="µg/person-day",
        allowed=["QUANTILE", "COMPLIANCE"],
    )
    b = body(contract)
    b["evaluation_object"] = "population-contaminant assessment cell"
    b["decision_question"] = "whether the high-exposure quantile exceeds the applicable intake threshold"
    b["output_scope"] = {
        "object": "daily dietary contaminant intake",
        "population": "declared population",
        "geography": "declared geography",
        "time": "declared assessment period",
        "category": "declared contaminant and food taxonomy",
    }
    b["comparator"] = {
        "used": True,
        "value": 10.0,
        "unit": "µg/person-day",
        "provenance": "OFFICIAL_STANDARD",
        "source": "versioned authority intake threshold",
        "scope": deepcopy(b["output_scope"]),
        "version_or_date": "declared applicable version",
    }
    b["hard_gate"] = "LINK_TO_EXISTING_HARD_CONSTRAINT_RULE"
    b["allowed_claim"] = "threshold comparison for the declared synthetic assessment cell"
    return contract


def test_a_relative_city_score_cannot_be_promoted_to_probability() -> None:
    contract = base_contract(allowed=["RELATIVE_SCORE", "PROBABILITY"])
    body(contract)["evaluation_object"] = "city"
    body(contract)["output_method"] = "TOPSIS closeness"
    result = assess_contract(contract, "PROBABILITY")
    assert "RELATIVE_OUTPUT_AS_PROBABILITY" in result["reviewer_codes"]
    assert result["claim_allowed"] is False


def test_b_supplier_rank_cannot_imply_failure_probability() -> None:
    contract = base_contract("RANK", allowed=["RANK", "PROBABILITY"])
    body(contract)["evaluation_object"] = "supplier"
    assert "RELATIVE_OUTPUT_AS_PROBABILITY" in reviewer_codes(contract, "PROBABILITY")


def test_c_explicit_probability_model_is_valid() -> None:
    contract = base_contract(
        "PROBABILITY",
        relation="ABSOLUTE",
        unit="probability",
        allowed=["PROBABILITY"],
    )
    b = body(contract)
    b["evaluation_object"] = "credit applicant"
    b["decision_question"] = "estimate P(default within one year)"
    b["output_method"] = "held-out calibrated probability model"
    b["allowed_claim"] = "estimated one-year default probability for the declared population"
    result = assess_contract(contract, "PROBABILITY")
    assert result["status"] == "EVALUATION_SEMANTICS_VERIFIED"
    assert result["reviewer_codes"] == []


def test_d_quantile_is_not_probability() -> None:
    contract = base_contract(
        "QUANTILE",
        relation="ABSOLUTE",
        unit="currency",
        allowed=["QUANTILE", "PROBABILITY"],
    )
    body(contract)["decision_question"] = "estimate Q_0.99(loss)"
    assert "QUANTILE_PROBABILITY_CONFLATION" in reviewer_codes(contract, "PROBABILITY")


def test_e_education_class_without_threshold_provenance_is_blocked() -> None:
    contract = base_contract("CLASS", relation="ABSOLUTE", allowed=["CLASS"])
    body(contract)["evaluation_object"] = "student"
    body(contract)["decision_question"] = "assign HIGH, MEDIUM, or LOW"
    assert "THRESHOLD_PROVENANCE_MISSING" in reviewer_codes(contract, "CLASS")


def test_f_derived_ratio_threshold_passes_when_semantics_match() -> None:
    contract = base_contract(
        "PHYSICAL_ESTIMATE",
        relation="ABSOLUTE",
        unit="dimensionless ratio",
        allowed=["PHYSICAL_ESTIMATE", "COMPLIANCE"],
    )
    b = body(contract)
    b["decision_question"] = "whether rho=q/T exceeds one"
    b["output_scope"] = {
        "object": "ratio of matched quantile to threshold",
        "population": "declared population",
        "geography": "declared geography",
        "time": "declared period",
        "category": "declared outcome",
    }
    b["comparator"] = {
        "used": True,
        "value": 1.0,
        "unit": "dimensionless ratio",
        "provenance": "DERIVED",
        "source": "rho=q/T; equality occurs at rho=1",
        "scope": deepcopy(b["output_scope"]),
        "version_or_date": "derived in current model",
    }
    b["hard_gate"] = "LINK_TO_EXISTING_HARD_CONSTRAINT_RULE"
    b["allowed_claim"] = "whether the matched ratio exceeds its derived boundary"
    assert assess_contract(contract, "COMPLIANCE")["reviewer_codes"] == []


def test_g_daily_intake_cannot_use_blood_concentration_comparator() -> None:
    contract = matched_threshold_contract()
    comparator = body(contract)["comparator"]
    comparator["unit"] = "µg/L"
    comparator["scope"]["object"] = "blood contaminant concentration"
    comparator["source"] = "blood diagnostic comparator"
    result = assess_contract(contract, "COMPLIANCE")
    assert "COMPARATOR_SCOPE_MISMATCH" in result["reviewer_codes"]
    assert result["formal_compliance"] == "BLOCKED"


def test_h_daily_intake_cannot_use_food_content_limit() -> None:
    contract = matched_threshold_contract()
    comparator = body(contract)["comparator"]
    comparator["unit"] = "µg/kg food"
    comparator["scope"]["object"] = "contaminant concentration in food"
    comparator["scope"]["population"] = "not applicable"
    comparator["source"] = "food-content standard"
    assert "COMPARATOR_SCOPE_MISMATCH" in reviewer_codes(contract, "COMPLIANCE")


def test_i_relative_score_cannot_directly_claim_compliance() -> None:
    contract = base_contract(allowed=["RELATIVE_SCORE", "COMPLIANCE"])
    assert "RELATIVE_OUTPUT_AS_COMPLIANCE" in reviewer_codes(contract, "COMPLIANCE")


def test_j_claim_cannot_exceed_allowed_relative_supplier_ranking() -> None:
    contract = base_contract("RANK", allowed=["RANK"])
    b = body(contract)
    b["evaluation_object"] = "supplier"
    b["allowed_claim"] = "relative supplier ranking in the declared comparison set"
    assert "EVALUATION_CLAIM_SCOPE_EXCEEDED" in reviewer_codes(contract, "COMPLIANCE")


def test_k_hard_violation_cannot_be_compensated_by_excellent_soft_score() -> None:
    contract = matched_threshold_contract()
    result = assess_contract(contract, "COMPLIANCE", hard_violation=True, soft_score=0.99)
    assert result["formal_compliance"] == "FAIL"
    assert result["hard_gate_reused"] is True
    assert result["soft_score_ignored_for_hard_gate"] == 0.99


def test_l_clearly_relative_city_ranking_is_valid() -> None:
    contract = base_contract(allowed=["RELATIVE_SCORE", "RANK"])
    b = body(contract)
    b["evaluation_object"] = "city"
    b["decision_question"] = "order the six current cities by relative composite quality"
    b["allowed_claim"] = "relative ranking among the current six cities"
    result = assess_contract(contract, "RANK")
    assert result["reviewer_codes"] == []
    assert result["status"] == "EVALUATION_SEMANTICS_VERIFIED"


def test_fuzzy_membership_is_not_probability_without_calibration() -> None:
    contract = base_contract(allowed=["RELATIVE_SCORE", "PROBABILITY"])
    body(contract)["output_method"] = "fuzzy membership"
    assert "RELATIVE_OUTPUT_AS_PROBABILITY" in reviewer_codes(contract, "PROBABILITY")


def test_verified_calibration_is_a_new_mathematical_step() -> None:
    contract = base_contract(allowed=["RELATIVE_SCORE", "PROBABILITY"])
    body(contract)["output_conversion"] = {
        "from_semantics": "RELATIVE_SCORE",
        "to_semantics": "PROBABILITY",
        "model": "held-out isotonic calibration",
        "evidence": "calibration set and reliability assessment",
        "status": "VERIFIED",
    }
    assert "RELATIVE_OUTPUT_AS_PROBABILITY" not in reviewer_codes(contract, "PROBABILITY")


def test_undeclared_target_and_output_emit_required_codes() -> None:
    contract = base_contract()
    body(contract)["evaluation_object"] = ""
    body(contract)["decision_question"] = ""
    body(contract)["output_semantics"] = ""
    codes = reviewer_codes(contract)
    assert "EVALUATION_TARGET_UNDECLARED" in codes
    assert "OUTPUT_SEMANTICS_UNDECLARED" in codes


def test_activation_boundary_is_specific_to_evaluation_decisions() -> None:
    assert should_activate("Use TOPSIS for a multi-criteria decision")
    assert should_activate("将 99.999% 分位数用于决策")
    assert should_activate("compare the estimate with a regulatory comparison threshold")
    assert not should_activate("fit an ordinary regression model")
    assert not should_activate("train a classification prediction model")
    assert not should_activate("minimize an optimization objective value")
    assert not should_activate("estimate a mechanism parameter")
