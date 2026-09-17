"""Lightweight gates for stateful scheduling search contracts.

This module does not implement a simulator, solver, or generic scheduling
platform.  It validates that a formal search either (a) expands legal actions
through an explicit state transition, or (b) decodes a sequence into a real
schedule and verifies hard constraints on that realized schedule.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any


PROBLEM_TYPE = "STATEFUL_SCHEDULING"
REPRESENTATIONS = {
    "STATE_COUPLED",
    "SEQUENCE_WITH_FEASIBLE_DECODER",
    "SEQUENCE_ONLY",
    "OTHER",
}
FEASIBILITY_MODES = {"BY_CONSTRUCTION", "DECODE_AND_VERIFY", "POST_HOC_ONLY"}
CONTRACT_FIELDS = {
    "problem_type",
    "state_variables",
    "resources",
    "queues_or_buffers",
    "time_representation",
    "terminal_condition",
    "legal_action_definition",
    "transition_definition",
    "hard_invariants",
    "objective_definition",
    "candidate_representation",
    "search_mode",
    "decoder_required",
    "feasibility_mode",
    "status",
}


class StatefulSchedulingError(ValueError):
    """A stateful scheduling contract makes a formal candidate invalid."""


def is_stateful_scheduling(
    *,
    dynamically_evolving_feasibility: bool = False,
    decisions_depend_on_prior_actions: bool = False,
    resources_or_positions_change_over_time: bool = False,
    actions_change_future_legality: bool = False,
    blocking_queue_or_finite_buffer: bool = False,
    dynamic_resource_occupancy: bool = False,
    setup_travel_or_processing_state: bool = False,
    release_or_precedence_constraints: bool = False,
    final_permutation_insufficient: bool = False,
) -> dict[str, Any]:
    """Detect stateful feasibility without activating on the word scheduling."""
    signals = {
        "dynamically_evolving_feasibility": bool(dynamically_evolving_feasibility),
        "decisions_depend_on_prior_actions": bool(decisions_depend_on_prior_actions),
        "resources_or_positions_change_over_time": bool(resources_or_positions_change_over_time),
        "actions_change_future_legality": bool(actions_change_future_legality),
        "blocking_queue_or_finite_buffer": bool(blocking_queue_or_finite_buffer),
        "dynamic_resource_occupancy": bool(dynamic_resource_occupancy),
        "setup_travel_or_processing_state": bool(setup_travel_or_processing_state),
        "release_or_precedence_constraints": bool(release_or_precedence_constraints),
        "final_permutation_insufficient": bool(final_permutation_insufficient),
    }
    active = any(signals.values())
    return {
        "problem_type": PROBLEM_TYPE if active else "OTHER",
        "stateful_scheduling_detected": active,
        "signals": signals,
        "activation_rule": "feasibility depends on evolving system state",
    }


def _missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def validate_stateful_contract(contract: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate the minimum contract needed to expand or decode candidates."""
    errors: list[str] = []
    if not isinstance(contract, Mapping):
        return {
            "status": "STATE_SEARCH_UNVERIFIED",
            "errors": ["stateful scheduling contract is required"],
            "eligible_for_formal_search": False,
        }
    missing = sorted(
        field
        for field in CONTRACT_FIELDS
        if field not in contract or _missing(contract.get(field)) and field != "decoder_required"
    )
    if missing:
        errors.append(f"missing contract fields: {missing}")
    if contract.get("problem_type") != PROBLEM_TYPE:
        errors.append("problem_type must be STATEFUL_SCHEDULING")
    representation = str(contract.get("candidate_representation", "")).upper()
    feasibility_mode = str(contract.get("feasibility_mode", "")).upper()
    if representation not in REPRESENTATIONS:
        errors.append(f"candidate_representation must be one of {sorted(REPRESENTATIONS)}")
    if feasibility_mode not in FEASIBILITY_MODES:
        errors.append(f"feasibility_mode must be one of {sorted(FEASIBILITY_MODES)}")
    decoder_required = bool(contract.get("decoder_required"))
    if representation == "STATE_COUPLED" and feasibility_mode != "BY_CONSTRUCTION":
        errors.append("STATE_COUPLED requires feasibility_mode BY_CONSTRUCTION")
    if representation == "SEQUENCE_WITH_FEASIBLE_DECODER":
        if not decoder_required:
            errors.append("SEQUENCE_WITH_FEASIBLE_DECODER requires decoder_required=true")
        if feasibility_mode != "DECODE_AND_VERIFY":
            errors.append("SEQUENCE_WITH_FEASIBLE_DECODER requires DECODE_AND_VERIFY")
    if representation == "SEQUENCE_ONLY" and not decoder_required:
        errors.append(
            "STATE_SEARCH_UNVERIFIED: SEQUENCE_ONLY without a feasible decoder "
            "cannot be formal Improved/Primary search"
        )
    if feasibility_mode == "POST_HOC_ONLY":
        errors.append(
            "STATE_SEARCH_UNVERIFIED: POST_HOC_ONLY cannot be formal "
            "Improved/Primary search"
        )
    invariants = contract.get("hard_invariants")
    if not isinstance(invariants, (list, tuple)) or not invariants:
        errors.append("hard_invariants must be a non-empty list")
    status = "PASS" if not errors else "STATE_SEARCH_UNVERIFIED"
    return {
        "status": status,
        "errors": errors,
        "candidate_representation": representation or None,
        "feasibility_mode": feasibility_mode or None,
        "decoder_required": decoder_required,
        "eligible_for_formal_search": not errors,
    }


