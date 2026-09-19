from __future__ import annotations

from copy import deepcopy

from skill.scripts.mechanism_closure import (
    assess_contract,
    claim_is_allowed,
    derive_closure_status,
    reviewer_codes,
)


def requirement(
    name: str,
    source_type: str = "GIVEN",
    status: str = "RESOLVED",
    *,
    essential: bool = True,
    value: str = "known",
    source: str = "problem statement",
) -> dict:
    return {
        "name": name,
        "meaning": name,
        "required_for": "forward simulation",
        "source_type": source_type,
        "source": source,
        "value_or_parameter": value,
        "unit": "unitless",
        "status": status,
        "essential": essential,
        "assumption_reason": "",
    }


def base_contract() -> dict:
    return {
        "mechanism_closure": {
            "model_name": "synthetic mechanism",
            "prediction_or_simulation_target": "state at T",
            "closure_scope": "declared forward model",
            "geometry_requirements": [],
            "state_initial_requirements": [requirement("x0")],
            "boundary_interface_requirements": [],
            "forcing_input_requirements": [requirement("parameter_k")],
            "material_constitutive_requirements": [],
            "observation_requirements": [requirement("receiver")],
            "termination_horizon_requirements": [requirement("T")],
            "unresolved_requirements": [],
            "assumptions_added": [],
            "parameterized_requirements": [],
            "identifiability_status": "PASS",
            "numerical_termination_verified": True,
            "model_form_uncertainty": {"status": "NONE", "acknowledged": False},
            "evidence": ["synthetic fixture"],
        }
    }


def body(contract: dict) -> dict:
    return contract["mechanism_closure"]


def test_a_fully_closed_ode_is_unique_under_model() -> None:
    contract = base_contract()
    assert derive_closure_status(contract) == "CLOSED_FOR_UNIQUE_NUMERICAL"
    assert claim_is_allowed(contract, "UNIQUE_NUMERICAL_UNDER_MODEL")


def test_b_missing_initial_condition_blocks_unique_claim() -> None:
    contract = base_contract()
    body(contract)["state_initial_requirements"] = [requirement("x0", "MISSING", "MISSING", value="")]
    assert derive_closure_status(contract) == "UNVERIFIED"
    assert not claim_is_allowed(contract, "UNIQUE_NUMERICAL_UNDER_MODEL")
    assert "MECHANISM_CLOSURE_UNVERIFIED" in reviewer_codes(contract, "UNIQUE_NUMERICAL_UNDER_MODEL")


def test_c_missing_initial_condition_has_parametric_fallback() -> None:
    contract = base_contract()
    body(contract)["state_initial_requirements"] = [requirement("x0", "PARAMETERIZED", "PARAMETERIZED", value="x0")]
    body(contract)["parameterized_requirements"] = ["x0"]
    assert derive_closure_status(contract) == "PARAMETRIC"
    assert claim_is_allowed(contract, "PARAMETRIC_RESULT")
    assert not claim_is_allowed(contract, "UNIQUE_NUMERICAL_UNDER_MODEL")


def test_d_explicit_assumption_is_a_scenario_result() -> None:
    contract = base_contract()
    body(contract)["state_initial_requirements"] = [requirement("x0", "ASSUMED", "ASSUMED", value="1")]
    body(contract)["assumptions_added"] = [
        {"name": "x0", "reason": "scenario requested", "plausible_range": "0 to 2", "result_dependency": "material"}
    ]
    assert derive_closure_status(contract) == "SCENARIO_ASSUMED"
    assert claim_is_allowed(contract, "SCENARIO_RESULT")
    assert not claim_is_allowed(contract, "UNIQUE_NUMERICAL_UNDER_MODEL")


def test_e_hardcoded_geometry_without_provenance_is_silent_assumption() -> None:
    contract = base_contract()
    body(contract)["geometry_requirements"] = [requirement("L", "ASSUMED", "ASSUMED", value="10", source="")]
    assert "SILENT_CLOSURE_ASSUMPTION" in reviewer_codes(contract)


