"""Generic A-L regressions for the stateful scheduling search contract."""

from __future__ import annotations

import copy

from skill.scripts.stateful_scheduling import (
    feasible_decoder_errors,
    is_stateful_scheduling,
    legal_action_errors,
    review_stateful_claim,
    select_feasible_incumbent,
    transition_errors,
    validate_stateful_contract,
)


def contract(**overrides):
    value = {
        "problem_type": "STATEFUL_SCHEDULING",
        "state_variables": ["time", "machine_busy", "buffer", "completed"],
        "resources": ["machine"],
        "queues_or_buffers": ["buffer"],
        "time_representation": "integer_epochs",
        "terminal_condition": "all jobs completed",
        "legal_action_definition": "job may start only when machine is free",
        "transition_definition": "occupies machine and updates buffer",
        "hard_invariants": ["machine_capacity", "buffer_capacity", "precedence"],
        "objective_definition": "realized completion time",
        "candidate_representation": "STATE_COUPLED",
        "search_mode": "beam",
        "decoder_required": False,
        "feasibility_mode": "BY_CONSTRUCTION",
        "status": "PASS",
    }
    value.update(overrides)
    return value


def test_a_dynamic_buffer_machine_is_detected() -> None:
    result = is_stateful_scheduling(
        dynamically_evolving_feasibility=True,
        blocking_queue_or_finite_buffer=True,
        dynamic_resource_occupancy=True,
    )
    assert result["problem_type"] == "STATEFUL_SCHEDULING"
    assert result["stateful_scheduling_detected"] is True


def test_b_static_assignment_does_not_activate_stateful_scheduling() -> None:
    result = is_stateful_scheduling()
    assert result["problem_type"] == "OTHER"
    assert result["stateful_scheduling_detected"] is False


def test_c_sequence_only_without_decoder_is_rejected() -> None:
    report = validate_stateful_contract(
        contract(
            candidate_representation="SEQUENCE_ONLY",
            decoder_required=False,
            feasibility_mode="POST_HOC_ONLY",
        )
    )
    assert report["status"] == "STATE_SEARCH_UNVERIFIED"
    assert report["eligible_for_formal_search"] is False
    assert any("SEQUENCE_ONLY" in error for error in report["errors"])


def test_d_feasible_decoder_is_accepted() -> None:
    report = validate_stateful_contract(
        contract(
            candidate_representation="SEQUENCE_WITH_FEASIBLE_DECODER",
            decoder_required=True,
            feasibility_mode="DECODE_AND_VERIFY",
        )
    )
    assert report["status"] == "PASS"
    assert report["eligible_for_formal_search"] is True


class State:
    def __init__(self, machine_busy=False, buffer=(), completed=()):
        self.machine_busy = machine_busy
        self.buffer = tuple(buffer)
        self.completed = tuple(completed)


def machine_legal(state: State):
    actions = []
    if not state.machine_busy and state.buffer:
        actions.append(("start", state.buffer[0]))
    if state.buffer:
        actions.append(("hold",))
    return actions


def machine_transition(state: State, action):
    if action[0] == "hold":
        return copy.deepcopy(state)
    _, job = action
    return State(
        machine_busy=True,
        buffer=tuple(item for item in state.buffer if item != job),
        completed=state.completed,
    )


def test_e_busy_machine_rejects_second_start_before_expansion() -> None:
    state = State(machine_busy=True, buffer=("A",))
    assert legal_action_errors(state, ("start", "A"), legal_actions=machine_legal) == [
        "ILLEGAL_ACTION: action is not legal in the current state"
    ]
    assert transition_errors(
        state,
        ("start", "A"),
        legal_actions=machine_legal,
        transition=machine_transition,
        invariants=[lambda candidate: not candidate.machine_busy or candidate.buffer],
    )


def test_f_buffer_overflow_is_rejected_at_transition() -> None:
    state = State(buffer=("A",))
    errors = transition_errors(
        state,
        ("add", "B"),
        legal_actions=lambda _: [("add", "B")],
        transition=lambda current, action: State(buffer=current.buffer + (action[1],)),
        invariants=[lambda candidate: len(candidate.buffer) <= 1],
    )
    assert errors == ["HARD_INVARIANT_VIOLATION[0]"]


