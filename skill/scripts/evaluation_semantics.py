"""Deterministic checks for evaluation targets, outputs, comparators, and claims.

This module does not implement weighting, normalization, ranking, probability
calibration, or any evaluation algorithm.  It validates the semantic contract
that must exist before those operations are used to support a decision claim.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


OUTPUT_SEMANTICS = {
    "PROBABILITY",
    "QUANTILE",
    "PHYSICAL_ESTIMATE",
    "COMPLIANCE",
    "RELATIVE_SCORE",
    "RANK",
    "CLASS",
}

ABSOLUTE_OR_RELATIVE = {"ABSOLUTE", "RELATIVE"}

COMPARATOR_PROVENANCE = {
    "PROBLEM_GIVEN",
    "OFFICIAL_STANDARD",
    "EXTERNAL_REFERENCE",
    "DERIVED",
    "ASSUMED",
}

HARD_GATES = {"NONE", "LINK_TO_EXISTING_HARD_CONSTRAINT_RULE"}

STATUSES = {
    "EVALUATION_SEMANTICS_VERIFIED",
    "EVALUATION_SEMANTICS_PARTIAL",
    "EVALUATION_SEMANTICS_UNVERIFIED",
}

SCOPE_FIELDS = ("object", "population", "geography", "time", "category")

REVIEWER_CODES = {
    "EVALUATION_TARGET_UNDECLARED",
    "OUTPUT_SEMANTICS_UNDECLARED",
    "RELATIVE_OUTPUT_AS_PROBABILITY",
    "QUANTILE_PROBABILITY_CONFLATION",
    "RELATIVE_OUTPUT_AS_COMPLIANCE",
    "COMPARATOR_SCOPE_MISMATCH",
    "THRESHOLD_PROVENANCE_MISSING",
    "EVALUATION_CLAIM_SCOPE_EXCEEDED",
}

ACTIVATION_TERMS = (
    "composite evaluation",
    "综合评价",
    "relative score",
    "相对得分",
    "ranking evaluation",
    "评价排名",
    "risk index",
    "风险指数",
    "风险分级",
    "threshold-based evaluation",
    "阈值评价",
    "regulatory comparison",
    "standard comparison",
    "法规比较",
    "标准比较",
    "probability-like evaluation",
    "概率型评价输出",
    "quantile used for decision",
    "分位数用于决策",
    "physical estimate used for decision",
    "物理估计用于决策",
    "multi-criteria decision",
    "多指标决策",
    "多准则决策",
    "ahp",
    "entropy weight",
    "熵权",
    "topsis",
    "fuzzy evaluation",
    "模糊评价",
    "grading evaluation",
    "等级评价",
)


def _body(contract: Mapping[str, Any]) -> Mapping[str, Any]:
    nested = contract.get("evaluation_contract")
    return nested if isinstance(nested, Mapping) else contract


def _has_text(value: Any) -> bool:
    return bool(str(value or "").strip())


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _normalise(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().replace("μ", "µ").split())


def should_activate(task_description: str) -> bool:
    """Return whether an evaluation output is being translated into a decision.

    Generic regression, predictive classification, optimization objectives, and
    parameter estimation do not activate this contract without an evaluation
    decision signal from ``ACTIVATION_TERMS``.
    """

    text = str(task_description or "").lower()
    return any(term.lower() in text for term in ACTIVATION_TERMS)


def validate_contract(contract: Mapping[str, Any]) -> list[str]:
    """Return structural/provenance errors without choosing an algorithm."""

    if not isinstance(contract, Mapping):
        return ["contract must be a mapping"]
    body = _body(contract)
    errors: list[str] = []

    for field in (
        "evaluation_object",
        "decision_question",
        "output_semantics",
        "absolute_or_relative",
        "output_unit",
        "allowed_claim",
        "status",
    ):
        if not _has_text(body.get(field)):
            errors.append(f"missing contract field: {field}")

    semantics = body.get("output_semantics")
    if semantics not in OUTPUT_SEMANTICS:
        errors.append(f"invalid output_semantics: {semantics}")
    relation = body.get("absolute_or_relative")
    if relation not in ABSOLUTE_OR_RELATIVE:
        errors.append(f"invalid absolute_or_relative: {relation}")
    if semantics in {"RELATIVE_SCORE", "RANK"} and relation != "RELATIVE":
        errors.append(f"{semantics} must be RELATIVE")
    if body.get("hard_gate") not in HARD_GATES:
        errors.append(f"invalid hard_gate: {body.get('hard_gate')}")
    if body.get("status") not in STATUSES:
        errors.append(f"invalid status: {body.get('status')}")

    output_scope = body.get("output_scope")
    if not isinstance(output_scope, Mapping):
        errors.append("output_scope must be a mapping")
    else:
        for field in SCOPE_FIELDS:
            if not _has_text(output_scope.get(field)):
                errors.append(f"output_scope missing field: {field}")

    allowed = body.get("allowed_claim_semantics")
    if not _is_sequence(allowed) or not allowed:
        errors.append("allowed_claim_semantics must be a non-empty list")
    else:
        for value in allowed:
            if value not in OUTPUT_SEMANTICS:
                errors.append(f"invalid allowed_claim_semantics value: {value}")

    comparator = body.get("comparator")
    if not isinstance(comparator, Mapping):
        errors.append("comparator must be a mapping")
        return errors
    if not isinstance(comparator.get("used"), bool):
        errors.append("comparator.used must be boolean")
        return errors
    if comparator.get("used") is True:
        if comparator.get("value") is None:
            errors.append("comparator.value is required when used")
        for field in ("unit", "provenance", "source", "version_or_date"):
            if not _has_text(comparator.get(field)):
                errors.append(f"comparator missing field: {field}")
        if comparator.get("provenance") not in COMPARATOR_PROVENANCE:
            errors.append(f"invalid comparator provenance: {comparator.get('provenance')}")
        scope = comparator.get("scope")
        if not isinstance(scope, Mapping):
            errors.append("comparator.scope must be a mapping")
        else:
            for field in SCOPE_FIELDS:
                if not _has_text(scope.get(field)):
                    errors.append(f"comparator.scope missing field: {field}")

    conversion = body.get("output_conversion")
    if conversion is not None and not isinstance(conversion, Mapping):
        errors.append("output_conversion must be a mapping")
    return errors


def _verified_conversion(body: Mapping[str, Any], target: str) -> bool:
    conversion = body.get("output_conversion")
    if not isinstance(conversion, Mapping):
        return False
    return bool(
        conversion.get("from_semantics") == body.get("output_semantics")
        and conversion.get("to_semantics") == target
        and conversion.get("status") == "VERIFIED"
        and _has_text(conversion.get("model"))
        and _has_text(conversion.get("evidence"))
    )


def _unit_compatible(body: Mapping[str, Any], comparator: Mapping[str, Any]) -> bool:
    if _normalise(body.get("output_unit")) == _normalise(comparator.get("unit")):
        return True
    conversion = comparator.get("unit_conversion")
    return bool(
        isinstance(conversion, Mapping)
        and conversion.get("status") == "VERIFIED"
        and _normalise(conversion.get("from_unit")) == _normalise(body.get("output_unit"))
        and _normalise(conversion.get("to_unit")) == _normalise(comparator.get("unit"))
        and _has_text(conversion.get("formula"))
    )


def comparator_is_compatible(contract: Mapping[str, Any]) -> bool:
    """Check unit and declared semantic scope; equal units alone are insufficient."""

    body = _body(contract)
    comparator = body.get("comparator")
    output_scope = body.get("output_scope")
    if not isinstance(comparator, Mapping) or comparator.get("used") is not True:
        return False
    if not isinstance(output_scope, Mapping) or not isinstance(comparator.get("scope"), Mapping):
        return False
    if not _unit_compatible(body, comparator):
        return False
    comparator_scope = comparator["scope"]
    return all(_normalise(output_scope.get(field)) == _normalise(comparator_scope.get(field)) for field in SCOPE_FIELDS)


def reviewer_codes(
    contract: Mapping[str, Any],
    claimed_semantics: str | None = None,
    *,
    hard_violation: bool = False,
) -> list[str]:
    """Return the eight deterministic evaluation reviewer guards."""

    body = _body(contract)
    codes: list[str] = []
    if not _has_text(body.get("evaluation_object")) or not _has_text(body.get("decision_question")):
        codes.append("EVALUATION_TARGET_UNDECLARED")
    source_semantics = body.get("output_semantics")
    if source_semantics not in OUTPUT_SEMANTICS:
        codes.append("OUTPUT_SEMANTICS_UNDECLARED")

    method = _normalise(body.get("output_method"))
    conversion = _verified_conversion(body, str(claimed_semantics))
    if claimed_semantics == "PROBABILITY" and not conversion:
        if source_semantics in {"RELATIVE_SCORE", "RANK"} or method == "fuzzy membership":
            codes.append("RELATIVE_OUTPUT_AS_PROBABILITY")
        if source_semantics == "QUANTILE":
            codes.append("QUANTILE_PROBABILITY_CONFLATION")
    if claimed_semantics == "COMPLIANCE" and not conversion:
        if source_semantics in {"RELATIVE_SCORE", "RANK"}:
            codes.append("RELATIVE_OUTPUT_AS_COMPLIANCE")

    comparator = body.get("comparator")
    comparator_used = isinstance(comparator, Mapping) and comparator.get("used") is True
    threshold_needed = comparator_used or source_semantics == "CLASS" or claimed_semantics in {"CLASS", "COMPLIANCE"}
    if threshold_needed:
        provenance = comparator.get("provenance") if isinstance(comparator, Mapping) else None
        if not comparator_used or provenance not in COMPARATOR_PROVENANCE:
            codes.append("THRESHOLD_PROVENANCE_MISSING")
    if comparator_used and not comparator_is_compatible(contract):
        codes.append("COMPARATOR_SCOPE_MISMATCH")

    allowed = body.get("allowed_claim_semantics")
    if claimed_semantics is not None and (
        claimed_semantics not in OUTPUT_SEMANTICS
        or not _is_sequence(allowed)
        or claimed_semantics not in allowed
    ):
        codes.append("EVALUATION_CLAIM_SCOPE_EXCEEDED")

    if hard_violation and claimed_semantics == "COMPLIANCE" and body.get("hard_gate") != "LINK_TO_EXISTING_HARD_CONSTRAINT_RULE":
        codes.append("EVALUATION_CLAIM_SCOPE_EXCEEDED")

    return list(dict.fromkeys(code for code in codes if code in REVIEWER_CODES))


def derive_status(contract: Mapping[str, Any], claimed_semantics: str | None = None, *, hard_violation: bool = False) -> str:
    """Derive the least permissive semantic status."""

    body = _body(contract)
    if validate_contract(contract) or reviewer_codes(contract, claimed_semantics, hard_violation=hard_violation):
        return "EVALUATION_SEMANTICS_UNVERIFIED"
    if body.get("status") == "EVALUATION_SEMANTICS_PARTIAL":
        return "EVALUATION_SEMANTICS_PARTIAL"
    if body.get("status") == "EVALUATION_SEMANTICS_UNVERIFIED":
        return "EVALUATION_SEMANTICS_UNVERIFIED"
    return "EVALUATION_SEMANTICS_VERIFIED"


def assess_contract(
    contract: Mapping[str, Any],
    claimed_semantics: str | None = None,
    *,
    hard_violation: bool = False,
    soft_score: float | None = None,
) -> dict[str, Any]:
    """Return schema, semantic guards, status, and hard-gate disposition."""

    body = _body(contract)
    errors = validate_contract(contract)
    codes = reviewer_codes(contract, claimed_semantics, hard_violation=hard_violation)
    status = derive_status(contract, claimed_semantics, hard_violation=hard_violation)
    formal_compliance = None
    if claimed_semantics == "COMPLIANCE":
        if hard_violation and body.get("hard_gate") == "LINK_TO_EXISTING_HARD_CONSTRAINT_RULE":
            formal_compliance = "FAIL"
        elif status != "EVALUATION_SEMANTICS_VERIFIED":
            formal_compliance = "BLOCKED"
        else:
            formal_compliance = "ELIGIBLE_FOR_CONCLUSION"
    return {
        "valid_schema": not errors,
        "schema_errors": errors,
        "status": status,
        "output_semantics": body.get("output_semantics"),
        "absolute_or_relative": body.get("absolute_or_relative"),
        "claimed_semantics": claimed_semantics,
        "claim_allowed": not codes and status == "EVALUATION_SEMANTICS_VERIFIED",
        "comparator_compatible": comparator_is_compatible(contract) if body.get("comparator", {}).get("used") is True else None,
        "hard_gate_reused": body.get("hard_gate") == "LINK_TO_EXISTING_HARD_CONSTRAINT_RULE",
        "hard_violation": hard_violation,
        "soft_score_ignored_for_hard_gate": soft_score if hard_violation else None,
        "formal_compliance": formal_compliance,
        "reviewer_codes": codes,
    }


__all__ = [
    "ABSOLUTE_OR_RELATIVE",
    "ACTIVATION_TERMS",
    "COMPARATOR_PROVENANCE",
    "HARD_GATES",
    "OUTPUT_SEMANTICS",
    "REVIEWER_CODES",
    "SCOPE_FIELDS",
    "STATUSES",
    "assess_contract",
    "comparator_is_compatible",
    "derive_status",
    "reviewer_codes",
    "should_activate",
    "validate_contract",
]
