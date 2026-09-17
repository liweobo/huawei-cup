"""Generic A-L regressions for structured improvement."""

from __future__ import annotations

from itertools import combinations

from skill.scripts.structured_improvement import (
    ImprovementBudget,
    exact_optimum_exception,
    is_improvement_candidate,
    objective_is_better,
    review_improvement_claim,
    update_incumbent,
    validate_improvement_contract,
    validate_trace_record,
)


def contract(**overrides):
    value = {
        "problem_type": "STRUCTURED_IMPROVEMENT",
        "objective_direction": "MAXIMIZE",
        "incumbent_source": "constructive heuristic",
        "incumbent_feasible": True,
        "decision_structure": ["sequence positions"],
        "move_families": [
            {
                "name": "adjacent_swap",
                "decision_component": "sequence positions",
                "description": "swap two adjacent jobs",
                "rationale": "can improve pair-based objective",
                "applicability": "both jobs present",
                "expected_effect": "change pair adjacency",
            }
        ],
        "candidate_realization": "decode sequence to schedule",
        "feasibility_check": "capacity and precedence",
        "objective_evaluator": "realized weighted score",
        "acceptance_rule": "accept objective improvement",
        "incumbent_update_rule": "monotone real objective",
        "search_budget": {"max_evaluations": 10},
        "stopping_rule": "no improving move or budget reached",
        "deterministic": True,
        "random_seed": None,
        "status": "PASS",
    }
    value.update(overrides)
    return value


def decode_score(order):
    # A tiny known-improvement problem: maximize adjacent equal pairs.
    return {"order": list(order), "objective": sum(
        left == right for left, right in zip(order, order[1:])
    )}


def feasible(schedule, precedence):
    positions = {job: index for index, job in enumerate(schedule["order"])}
    return all(
        before in positions and after in positions and positions[before] < positions[after]
        for before, after in precedence
    )


def structured_swap_search(initial, *, direction="MAXIMIZE", budget=10, precedence=()):
    working = decode_score(initial)
    incumbent = working
    moves = []
    evaluations = 0
    for iteration, (left, right) in enumerate(combinations(range(len(working["order"])), 2), 1):
        if evaluations >= budget:
            break
        candidate_order = list(working["order"])
        candidate_order[left], candidate_order[right] = candidate_order[right], candidate_order[left]
        candidate = decode_score(candidate_order)
        evaluations += 1
        is_feasible = feasible(candidate, precedence)
        before = incumbent["objective"]
        accepted = False
        if is_feasible:
            update = update_incumbent(
                incumbent,
                {"id": f"swap-{left}-{right}", "feasible": True, "objective": candidate["objective"]},
                direction=direction,
            )
            incumbent = update["incumbent"]
            accepted = update["updated"]
            if accepted:
                working = candidate
        moves.append(
            {
                "iteration": iteration,
                "move_family": "swap",
                "candidate_id": f"swap-{left}-{right}",
                "feasible": is_feasible,
                "objective": candidate["objective"],
                "incumbent_before": before,
                "incumbent_after": incumbent["objective"],
                "accepted": accepted,
                "reason": "real objective better" if accepted else "not accepted",
            }
        )
    return {
        "status": "PASS",
        "initial": decode_score(initial),
        "incumbent": incumbent,
        "working": working,
        "trace": moves,
        "evaluated_moves": evaluations,
        "termination_reason": "budget" if evaluations >= budget else "no improving move",
    }


def test_a_known_improvement_updates_incumbent() -> None:
    result = structured_swap_search([1, 2, 1], budget=10)
    assert result["incumbent"]["objective"] > result["initial"]["objective"]
    assert any(item["accepted"] for item in result["trace"])


def test_b_no_improvement_is_a_legitimate_negative_result() -> None:
    result = structured_swap_search([1, 1], budget=1)
    assert result["incumbent"]["objective"] == result["initial"]["objective"]
    assert not any(item["accepted"] for item in result["trace"])