def legal_action_errors(
    state: Any,
    action: Any,
    *,
    legal_actions: Callable[[Any], Iterable[Any]],
) -> list[str]:
    """Return a hard rejection if an action is not legal in the current state."""
    try:
        actions = list(legal_actions(state))
    except Exception as exc:  # pragma: no cover - caller-owned state object
        return [f"LEGAL_ACTION_CHECK_FAILED: {exc}"]
    if action not in actions:
        return ["ILLEGAL_ACTION: action is not legal in the current state"]
    return []


def transition_errors(
    state: Any,
    action: Any,
    *,
    legal_actions: Callable[[Any], Iterable[Any]],
    transition: Callable[[Any, Any], Any],
    invariants: Iterable[Callable[[Any], bool]] = (),
) -> list[str]:
    """Reject illegal actions and any transition that breaks an invariant."""
    errors = legal_action_errors(state, action, legal_actions=legal_actions)
    if errors:
        return errors
    try:
        next_state = transition(state, action)
    except Exception as exc:  # pragma: no cover - caller-owned transition
        return [f"TRANSITION_FAILED: {exc}"]
    for index, invariant in enumerate(invariants):
        try:
            valid = invariant(next_state)
        except Exception as exc:  # pragma: no cover - caller-owned invariant
            return [f"INVARIANT_CHECK_FAILED[{index}]: {exc}"]
        if not valid:
            return [f"HARD_INVARIANT_VIOLATION[{index}]"]
    return []


def feasible_decoder_errors(
    sequence: Iterable[Any],
    *,
    decoder: Callable[[Iterable[Any]], Any] | None,
    hard_constraints: Callable[[Any], bool] | None,
    objective: Callable[[Any], float] | None,
) -> list[str]:
    """Validate that a sequence decoder produces and checks a realized schedule."""
    if decoder is None:
        return ["FEASIBLE_DECODER_REQUIRED"]
    if hard_constraints is None:
        return ["DECODER_HARD_CONSTRAINT_CHECK_REQUIRED"]
    if objective is None:
        return ["DECODER_REAL_OBJECTIVE_REQUIRED"]
    try:
        schedule = decoder(sequence)
    except Exception as exc:
        return [f"DECODE_FAILED: {exc}"]
    try:
        if not hard_constraints(schedule):
            return ["DECODE_INFEASIBLE"]
        objective(schedule)
    except Exception as exc:
        return [f"DECODED_SCHEDULE_CHECK_FAILED: {exc}"]
    return []


def select_feasible_incumbent(
    candidates: Iterable[Mapping[str, Any]],
    *,
    sense: str = "maximize",
    objective_key: str = "objective",
) -> dict[str, Any]:
    """Select only feasible candidates, using realized/decoded objective."""
    sense = str(sense).lower()
    if sense not in {"maximize", "minimize"}:
        raise ValueError("sense must be maximize or minimize")
    feasible = []
    for candidate in candidates:
        if not candidate.get("feasible"):
            continue
        if objective_key not in candidate or candidate[objective_key] is None:
            raise ValueError(f"feasible candidate lacks {objective_key}")
        feasible.append(dict(candidate))
    if not feasible:
        return {
            "status": "NO_FEASIBLE_INCUMBENT",
            "incumbent": None,
            "feasible_candidate_count": 0,
        }
    key = lambda candidate: float(candidate[objective_key])
    incumbent = max(feasible, key=key) if sense == "maximize" else min(feasible, key=key)
    return {
        "status": "PASS",
        "incumbent": incumbent,
        "feasible_candidate_count": len(feasible),
    }


def review_stateful_claim(
    text: str,
    *,
    contract: Mapping[str, Any] | None,
    candidate: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Flag the three stateful errors a reviewer must be able to catch."""
    claim = str(text or "")
    findings: list[dict[str, str]] = []
    lowered = claim.lower()
    representation = str((contract or {}).get("candidate_representation", "")).upper()
    feasibility_mode = str((contract or {}).get("feasibility_mode", "")).upper()
    decoder_required = bool((contract or {}).get("decoder_required"))
    if (
        any(
            token in claim
            for token in ("理想顺序", "理想车辆顺序", "排列", "target sequence", "ideal sequence")
        )
        and any(
            token in claim
            for token in ("之后", "再尝试", "然后再", "最后", "finally", "post-hoc")
        )
        and representation == "SEQUENCE_ONLY"
        and not decoder_required
    ):
        findings.append(
            {
                "code": "STATE_FEASIBILITY_DECOUPLED",
                "message": "state feasibility is checked only after sequence optimization",
            }
        )
    if any(token in lowered for token in ("penalty", "惩罚", "扣分")) and (
        "penalty" in lowered or "惩罚" in lowered
    ):
        findings.append(
            {
                "code": "HARD_CONSTRAINT_AS_PENALTY",
                "message": "hard-state violations must be illegal actions, not scoring penalties",
            }
        )
    if candidate and candidate.get("surrogate_objective") is not None and not candidate.get(
        "realized_objective"
    ):
        findings.append(
            {
                "code": "SURROGATE_OBJECTIVE_AS_FINAL",
                "message": "surrogate score cannot select the final incumbent",
            }
        )
    return {"status": "FAIL" if findings else "PASS", "findings": findings}


__all__ = [
    "StatefulSchedulingError",
    "is_stateful_scheduling",
    "legal_action_errors",
    "review_stateful_claim",
    "select_feasible_incumbent",
    "transition_errors",
    "validate_stateful_contract",
    "feasible_decoder_errors",
]
