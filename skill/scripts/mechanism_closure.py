"""Lightweight mechanism-model closure and claim checks.

This module checks whether a declared mechanism model is closed under its own
assumptions. It does not solve ODEs, infer physical parameters, or choose a
physics model. Callers provide a mapping shaped like the mechanism-closure
template and receive deterministic status/claim/reviewer decisions.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


SOURCE_TYPES = {
    "GIVEN",
    "DERIVED",
    "EXTERNAL",
    "ASSUMED",
    "PARAMETERIZED",
    "MISSING",
}

REQUIREMENT_STATUSES = {
    "RESOLVED",
    "PARAMETERIZED",
    "ASSUMED",
    "MISSING",
    "UNVERIFIED",
}

CLOSURE_STATUSES = {
    "CLOSED_FOR_UNIQUE_NUMERICAL",
    "PARAMETRIC",
    "SCENARIO_ASSUMED",
    "PARTIAL",
    "UNVERIFIED",
}

CLAIM_LEVELS = {
    "UNIQUE_NUMERICAL_UNDER_MODEL",
    "PARAMETRIC_RESULT",
    "SCENARIO_RESULT",
    "PARTIAL_RESULT",
    "NO_FORMAL_RESULT",
}

IDENTIFIABILITY_STATUSES = {"PASS", "LIMITED", "NON_IDENTIFIABLE", "UNVERIFIED"}

REQUIREMENT_CATEGORIES = (
    "geometry_requirements",
    "state_initial_requirements",
    "boundary_interface_requirements",
    "forcing_input_requirements",
    "material_constitutive_requirements",
    "observation_requirements",
    "termination_horizon_requirements",
)

REQUIREMENT_FIELDS = (
    "name",
    "meaning",
    "required_for",
    "source_type",
    "source",
    "value_or_parameter",
    "unit",
    "status",
    "essential",
    "assumption_reason",
)

REVIEWER_CODES = {
    "MECHANISM_CLOSURE_UNVERIFIED",
    "SILENT_CLOSURE_ASSUMPTION",
    "UNSUPPORTED_UNIQUE_NUMERICAL_CLAIM",
    "TERMINATION_RULE_UNVERIFIED",
    "MODEL_FORM_UNCERTAINTY_IGNORED",
}


def _contract_body(contract: Mapping[str, Any]) -> Mapping[str, Any]:
    """Accept either the template wrapper or the inner mapping."""
    nested = contract.get("mechanism_closure")
    if isinstance(nested, Mapping):
        return nested
    return contract


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def iter_requirements(contract: Mapping[str, Any]):
    """Yield ``(category, requirement)`` pairs in stable category order."""
    body = _contract_body(contract)
    for category in REQUIREMENT_CATEGORIES:
        items = body.get(category, [])
        if not _is_sequence(items):
            continue
        for item in items:
            if isinstance(item, Mapping):
                yield category, item


def validate_contract(contract: Mapping[str, Any]) -> list[str]:
    """Return schema/provenance errors without deriving a closure status."""
    errors: list[str] = []
    if not isinstance(contract, Mapping):
        return ["contract must be a mapping"]
    body = _contract_body(contract)
    for field in ("model_name", "prediction_or_simulation_target", "closure_scope"):
        if not str(body.get(field, "")).strip():
            errors.append(f"missing contract field: {field}")

    for category in REQUIREMENT_CATEGORIES:
        if category not in body:
            continue
        items = body[category]
        if not _is_sequence(items):
            errors.append(f"{category} must be a list")
            continue
        for index, requirement in enumerate(items):
            prefix = f"{category}[{index}]"
            if not isinstance(requirement, Mapping):
                errors.append(f"{prefix} must be a mapping")
                continue
            for field in REQUIREMENT_FIELDS:
                if field not in requirement:
                    errors.append(f"{prefix} missing field: {field}")
            source_type = requirement.get("source_type")
            if source_type not in SOURCE_TYPES:
                errors.append(f"{prefix} invalid source_type: {source_type}")
            status = requirement.get("status")
            if status not in REQUIREMENT_STATUSES:
                errors.append(f"{prefix} invalid status: {status}")
            if not isinstance(requirement.get("essential"), bool):
                errors.append(f"{prefix} essential must be boolean")
            if source_type == "MISSING" and status not in {"MISSING", "PARAMETERIZED", "UNVERIFIED"}:
                errors.append(f"{prefix} MISSING source_type needs unresolved status")
            if source_type == "DERIVED" and not str(requirement.get("source", "")).strip():
                errors.append(f"{prefix} DERIVED requirement needs a derivation source")

    identifiability = body.get("identifiability_status")
    if identifiability not in IDENTIFIABILITY_STATUSES:
        errors.append(f"invalid identifiability_status: {identifiability}")
    if not isinstance(body.get("numerical_termination_verified"), bool):
        errors.append("numerical_termination_verified must be boolean")

    declared_status = body.get("closure_status")
    if declared_status is not None and declared_status not in CLOSURE_STATUSES:
        errors.append(f"invalid closure_status: {declared_status}")
    declared_claim = body.get("allowed_claim_level")
    if declared_claim is not None and declared_claim not in CLAIM_LEVELS:
        errors.append(f"invalid allowed_claim_level: {declared_claim}")

    for field in ("unresolved_requirements", "assumptions_added", "parameterized_requirements", "evidence"):
        if field in body and not _is_sequence(body[field]):
            errors.append(f"{field} must be a list")
    return errors


def _essential_requirements(body: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [item for _, item in iter_requirements(body) if item.get("essential") is True]


def _names(values: Any) -> set[str]:
    if not _is_sequence(values):
        return set()
    result: set[str] = set()
    for value in values:
        if isinstance(value, Mapping):
            name = value.get("name")
        else:
            name = value
        if name is not None:
            result.add(str(name))
    return result


def derive_closure_status(contract: Mapping[str, Any]) -> str:
    """Derive the least permissive valid closure status."""
    body = _contract_body(contract)
    if validate_contract(contract):
        return "UNVERIFIED"
    declared_status = body.get("closure_status")
    if declared_status in {"PARTIAL", "UNVERIFIED"}:
        return declared_status
    essentials = _essential_requirements(body)
    if not essentials:
        return "UNVERIFIED"

    parameterized_names = _names(body.get("parameterized_requirements"))
    unresolved_names = _names(body.get("unresolved_requirements"))
    missing = []
    parameterized = []
    assumed = []
    unverified = []
    for requirement in essentials:
        name = str(requirement.get("name"))
        source_type = requirement.get("source_type")
        status = requirement.get("status")
        if source_type == "PARAMETERIZED" or status == "PARAMETERIZED" or name in parameterized_names:
            parameterized.append(requirement)
        elif source_type == "MISSING" or status == "MISSING" or name in unresolved_names:
            missing.append(requirement)
        elif source_type == "ASSUMED" or status == "ASSUMED":
            assumed.append(requirement)
        elif status == "UNVERIFIED":
            unverified.append(requirement)

    if missing or unverified:
        return "UNVERIFIED"
    if parameterized:
        return "PARAMETRIC"
    if assumed:
        return "SCENARIO_ASSUMED"

    termination_requirements = body.get("termination_horizon_requirements", [])
    termination_is_essential = any(
        isinstance(item, Mapping) and item.get("essential") is True for item in termination_requirements
    )
    if termination_is_essential and body.get("numerical_termination_verified") is not True:
        return "UNVERIFIED"
    return "CLOSED_FOR_UNIQUE_NUMERICAL"


def allowed_claim_for_status(status: str) -> str:
    """Return the strongest claim permitted by a closure status."""
    return {
        "CLOSED_FOR_UNIQUE_NUMERICAL": "UNIQUE_NUMERICAL_UNDER_MODEL",
        "PARAMETRIC": "PARAMETRIC_RESULT",
        "SCENARIO_ASSUMED": "SCENARIO_RESULT",
        "PARTIAL": "PARTIAL_RESULT",
        "UNVERIFIED": "NO_FORMAL_RESULT",
    }.get(status, "NO_FORMAL_RESULT")


def claim_is_allowed(
    contract: Mapping[str, Any],
    claim_level: str,
    *,
    claim_scope: str = "",
) -> bool:
    """Check a claim against derived closure and parameter identifiability."""
    if claim_level not in CLAIM_LEVELS:
        return False
    status = derive_closure_status(contract)
    if claim_level == "NO_FORMAL_RESULT":
        return True
    if claim_level != allowed_claim_for_status(status):
        return False
    if claim_scope.upper() in {"PARAMETER_ESTIMATION", "UNIQUE_PARAMETER_ESTIMATES"}:
        body = _contract_body(contract)
        return body.get("identifiability_status") == "PASS"
    return True


def _assumption_guard(body: Mapping[str, Any]) -> bool:
    records = body.get("assumptions_added", [])
    if not _is_sequence(records):
        return False
    by_name = {str(item.get("name")): item for item in records if isinstance(item, Mapping)}
    for requirement in _essential_requirements(body):
        if requirement.get("source_type") != "ASSUMED" and requirement.get("status") != "ASSUMED":
            continue
        record = by_name.get(str(requirement.get("name")))
        if not record:
            return False
        if not all(str(record.get(field, "")).strip() for field in ("reason", "plausible_range", "result_dependency")):
            return False
    return True


def reviewer_codes(contract: Mapping[str, Any], claimed_level: str | None = None) -> list[str]:
    """Return deterministic reviewer guard codes for a declared contract."""
    body = _contract_body(contract)
    codes: list[str] = []
    schema_errors = validate_contract(contract)
    derived = derive_closure_status(contract)
    if schema_errors or derived == "UNVERIFIED":
        codes.append("MECHANISM_CLOSURE_UNVERIFIED")

    if not _assumption_guard(body):
        has_assumed = any(
            item.get("source_type") == "ASSUMED" or item.get("status") == "ASSUMED"
            for item in _essential_requirements(body)
        )
        if has_assumed:
            codes.append("SILENT_CLOSURE_ASSUMPTION")

    if claimed_level == "UNIQUE_NUMERICAL_UNDER_MODEL" and not claim_is_allowed(contract, claimed_level):
        codes.append("UNSUPPORTED_UNIQUE_NUMERICAL_CLAIM")

    termination_requirements = body.get("termination_horizon_requirements", [])
    if any(isinstance(item, Mapping) and item.get("essential") is True for item in termination_requirements):
        if body.get("numerical_termination_verified") is not True:
            codes.append("TERMINATION_RULE_UNVERIFIED")

    discrepancy = body.get("model_form_uncertainty", {})
    if isinstance(discrepancy, Mapping) and discrepancy.get("status") == "PRESENT" and discrepancy.get("acknowledged") is not True:
        codes.append("MODEL_FORM_UNCERTAINTY_IGNORED")

    return list(dict.fromkeys(code for code in codes if code in REVIEWER_CODES))


def assess_contract(contract: Mapping[str, Any], claimed_level: str | None = None) -> dict[str, Any]:
    """Return validation, derived status, claim and reviewer information."""
    body = _contract_body(contract)
    errors = validate_contract(contract)
    status = derive_closure_status(contract)
    claim = allowed_claim_for_status(status)
    return {
        "valid_schema": not errors,
        "schema_errors": errors,
        "closure_status": status,
        "allowed_claim_level": claim,
        "claimed_level": claimed_level,
        "claim_allowed": claimed_level is None or claim_is_allowed(contract, claimed_level),
        "identifiability_status": body.get("identifiability_status"),
        "numerical_termination_verified": body.get("numerical_termination_verified"),
        "reviewer_codes": reviewer_codes(contract, claimed_level),
        "essential_requirements": [str(item.get("name")) for item in _essential_requirements(body)],
    }


__all__ = [
    "CLAIM_LEVELS",
    "CLOSURE_STATUSES",
    "REQUIREMENT_CATEGORIES",
    "REVIEWER_CODES",
    "SOURCE_TYPES",
    "allowed_claim_for_status",
    "assess_contract",
    "claim_is_allowed",
    "derive_closure_status",
    "reviewer_codes",
    "validate_contract",
]
