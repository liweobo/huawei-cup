from __future__ import annotations

from run_targeted_regression import run


def _by_id(result: dict) -> dict[str, dict]:
    return {case["case_id"]: case for case in result["cases"]}


def test_valid_frozen_semantics_are_accepted() -> None:
    cases = _by_id(run())
    assert cases["2007A_VALID_PRIMARY_QUANTILE"]["observed"] == "PASS"
    assert cases["2007A_VALID_SYNTHETIC_THRESHOLD_CLASS"]["observed"] == "PASS"
    assert cases["2007A_VALID_SECONDARY_RELATIVE_TRIAGE"]["observed"] == "PASS"


def test_quantile_probability_promotion_is_blocked() -> None:
    case = _by_id(run())["2007A_QUANTILE_AS_PROBABILITY"]
    assert case["observed"] == "BLOCKED"
    assert "QUANTILE_PROBABILITY_CONFLATION" in case["reviewer_codes"]


def test_blood_concentration_comparator_is_blocked() -> None:
    case = _by_id(run())["2007A_DIETARY_QUANTILE_VS_BLOOD_CONCENTRATION"]
    assert case["observed"] == "BLOCKED"
    assert "COMPARATOR_SCOPE_MISMATCH" in case["reviewer_codes"]


def test_food_content_comparator_is_blocked() -> None:
    case = _by_id(run())["2007A_DAILY_INTAKE_VS_FOOD_CONTENT_LIMIT"]
    assert case["observed"] == "BLOCKED"
    assert "COMPARATOR_SCOPE_MISMATCH" in case["reviewer_codes"]


def test_frozen_historical_status_remains_valid() -> None:
    result = run()
    assert _by_id(result)["FROZEN_HISTORICAL_STATUS"]["observed"] == "PASS"
    assert result["risk_model_rerun"] is False
    assert result["quantile_reestimated"] is False
    assert result["ranking_recomputed"] is False