def test_f_traceable_derived_geometry_can_close_model() -> None:
    contract = base_contract()
    body(contract)["geometry_requirements"] = [
        requirement("L", "DERIVED", "RESOLVED", value="2*h*tan(alpha)", source="problem facts h and alpha")
    ]
    assert derive_closure_status(contract) == "CLOSED_FOR_UNIQUE_NUMERICAL"


def test_g_missing_observation_condition_blocks_formal_output() -> None:
    contract = base_contract()
    body(contract)["observation_requirements"] = [requirement("receiver", "MISSING", "MISSING", value="")]
    assert derive_closure_status(contract) == "UNVERIFIED"
    assert assess_contract(contract)["allowed_claim_level"] == "NO_FORMAL_RESULT"


def test_h_limited_identifiability_blocks_unique_parameter_estimates() -> None:
    contract = base_contract()
    body(contract)["identifiability_status"] = "LIMITED"
    assert derive_closure_status(contract) == "CLOSED_FOR_UNIQUE_NUMERICAL"
    assert not claim_is_allowed(contract, "UNIQUE_NUMERICAL_UNDER_MODEL", claim_scope="PARAMETER_ESTIMATION")
    assert claim_is_allowed(contract, "UNIQUE_NUMERICAL_UNDER_MODEL", claim_scope="FORWARD_SIMULATION")


def test_i_unverified_cutoff_emits_termination_guard() -> None:
    contract = base_contract()
    body(contract)["numerical_termination_verified"] = False
    assert derive_closure_status(contract) == "UNVERIFIED"
    assert "TERMINATION_RULE_UNVERIFIED" in reviewer_codes(contract)


def test_j_verified_cutoff_allows_closed_model() -> None:
    contract = base_contract()
    body(contract)["numerical_termination_verified"] = True
    assert derive_closure_status(contract) == "CLOSED_FOR_UNIQUE_NUMERICAL"
    assert "TERMINATION_RULE_UNVERIFIED" not in reviewer_codes(contract)


def test_partial_scope_stays_partial_even_when_one_component_is_closed() -> None:
    contract = base_contract()
    body(contract)["closure_status"] = "PARTIAL"
    assert derive_closure_status(contract) == "PARTIAL"
    assert claim_is_allowed(contract, "PARTIAL_RESULT")
    assert not claim_is_allowed(contract, "UNIQUE_NUMERICAL_UNDER_MODEL")


def test_k_model_form_discrepancy_is_explicitly_acknowledged() -> None:
    contract = base_contract()
    body(contract)["model_form_uncertainty"] = {
        "status": "PRESENT",
        "acknowledged": True,
        "rationale": "two closure-complete approximations disagree",
    }
    assert derive_closure_status(contract) == "CLOSED_FOR_UNIQUE_NUMERICAL"
    assert "MODEL_FORM_UNCERTAINTY_IGNORED" not in reviewer_codes(contract)

    ignored = deepcopy(contract)
    body(ignored)["model_form_uncertainty"]["acknowledged"] = False
    assert "MODEL_FORM_UNCERTAINTY_IGNORED" in reviewer_codes(ignored)


def test_l_parametric_result_cannot_be_published_as_unique() -> None:
    contract = base_contract()
    body(contract)["state_initial_requirements"] = [requirement("x0", "PARAMETERIZED", "PARAMETERIZED", value="x0")]
    body(contract)["parameterized_requirements"] = ["x0"]
    result = assess_contract(contract, "UNIQUE_NUMERICAL_UNDER_MODEL")
    assert result["closure_status"] == "PARAMETRIC"
    assert result["claim_allowed"] is False
    assert "UNSUPPORTED_UNIQUE_NUMERICAL_CLAIM" in result["reviewer_codes"]
