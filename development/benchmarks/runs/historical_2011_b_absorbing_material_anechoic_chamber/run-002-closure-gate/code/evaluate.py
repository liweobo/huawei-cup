from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[6]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from skill.scripts.mechanism_closure import assess_contract


ROOT = Path(__file__).resolve().parents[1]


def req(name, source_type="GIVEN", status="RESOLVED", value="known", source="synthetic fixture"):
    return {
        "name": name,
        "meaning": name,
        "required_for": "forward simulation",
        "source_type": source_type,
        "source": source,
        "value_or_parameter": value,
        "unit": "unitless",
        "status": status,
        "essential": True,
        "assumption_reason": "",
    }


def base():
    return {
        "mechanism_closure": {
            "model_name": "synthetic mechanism",
            "prediction_or_simulation_target": "state at T",
            "closure_scope": "declared forward model",
            "geometry_requirements": [],
            "state_initial_requirements": [req("x0")],
            "boundary_interface_requirements": [],
            "forcing_input_requirements": [req("k")],
            "material_constitutive_requirements": [],
            "observation_requirements": [req("receiver")],
            "termination_horizon_requirements": [req("T")],
            "unresolved_requirements": [],
            "assumptions_added": [],
            "parameterized_requirements": [],
            "identifiability_status": "PASS",
            "numerical_termination_verified": True,
            "model_form_uncertainty": {"status": "NONE", "acknowledged": False},
            "evidence": ["synthetic fixture"],
        }
    }


def body(contract):
    return contract["mechanism_closure"]


def run_case(name, mutate, expected_status, expected_claim):
    contract = base()
    mutate(contract)
    result = assess_contract(contract)
    return {
        "case": name,
        "closure_status": result["closure_status"],
        "allowed_claim_level": result["allowed_claim_level"],
        "reviewer_codes": result["reviewer_codes"],
        "pass": result["closure_status"] == expected_status and result["allowed_claim_level"] == expected_claim,
    }


def main():
    cases = [
        ("A_fully_closed_ode", lambda c: None, "CLOSED_FOR_UNIQUE_NUMERICAL", "UNIQUE_NUMERICAL_UNDER_MODEL"),
        ("B_missing_initial", lambda c: body(c).update(state_initial_requirements=[req("x0", "MISSING", "MISSING", "")]), "UNVERIFIED", "NO_FORMAL_RESULT"),
        ("C_parametric_fallback", lambda c: (body(c).update(state_initial_requirements=[req("x0", "PARAMETERIZED", "PARAMETERIZED", "x0")]), body(c).update(parameterized_requirements=["x0"])), "PARAMETRIC", "PARAMETRIC_RESULT"),
        ("D_explicit_scenario", lambda c: (body(c).update(state_initial_requirements=[req("x0", "ASSUMED", "ASSUMED", "1")]), body(c).update(assumptions_added=[{"name": "x0", "reason": "scenario", "plausible_range": "0..2", "result_dependency": "material"}])), "SCENARIO_ASSUMED", "SCENARIO_RESULT"),
        ("E_silent_geometry_assumption", lambda c: body(c).update(geometry_requirements=[req("L", "ASSUMED", "ASSUMED", "10", "")]), "SCENARIO_ASSUMED", "SCENARIO_RESULT"),
        ("F_derived_geometry", lambda c: body(c).update(geometry_requirements=[req("L", "DERIVED", "RESOLVED", "2*h*tan(alpha)", "problem facts")]), "CLOSED_FOR_UNIQUE_NUMERICAL", "UNIQUE_NUMERICAL_UNDER_MODEL"),
        ("G_missing_observation", lambda c: body(c).update(observation_requirements=[req("receiver", "MISSING", "MISSING", "")]), "UNVERIFIED", "NO_FORMAL_RESULT"),
        ("H_limited_identifiability", lambda c: body(c).update(identifiability_status="LIMITED"), "CLOSED_FOR_UNIQUE_NUMERICAL", "UNIQUE_NUMERICAL_UNDER_MODEL"),
        ("I_unverified_termination", lambda c: body(c).update(numerical_termination_verified=False), "UNVERIFIED", "NO_FORMAL_RESULT"),
        ("J_verified_termination", lambda c: None, "CLOSED_FOR_UNIQUE_NUMERICAL", "UNIQUE_NUMERICAL_UNDER_MODEL"),
        ("K_acknowledged_model_form_uncertainty", lambda c: body(c).update(model_form_uncertainty={"status": "PRESENT", "acknowledged": True}), "CLOSED_FOR_UNIQUE_NUMERICAL", "UNIQUE_NUMERICAL_UNDER_MODEL"),
        ("L_claim_gate", lambda c: (body(c).update(state_initial_requirements=[req("x0", "PARAMETERIZED", "PARAMETERIZED", "x0")]), body(c).update(parameterized_requirements=["x0"])), "PARAMETRIC", "PARAMETRIC_RESULT"),
    ]
    results = [run_case(*case) for case in cases]
    output = {
        "run_id": "run-002-closure-gate",
        "cases": results,
        "passed": all(item["pass"] for item in results),
        "case_count": len(results),
    }
    output_path = ROOT / "outputs" / "results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
