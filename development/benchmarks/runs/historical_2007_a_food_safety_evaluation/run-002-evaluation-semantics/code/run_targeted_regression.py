"""Post-fix 2007A semantic regressions; no risk model is rerun."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[6]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from skill.scripts.evaluation_semantics import assess_contract  # noqa: E402


RUN_DIR = Path(__file__).resolve().parents[1]
HISTORICAL_DIR = RUN_DIR.parent


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _case(case_id: str, expected: str, observed: str, reviewer_codes: list[str]) -> dict:
    return {
        "case_id": case_id,
        "expected": expected,
        "observed": observed,
        "reviewer_codes": reviewer_codes,
        "passed": expected == observed,
    }


def run() -> dict:
    contracts = _load_json(RUN_DIR / "evaluation-contracts.json")
    primary = contracts["primary_quantile_contract"]
    triage = contracts["secondary_triage_contract"]
    cases: list[dict] = []

    valid_quantile = assess_contract(primary, "QUANTILE")
    cases.append(_case(
        "2007A_VALID_PRIMARY_QUANTILE",
        "PASS",
        "PASS" if valid_quantile["status"] == "EVALUATION_SEMANTICS_VERIFIED" and not valid_quantile["reviewer_codes"] else "BLOCKED",
        valid_quantile["reviewer_codes"],
    ))

    valid_compliance = assess_contract(primary, "COMPLIANCE")
    cases.append(_case(
        "2007A_VALID_SYNTHETIC_THRESHOLD_CLASS",
        "PASS",
        "PASS" if valid_compliance["formal_compliance"] == "ELIGIBLE_FOR_CONCLUSION" and not valid_compliance["reviewer_codes"] else "BLOCKED",
        valid_compliance["reviewer_codes"],
    ))

    valid_rank = assess_contract(triage, "RANK")
    cases.append(_case(
        "2007A_VALID_SECONDARY_RELATIVE_TRIAGE",
        "PASS",
        "PASS" if valid_rank["status"] == "EVALUATION_SEMANTICS_VERIFIED" and not valid_rank["reviewer_codes"] else "BLOCKED",
        valid_rank["reviewer_codes"],
    ))

    quantile_probability = assess_contract(primary, "PROBABILITY")
    cases.append(_case(
        "2007A_QUANTILE_AS_PROBABILITY",
        "BLOCKED",
        "BLOCKED" if "QUANTILE_PROBABILITY_CONFLATION" in quantile_probability["reviewer_codes"] else "NOT_BLOCKED",
        quantile_probability["reviewer_codes"],
    ))

    blood = deepcopy(primary)
    blood_comparator = blood["evaluation_contract"]["comparator"]
    blood_comparator["value"] = 100.0
    blood_comparator["unit"] = "µg/L blood"
    blood_comparator["source"] = "blood-concentration diagnostic comparator"
    blood_comparator["scope"]["object"] = "blood contaminant concentration"
    blood_result = assess_contract(blood, "COMPLIANCE")
    cases.append(_case(
        "2007A_DIETARY_QUANTILE_VS_BLOOD_CONCENTRATION",
        "BLOCKED",
        "BLOCKED" if "COMPARATOR_SCOPE_MISMATCH" in blood_result["reviewer_codes"] and blood_result["formal_compliance"] == "BLOCKED" else "NOT_BLOCKED",
        blood_result["reviewer_codes"],
    ))

    food = deepcopy(primary)
    food_comparator = food["evaluation_contract"]["comparator"]
    food_comparator["value"] = 0.2
    food_comparator["unit"] = "mg/kg food"
    food_comparator["source"] = "food-content concentration standard"
    food_comparator["scope"]["object"] = "contaminant concentration in food"
    food_comparator["scope"]["population"] = "not applicable"
    food_result = assess_contract(food, "COMPLIANCE")
    cases.append(_case(
        "2007A_DAILY_INTAKE_VS_FOOD_CONTENT_LIMIT",
        "BLOCKED",
        "BLOCKED" if "COMPARATOR_SCOPE_MISMATCH" in food_result["reviewer_codes"] and food_result["formal_compliance"] == "BLOCKED" else "NOT_BLOCKED",
        food_result["reviewer_codes"],
    ))

    frozen_completion = _load_json(HISTORICAL_DIR / "run-001" / "completion.json")
    reference_completion = _load_json(HISTORICAL_DIR / "reference-benchmark" / "completion.json")
    frozen_ok = (
        frozen_completion.get("final_result_status") == "VALID"
        and reference_completion.get("final_decision") == "GENERALIZABLE_EVALUATION_GAP_FOUND"
    )
    cases.append(_case(
        "FROZEN_HISTORICAL_STATUS",
        "PASS",
        "PASS" if frozen_ok else "CHANGED",
        [],
    ))

    return {
        "run_type": "POST_FIX_TARGETED_REGRESSION",
        "risk_model_rerun": False,
        "quantile_reestimated": False,
        "ranking_recomputed": False,
        "cases": cases,
        "passed": all(case["passed"] for case in cases),
    }


def main() -> int:
    result = run()
    output = RUN_DIR / "outputs" / "results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