def test_g_precedence_hides_b_until_a_completed() -> None:
    state = State(completed=())

    def legal(current):
        actions = []
        if "A" not in current.completed:
            actions.append(("do", "A"))
        elif "B" not in current.completed:
            actions.append(("do", "B"))
        return actions

    assert ("do", "B") not in legal(state)
    errors = legal_action_errors(state, ("do", "B"), legal_actions=legal)
    assert errors == ["ILLEGAL_ACTION: action is not legal in the current state"]


def test_h_illegal_state_is_invalid_not_penalized() -> None:
    state = State(machine_busy=True, buffer=("A",))
    errors = transition_errors(
        state,
        ("start", "A"),
        legal_actions=lambda _: [],
        transition=machine_transition,
        invariants=[lambda _: True],
    )
    assert errors and errors[0].startswith("ILLEGAL_ACTION")
    # There is no objective adjustment path in the state gate: invalid
    # candidates are rejected rather than returned with a large penalty.


def test_i_infeasible_high_score_cannot_beat_feasible_incumbent() -> None:
    result = select_feasible_incumbent(
        [
            {"candidate_id": "A", "feasible": False, "objective": 100},
            {"candidate_id": "B", "feasible": True, "objective": 80},
        ],
        sense="maximize",
    )
    assert result["incumbent"]["candidate_id"] == "B"


def test_j_surrogate_cannot_replace_realized_objective() -> None:
    candidate = {
        "candidate_id": "A",
        "feasible": True,
        "surrogate_objective": 100,
        "realized_objective": 40,
    }
    result = select_feasible_incumbent([candidate], objective_key="realized_objective")
    assert result["incumbent"]["realized_objective"] == 40
    findings = review_stateful_claim(
        "候选排列得分最高，因此为最佳调度",
        contract=contract(),
        candidate={"surrogate_objective": 100, "realized_objective": None},
    )
    assert any(item["code"] == "SURROGATE_OBJECTIVE_AS_FINAL" for item in findings["findings"])


def test_k_terminal_completeness_is_required() -> None:
    # Terminal is a caller-provided state predicate; an incomplete state must
    # not be wrapped as a feasible solution.
    incomplete = {"completed": [], "terminal": False}
    assert not incomplete["terminal"]
    result = select_feasible_incumbent(
        [{"candidate_id": "partial", "feasible": incomplete["terminal"], "objective": 1}]
    )
    assert result["status"] == "NO_FEASIBLE_INCUMBENT"


def test_l_independent_audit_remains_a_separate_requirement() -> None:
    report = validate_stateful_contract(contract())
    assert report["status"] == "PASS"
    # Even BY_CONSTRUCTION contracts expose no claim that independent audit
    # has been performed; the workflow must still consume an external audit.
    assert "independent_audit" not in report


def test_feasible_decoder_generates_realized_schedule() -> None:
    def decoder(sequence):
        return {"order": list(sequence), "feasible": True, "objective": 42}

    assert feasible_decoder_errors(
        ["A", "B"],
        decoder=decoder,
        hard_constraints=lambda schedule: schedule["feasible"],
        objective=lambda schedule: schedule["objective"],
    ) == []
    assert feasible_decoder_errors(
        ["A", "B"],
        decoder=None,
        hard_constraints=lambda _: True,
        objective=lambda _: 0,
    ) == ["FEASIBLE_DECODER_REQUIRED"]


def test_reviewer_state_decoupled_and_penalty_codes() -> None:
    decoupled = review_stateful_claim(
        "\u6211\u4eec\u5148\u4f18\u5316\u7406\u60f3\u8f66\u8f86\u987a\u5e8f\uff0c"
        "\u4e4b\u540e\u518d\u5c1d\u8bd5\u5c06\u5176\u6620\u5c04\u5230\u5b9e\u9645\u8c03\u5ea6\u3002",
        contract=contract(candidate_representation="SEQUENCE_ONLY", decoder_required=False),
    )
    assert decoupled["findings"][0]["code"] == "STATE_FEASIBILITY_DECOUPLED"
    penalty = review_stateful_claim(
        "\u975e\u6cd5\u52a8\u4f5c\u589e\u52a0\u4e00\u4e2a\u5f88\u5927\u7684 penalty\u3002",
        contract=contract(),
    )
    assert any(item["code"] == "HARD_CONSTRAINT_AS_PENALTY" for item in penalty["findings"])
