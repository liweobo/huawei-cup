"""Lightweight gates and bookkeeping for structured improvement phases.

This module deliberately implements no metaheuristic or solver. It validates
the improvement contract, compares real objectives, updates a monotone
feasible incumbent, tracks a bounded search budget, and validates a compact
audit trace.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


CONTRACT_FIELDS = {
    "problem_type",
    "objective_direction",
    "incumbent_source",
    "incumbent_feasible",
    "decision_structure",
    "move_families",
    "candidate_realization",
    "feasibility_check",
    "objective_evaluator",
    "acceptance_rule",
    "incumbent_update_rule",
    "search_budget",
    "stopping_rule",
    "deterministic",
    "status",
}
MOVE_FIELDS = {
    "name",
    "decision_component",
    "description",
    "rationale",
    "applicability",
    "expected_effect",
}


def _missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def is_improvement_candidate(**signals: bool) -> dict[str, Any]:
    """Detect when a structured improvement phase is justified."""
    active = all(
        bool(signals.get(name, False))
        for name in (
            "feasible_incumbent_available",
            "no_proven_exact_optimum",
            "quality_may_improve_via_discrete_changes",
            "meaningful_moves_available",
            "candidate_can_be_realized_feasibly",
        )
    )
    return {
        "problem_type": "STRUCTURED_IMPROVEMENT" if active else "NOT_APPLICABLE",
        "structured_improvement_required": active,
        "signals": dict(signals),
    }


def validate_improvement_contract(
    contract: Mapping[str, Any] | None,
) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(contract, Mapping):
        return {
            "status": "IMPROVEMENT_CONTRACT_INCOMPLETE",
            "errors": ["structured improvement contract is required"],
            "eligible_for_formal_improvement": False,
        }
    missing = sorted(
        field
        for field in CONTRACT_FIELDS
        if field not in contract or _missing(contract.get(field))
    )
    if missing:
        errors.append(f"missing contract fields: {missing}")
    if contract.get("problem_type") != "STRUCTURED_IMPROVEMENT":
        errors.append("problem_type must be STRUCTURED_IMPROVEMENT")
    direction = str(contract.get("objective_direction", "")).upper()
    if direction not in {"MAXIMIZE", "MINIMIZE"}:
        errors.append("objective_direction must be MAXIMIZE or MINIMIZE")
    families = contract.get("move_families")
    if not isinstance(families, list) or not families:
        errors.append("move_families must be a non-empty list")
    else:
        for index, family in enumerate(families):
            if not isinstance(family, Mapping):
                errors.append(f"move_families[{index}] must be a mapping")
                continue
            absent = sorted(
                field for field in MOVE_FIELDS if _missing(family.get(field))
            )
            if absent:
                errors.append(f"move_families[{index}] missing fields: {absent}")
            generic = str(family.get("decision_component", "")).strip().lower()
            if generic in {"mutation", "random", "neighbor", "perturbation"}:
                errors.append(
                    f"move_families[{index}] lacks real decision semantics"
                )
    budget = contract.get("search_budget")
    if not isinstance(budget, Mapping) or not any(
        budget.get(key) is not None
        for key in ("max_iterations", "max_evaluations", "time_limit_seconds")
    ):
        errors.append("search_budget requires iterations, evaluations, or time")
    if _missing(contract.get("stopping_rule")):
        errors.append("stopping_rule is required")
    if not bool(contract.get("incumbent_feasible")):
        errors.append("incumbent must be feasible")
    if contract.get("deterministic") is False and _missing(contract.get("random_seed")):
        errors.append("stochastic improvement requires random_seed")
    return {
        "status": "PASS" if not errors else "IMPROVEMENT_CONTRACT_INCOMPLETE",
        "errors": errors,
        "objective_direction": direction or None,
        "eligible_for_formal_improvement": not errors,
    }


def objective_is_better(
    candidate_objective: float,
    incumbent_objective: float,
    *,
    direction: str,
) -> bool:
    direction = str(direction).upper()
    if direction not in {"MAXIMIZE", "MINIMIZE"}:
        raise ValueError("direction must be MAXIMIZE or MINIMIZE")
    if direction == "MAXIMIZE":
        return float(candidate_objective) > float(incumbent_objective)
    return float(candidate_objective) < float(incumbent_objective)


def update_incumbent(
    incumbent: Mapping[str, Any] | None,
    candidate: Mapping[str, Any],
    *,
    direction: str,
    objective_key: str = "objective",
) -> dict[str, Any]:
    """Update incumbent only for a feasible candidate with a real objective."""
    errors: list[str] = []
    if not candidate.get("feasible"):
        errors.append("INFEASIBLE_NEIGHBOR_AS_VALID")
    if candidate.get(objective_key) is None:
        errors.append("REAL_OBJECTIVE_REQUIRED")
    if errors:
        return {
            "status": "REJECTED",
            "errors": errors,
            "incumbent": dict(incumbent) if incumbent is not None else None,
            "updated": False,
        }
    if incumbent is None:
        return {
            "status": "PASS",
            "errors": [],
            "incumbent": dict(candidate),
            "updated": True,
        }
    if incumbent.get(objective_key) is None:
        raise ValueError("incumbent lacks the real objective")
    if not incumbent.get("feasible", True):
        return {
            "status": "PASS",
            "errors": [],
            "incumbent": dict(candidate),
            "updated": True,
        }
    updated = objective_is_better(
        candidate[objective_key],
        incumbent[objective_key],
        direction=direction,
    )
    return {
        "status": "PASS",
        "errors": [],
        "incumbent": dict(candidate) if updated else dict(incumbent),
        "updated": updated,
    }


class ImprovementBudget:
    """Small bookkeeping object; it does not define a search algorithm."""

    def __init__(
        self,
        *,
        max_iterations: int | None = None,
        max_evaluations: int | None = None,
        time_limit_seconds: float | None = None,
    ):
        if max_iterations is None and max_evaluations is None and time_limit_seconds is None:
            raise ValueError("SEARCH_BUDGET_UNSPECIFIED")
        if max_iterations is not None and max_iterations < 0:
            raise ValueError("max_iterations must be non-negative")
        if max_evaluations is not None and max_evaluations < 0:
            raise ValueError("max_evaluations must be non-negative")
        self.max_iterations = max_iterations
        self.max_evaluations = max_evaluations
        self.time_limit_seconds = time_limit_seconds
        self.iterations = 0
        self.evaluations = 0

    def can_continue(self, elapsed_seconds: float = 0.0) -> bool:
        if self.max_iterations is not None and self.iterations >= self.max_iterations:
            return False
        if self.max_evaluations is not None and self.evaluations >= self.max_evaluations:
            return False
        if (
            self.time_limit_seconds is not None
            and elapsed_seconds >= self.time_limit_seconds
        ):
            return False
        return True

    def record_iteration(self) -> None:
        self.iterations += 1

    def record_evaluation(self) -> None:
        self.evaluations += 1

    def summary(self, *, termination_reason: str) -> dict[str, Any]:
        return {
            "iterations": self.iterations,
            "evaluated_moves": self.evaluations,
            "termination_reason": termination_reason,
        }


def validate_trace_record(record: Mapping[str, Any]) -> list[str]:
    required = {
        "iteration",
        "move_family",
        "candidate_id",
        "feasible",
        "objective",
        "incumbent_before",
        "incumbent_after",
        "accepted",
        "reason",
    }
    missing = sorted(field for field in required if field not in record)
    errors = [f"trace missing fields: {missing}"] if missing else []
    if record.get("move_family") in {"", None, "mutation", "random", "neighbor"}:
        errors.append("trace move_family lacks decision semantics")
    return errors


def review_improvement_claim(
    text: str,
    *,
    contract: Mapping[str, Any] | None,
    trace: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return the five reviewer codes without attempting semantic proof."""
    findings: list[dict[str, str]] = []
    claim = str(text or "")
    lowered = claim.lower()
    if contract is None:
        findings.append(
            {
                "code": "UNSTRUCTURED_OPTIMIZATION_SEARCH",
                "message": "claim has no structured improvement contract",
            }
        )
    if any(token in lowered for token in ("penalty", "惩罚", "罚分", "罚项")):
        findings.append(
            {
                "code": "INFEASIBLE_NEIGHBOR_AS_VALID",
                "message": "hard-infeasible neighbors cannot be kept via penalties",
            }
        )
    if "surrogate" in lowered or "替代分数" in claim:
        findings.append(
            {
                "code": "SURROGATE_IMPROVEMENT_CLAIM",
                "message": "surrogate cannot update the real incumbent",
            }
        )
    if contract is not None and contract.get("search_budget") is None:
        findings.append(
            {
                "code": "SEARCH_BUDGET_UNSPECIFIED",
                "message": "formal improvement requires a bounded search budget",
            }
        )
    if trace is None:
        findings.append(
            {
                "code": "IMPROVEMENT_EVIDENCE_MISSING",
                "message": "claim has no auditable before/after trace",
            }
        )
    return {"status": "FAIL" if findings else "PASS", "findings": findings}


def exact_optimum_exception(proof_available: bool, valid_bound: bool) -> dict[str, Any]:
    """Exact optimality removes the obligation to run heuristic improvement."""
    eligible = bool(proof_available and valid_bound)
    return {
        "status": "EXACT_OPTIMUM" if eligible else "IMPROVEMENT_OPTIONAL",
        "exact_optimum_exception": eligible,
        "structured_improvement_required": not eligible,
    }


__all__ = [
    "ImprovementBudget",
    "exact_optimum_exception",
    "is_improvement_candidate",
    "objective_is_better",
    "review_improvement_claim",
    "update_incumbent",
    "validate_improvement_contract",
    "validate_trace_record",
]