def test_c_infeasible_move_is_rejected_before_comparison() -> None:
    # The first swap candidate violates 2-before-1 precedence.
    result = structured_swap_search([1, 2, 1], precedence=((2, 1),), budget=1)
    assert all(item["objective"] == 1 for item in result["trace"])
    update = update_incumbent(
        {"id": "inc", "feasible": True, "objective": 10},
        {"id": "bad", "feasible": False, "objective": 100},
        direction="MAXIMIZE",
    )
    assert update["errors"] == ["INFEASIBLE_NEIGHBOR_AS_VALID"]


def test_d_surrogate_higher_but_real_lower_does_not_update() -> None:
    update = update_incumbent(
        {"id": "inc", "feasible": True, "objective": 10},
        {"id": "candidate", "feasible": True, "objective": 8, "surrogate": 999},
        direction="MAXIMIZE",
    )
    assert update["updated"] is False


def test_e_working_solution_can_worsen_but_incumbent_stays_best() -> None:
    incumbent = {"id": "best", "feasible": True, "objective": 10}
    candidate = {"id": "worse", "feasible": True, "objective": 7}
    update = update_incumbent(incumbent, candidate, direction="MAXIMIZE")
    assert update["incumbent"]["id"] == "best"
    assert update["updated"] is False


def test_f_and_g_objective_directions() -> None:
    assert objective_is_better(11, 10, direction="MAXIMIZE")
    assert not objective_is_better(9, 10, direction="MAXIMIZE")
    assert objective_is_better(9, 10, direction="MINIMIZE")
    assert not objective_is_better(11, 10, direction="MINIMIZE")


def test_h_decoder_integration_accepts_only_decoded_feasible_result() -> None:
    schedule = decode_score([1, 1, 2])
    assert feasible(schedule, ()) is True
    update = update_incumbent(
        None,
        {"id": "decoded", "feasible": feasible(schedule, ()), "objective": schedule["objective"]},
        direction="MAXIMIZE",
    )
    assert update["updated"] is True


def test_i_search_budget_stops() -> None:
    budget = ImprovementBudget(max_evaluations=2)
    budget.record_evaluation()
    budget.record_evaluation()
    assert budget.can_continue() is False
    assert budget.summary(termination_reason="budget")["evaluated_moves"] == 2


def test_j_deterministic_reproducibility() -> None:
    first = structured_swap_search([1, 2, 1], budget=3)
    second = structured_swap_search([1, 2, 1], budget=3)
    assert first == second


def test_k_move_provenance_is_required() -> None:
    broken = contract(move_families=[{
        "name": "mutation",
        "decision_component": "random",
        "description": "change something",
        "rationale": "unknown",
        "applicability": "all",
        "expected_effect": "unknown",
    }])
    report = validate_improvement_contract(broken)
    assert report["status"] == "IMPROVEMENT_CONTRACT_INCOMPLETE"
    assert any("decision semantics" in error for error in report["errors"])


def test_l_exact_optimum_exception() -> None:
    result = exact_optimum_exception(proof_available=True, valid_bound=True)
    assert result["exact_optimum_exception"] is True
    assert result["structured_improvement_required"] is False


def test_detection_and_reviewer_codes() -> None:
    detection = is_improvement_candidate(
        feasible_incumbent_available=True,
        no_proven_exact_optimum=True,
        quality_may_improve_via_discrete_changes=True,
        meaningful_moves_available=True,
        candidate_can_be_realized_feasibly=True,
    )
    assert detection["structured_improvement_required"] is True
    review = review_improvement_claim(
        "We improved using surrogate and penalty.",
        contract=contract(),
        trace=None,
    )
    codes = {item["code"] for item in review["findings"]}
    assert {"SURROGATE_IMPROVEMENT_CLAIM", "INFEASIBLE_NEIGHBOR_AS_VALID", "IMPROVEMENT_EVIDENCE_MISSING"} <= codes
    trace_errors = validate_trace_record({"iteration": 1, "move_family": "random"})
    assert trace_errors
