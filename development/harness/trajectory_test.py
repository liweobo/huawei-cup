"""Layer A deterministic trajectory benchmark.

This runner tests control-plane behavior only: trigger, route, lightweight
state transitions, safety gates, and fixture-declared expectations. It does not
generate or evaluate assistant answers.
"""

from __future__ import annotations

import json
import hashlib
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from behavior_contract_test import CONTRACTS
from router import classify, load_routing, should_trigger


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "development/benchmarks" / "trajectories"
PHASE_BY_ROUTE = {
    "select_problem": "selection",
    "analyze_problem": "problem_analysis",
    "audit_data": "data",
    "build_baseline": "baseline",
    "design_model": "modeling",
    "run_experiment": "experiment",
    "validate_model": "validation",
    "write_paper": "writing",
    "reviewer": "review",
    "final_check": "submission",
}
VALID_STATUS = {"NOT STARTED", "IN PROGRESS", "COMPLETE", "BLOCKED"}
RISK_TERMS = (
    "数据泄漏",
    "未来数据进入训练集",
    "时间序列随机",
    "target leakage",
    "过拟合",
    "违反约束",
    "最优解不满足约束",
    "论文结果和代码对不上",
    "摘要和正文不一致",
    "unverified",
)
EVIDENCE_NUMBER_KEYS = {"accuracy", "rmse", "objective_value", "improvement", "improvement_pct", "metrics"}


def _load_trajectories() -> list[dict[str, Any]]:
    trajectories: list[dict[str, Any]] = []
    required = {"id", "name", "kind", "source", "source_status", "problem_family", "initial_state", "turns"}
    required_turn = {"turn", "user", "expected_trigger", "expected_route", "expected_phase"}
    for path in sorted(FIXTURE_DIR.glob("*.yaml")):
        if path.name in {"schema.yaml", "schema.yml"}:
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"trajectory must be a mapping: {path}")
        missing = sorted(required - set(data))
        if missing:
            raise ValueError(f"trajectory {path.name} missing fields: {missing}")
        if data["kind"] not in {"historical", "synthetic"}:
            raise ValueError(f"trajectory {path.name} has invalid kind: {data['kind']!r}")
        if data["source_status"] not in {"ACCEPTED", "VERIFIED", "MISSING", "UNVERIFIED"}:
            raise ValueError(f"trajectory {path.name} has invalid source_status: {data['source_status']!r}")
        if not isinstance(data["turns"], list) or not data["turns"]:
            raise ValueError(f"trajectory {path.name} turns must be a non-empty list")
        seen_turns: set[str] = set()
        for index, turn in enumerate(data["turns"], start=1):
            if not isinstance(turn, dict):
                raise ValueError(f"trajectory {path.name} turn {index} must be a mapping")
            missing_turn = sorted(required_turn - set(turn))
            if missing_turn:
                raise ValueError(f"trajectory {path.name} turn {index} missing fields: {missing_turn}")
            turn_id = str(turn.get("turn", "")).strip()
            if turn_id in seen_turns:
                raise ValueError(f"trajectory {path.name} duplicate turn id: {turn_id}")
            seen_turns.add(turn_id)
        data["_path"] = str(path)
        trajectories.append(data)
    return trajectories


def _initial_state(initial: dict[str, Any] | None) -> dict[str, Any]:
    state = {
        "domain_context": None,
        "selected_problem": None,
        "current_phase": None,
        "status": "NOT STARTED",
        "p0_risks": [],
        "completed_routes": [],
        "last_route": None,
        "current_task": None,
        "blocked": False,
        "historical_coverage": False,
    }
    if initial:
        state.update(deepcopy(initial))
    state["p0_risks"] = list(state.get("p0_risks") or [])
    state["completed_routes"] = list(state.get("completed_routes") or [])
    return state


def _apply_updates(state: dict[str, Any], updates: dict[str, Any] | None) -> None:
    if not updates:
        return
    for key, value in updates.items():
        if key == "p0_risks_add":
            state.setdefault("p0_risks", []).extend(item for item in value if item not in state["p0_risks"])
        elif key == "p0_risks_resolve":
            state["p0_risks"] = [item for item in state.get("p0_risks", []) if item not in value]
        elif key == "completed_routes_add":
            state.setdefault("completed_routes", []).extend(item for item in value if item not in state["completed_routes"])
        else:
            state[key] = deepcopy(value)


def _route_transition_valid(previous: str | None, current: str | None, state: dict[str, Any]) -> bool:
    if previous is None or current is None:
        return True
    if previous == current:
        return True
    if previous == "final_check" and current == "select_problem" and not state.get("p0_risks"):
        return False
    return True


def _risk_detected(user: str) -> bool:
    query = user.lower()
    return any(term.lower() in query for term in RISK_TERMS)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_source_record(source_path: Path, expected_status: str) -> list[str]:
    """Validate a local historical source record and its raw artifact hashes."""
    errors: list[str] = []
    if not source_path.exists() or not source_path.is_file():
        return [f"source artifact does not exist: {source_path}"]
    try:
        record = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"source record cannot be read: {exc}"]
    if not isinstance(record, dict):
        return ["source record must be a mapping"]
    status = record.get("benchmark_source_status")
    if status != expected_status:
        errors.append(f"benchmark_source_status expected {expected_status}, got {status!r}")
    if expected_status == "ACCEPTED":
        if record.get("artifact_origin") != "USER_PROVIDED":
            errors.append("ACCEPTED source requires artifact_origin: USER_PROVIDED")
        if record.get("official_provenance") == "OFFICIAL_DIRECT":
            errors.append("USER_PROVIDED source must not claim official_provenance: OFFICIAL_DIRECT")
    artifacts = record.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("source record requires a non-empty artifacts manifest")
        return errors
    seen_ids: set[str] = set()
    for index, artifact in enumerate(artifacts, start=1):
        if not isinstance(artifact, dict):
            errors.append(f"artifact {index} must be a mapping")
            continue
        artifact_id = str(artifact.get("id", "")).strip()
        if not artifact_id:
            errors.append(f"artifact {index} has no id")
        elif artifact_id in seen_ids:
            errors.append(f"duplicate artifact id: {artifact_id}")
        seen_ids.add(artifact_id)
        raw_path = str(artifact.get("raw_path", "")).strip()
        if not raw_path:
            errors.append(f"artifact {artifact_id or index} has no raw_path")
            continue
        target = (source_path.parent / raw_path).resolve()
        if not target.exists() or not target.is_file():
            errors.append(f"raw artifact does not exist: {raw_path}")
            continue
        expected_hash = str(artifact.get("sha256", "")).lower()
        if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            errors.append(f"artifact {artifact_id or index} has invalid SHA256")
            continue
        actual_hash = _sha256(target)
        if actual_hash != expected_hash:
            errors.append(
                f"artifact hash mismatch for {artifact_id or raw_path}: expected {expected_hash}, got {actual_hash}"
            )
    return errors


def _source_gate(trajectory: dict[str, Any]) -> tuple[bool, str | None]:
    """Require traceable provenance before a trajectory counts as historical."""
    if trajectory.get("kind") != "historical":
        return True, None
    source_status = trajectory.get("source_status")
    if source_status not in {"ACCEPTED", "VERIFIED"}:
        return False, "historical source_status must be ACCEPTED or VERIFIED"
    source = str(trajectory.get("source", "")).strip()
    if source_status == "VERIFIED" and source.startswith(("https://", "http://")):
        return True, None
    target = (ROOT / "development" / source).resolve() if str(source).startswith("benchmarks/") else (ROOT / source).resolve()
    errors = validate_source_record(target, str(source_status))
    if errors:
        return False, "; ".join(errors)
    return True, None


def _validate_route_assets(route: str, routing: dict[str, Any]) -> list[str]:
    """Check that a routed turn is backed by a workflow, reads and contract."""
    failures: list[str] = []
    config = routing.get("routes", {}).get(route)
    if not config:
        return [f"route has no routing.yaml entry: {route}"]
    workflow = (ROOT / "skill" / config.get("workflow", "")).resolve()
    if not workflow.exists():
        failures.append(f"route workflow missing: {workflow}")
    for value in config.get("required_reads", []):
        path = (ROOT / "skill" / value).resolve()
        if not path.exists():
            failures.append(f"route Required Read missing: {path}")
    if route not in CONTRACTS:
        failures.append(f"route lacks Static Behavior Contract: {route}")
    return failures


def _validate_state(state: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if state.get("status") not in VALID_STATUS:
        failures.append(f"invalid status: {state.get('status')!r}")
    if state.get("current_phase") not in set(PHASE_BY_ROUTE.values()) | {None}:
        failures.append(f"invalid phase: {state.get('current_phase')!r}")
    if state.get("status") == "BLOCKED" and not state.get("blocked"):
        failures.append("BLOCKED status must set blocked=true")
    if state.get("blocked") and state.get("status") != "BLOCKED":
        failures.append("blocked=true requires status=BLOCKED")
    if state.get("status") == "COMPLETE" and state.get("p0_risks"):
        failures.append("COMPLETE is not allowed while P0 risks remain")
    if state.get("experiment_status") == "COMPLETE" and not state.get("observed_evidence"):
        failures.append("experiment COMPLETE requires observed_evidence")
    if any(state.get(key) is not None for key in EVIDENCE_NUMBER_KEYS) and not state.get("observed_evidence"):
        failures.append("experiment numbers require observed_evidence")
    if state.get("historical_coverage") and state.get("source_status") not in {"ACCEPTED", "VERIFIED"}:
        failures.append("historical coverage requires ACCEPTED or VERIFIED source")
    return failures


def _format_state(state: dict[str, Any]) -> str:
    compact = {key: state.get(key) for key in ("domain_context", "selected_problem", "current_phase", "status", "p0_risks", "blocked")}
    return json.dumps(compact, ensure_ascii=False, sort_keys=True)


def run_trajectory(trajectory: dict[str, Any], routing: dict[str, Any]) -> dict[str, Any]:
    state = _initial_state(trajectory.get("initial_state"))
    state["kind"] = trajectory.get("kind")
    state["source_status"] = trajectory.get("source_status")
    source_gate_ok, source_gate_reason = _source_gate(trajectory)
    state["historical_coverage"] = bool(source_gate_ok and trajectory.get("kind") == "historical")
    failures: list[dict[str, Any]] = []
    transitions = 0
    valid_transitions = 0
    trigger_correct = 0
    route_correct = 0
    context_turns = 0
    context_correct = 0
    risk_turns = 0
    risk_correct = 0
    previous_route: str | None = None
    previous_expected_route: str | None = None
    stable_run = 0
    longest_stable = 0
    covered_routes: set[str] = set()
    results: list[dict[str, Any]] = []

    for turn in trajectory.get("turns", []):
        user = str(turn.get("user", ""))
        before = deepcopy(state)
        expected_trigger = bool(turn.get("expected_trigger"))
        expected_route = turn.get("expected_route")
        expected_phase = turn.get("expected_phase")
        actual_trigger = should_trigger(user, state)
        actual_route = classify(user, state).route if actual_trigger else None
        evidence = classify(user, state).evidence if actual_trigger else ()
        if actual_trigger == expected_trigger:
            trigger_correct += 1
        else:
            failures.append({"turn": turn.get("turn"), "user": user, "reason": f"trigger expected {expected_trigger}, got {actual_trigger}"})
        if expected_trigger and actual_route == expected_route:
            route_correct += 1
        elif expected_trigger:
            failures.append({"turn": turn.get("turn"), "user": user, "reason": f"route expected {expected_route!r}, got {actual_route!r}"})
        if state.get("domain_context") and not re.search(r"数学建模|数模|MCM|ICM|mathematical modeling|mathematical modelling", user, re.IGNORECASE):
            context_turns += 1
            if actual_trigger:
                context_correct += 1
        if actual_route:
            covered_routes.add(actual_route)
            for reason in _validate_route_assets(actual_route, routing):
                failures.append({"turn": turn.get("turn"), "user": user, "reason": reason})
            if previous_expected_route is not None and expected_route is not None:
                transitions += 1
                valid = (
                    previous_route == previous_expected_route
                    and actual_route == expected_route
                    and _route_transition_valid(previous_route, actual_route, state)
                )
                valid_transitions += int(valid)
            else:
                valid = True
            if previous_route is not None and not _route_transition_valid(previous_route, actual_route, state):
                failures.append({"turn": turn.get("turn"), "user": user, "reason": "suspicious route regression"})
            previous_route = actual_route
        if expected_route is not None:
            previous_expected_route = expected_route
        _apply_updates(state, turn.get("state_updates"))
        if actual_route and not turn.get("state_updates", {}).get("current_phase"):
            state["current_phase"] = PHASE_BY_ROUTE[actual_route]
        if actual_route and actual_route not in state["completed_routes"]:
            state["completed_routes"].append(actual_route)
        state["last_route"] = actual_route
        state["current_task"] = user
        if _risk_detected(user) and not state.get("p0_risks") and turn.get("risk_policy") == "auto_add":
            state["p0_risks"] = ["risk detected; fixture omitted explicit p0_risks_add"]
        if state.get("p0_risks") and turn.get("risk_policy") == "block":
            state["blocked"] = True
            state["status"] = "BLOCKED"
        if turn.get("state_updates", {}).get("blocked") is False and not state.get("p0_risks"):
            state["status"] = "IN PROGRESS"
            state["blocked"] = False
        if _risk_detected(user):
            risk_turns += 1
            risk_ok = (
                actual_trigger
                and actual_route in {"audit_data", "validate_model", "reviewer", "final_check"}
                and state.get("p0_risks")
            )
            if risk_ok:
                risk_correct += 1
            else:
                failures.append({"turn": turn.get("turn"), "user": user, "reason": "risk turn did not produce a safety route and P0 state"})
        if expected_phase is not None and state.get("current_phase") != expected_phase:
            failures.append({"turn": turn.get("turn"), "user": user, "reason": f"phase expected {expected_phase!r}, got {state.get('current_phase')!r}"})
        if turn.get("assertions", {}).get("no_fake_experiment") and state.get("experiment_status") == "COMPLETE" and not state.get("observed_evidence"):
            failures.append({"turn": turn.get("turn"), "user": user, "reason": "fake experiment completion"})
        for reason in _validate_state(state):
            failures.append({"turn": turn.get("turn"), "user": user, "reason": reason})
        ok = not any(item.get("turn") == turn.get("turn") for item in failures)
        stable_run = stable_run + 1 if ok else 0
        longest_stable = max(longest_stable, stable_run)
        results.append({
            "turn": turn.get("turn"),
            "user": user,
            "expected_trigger": expected_trigger,
            "trigger": actual_trigger,
            "expected_route": expected_route,
            "route": actual_route,
            "expected_phase": expected_phase,
            "phase": state.get("current_phase"),
            "before": before,
            "after": deepcopy(state),
            "evidence": list(evidence),
            "ok": ok,
        })

    expected_routes = set(trajectory.get("expected_route_coverage", []))
    if expected_routes - covered_routes:
        failures.append({"turn": None, "user": "", "reason": f"missing route coverage: {sorted(expected_routes - covered_routes)}"})
    if not source_gate_ok:
        failures.append({"turn": None, "user": "", "reason": f"historical source gate: {source_gate_reason}"})
    total = len(trajectory.get("turns", []))
    triggered = sum(1 for item in results if item["trigger"])
    return {
        "id": trajectory.get("id"),
        "kind": trajectory.get("kind"),
        "source_status": trajectory.get("source_status"),
        "historical_coverage": state.get("historical_coverage", False),
        "problem_family": trajectory.get("problem_family"),
        "turns": total,
        "trigger_correct": trigger_correct,
        "route_correct": route_correct,
        "triggered_turns": triggered,
        "context_turns": context_turns,
        "context_correct": context_correct,
        "transitions": transitions,
        "valid_transitions": valid_transitions,
        "risk_turns": risk_turns,
        "risk_correct": risk_correct,
        "route_coverage": sorted(covered_routes),
        "longest_stable": longest_stable,
        "failures": failures,
        "results": results,
    }


def _print_result(result: dict[str, Any]) -> None:
    for item in result["results"]:
        prefix = "PASS" if item["ok"] else "FAIL"
        print(f"{prefix} | trajectory={result['id']} | turn={item['turn']}")
        print(f"  trigger={item['trigger']} route={item['route']} phase={item['phase']}")
        if not item["ok"]:
            print(f"  user={item['user']}")
            print(f"  expected_trigger={item['expected_trigger']} actual_trigger={item['trigger']}")
            print(f"  expected_route={item['expected_route']} actual_route={item['route']}")
            print(f"  expected_phase={item['expected_phase']} actual_phase={item['phase']}")
            print(f"  state_before={_format_state(item['before'])}")
            print(f"  state_after={_format_state(item['after'])}")
            print(f"  evidence={item['evidence']}")
    for failure in result["failures"]:
        if failure.get("turn") is None:
            print(f"FAIL | trajectory={result['id']} | {failure['reason']}")


def main() -> int:
    routing = load_routing()
    trajectories = _load_trajectories()
    if not trajectories:
        print("No trajectory fixtures found")
        return 1
    all_results = []
    for trajectory in trajectories:
        result = run_trajectory(trajectory, routing)
        _print_result(result)
        all_results.append(result)
    total_turns = sum(item["turns"] for item in all_results)
    trigger_correct = sum(item["trigger_correct"] for item in all_results)
    triggered = sum(item["triggered_turns"] for item in all_results)
    route_correct = sum(item["route_correct"] for item in all_results)
    context_turns = sum(item["context_turns"] for item in all_results)
    context_correct = sum(item["context_correct"] for item in all_results)
    transitions = sum(item["transitions"] for item in all_results)
    valid_transitions = sum(item["valid_transitions"] for item in all_results)
    risk_turns = sum(item["risk_turns"] for item in all_results)
    risk_correct = sum(item["risk_correct"] for item in all_results)
    route_coverage = sorted(set().union(*(set(item["route_coverage"]) for item in all_results)))
    failures = sum(len(item["failures"]) for item in all_results)
    historical = sum(1 for item in all_results if item["kind"] == "historical" and item["historical_coverage"])
    print("\nTrajectory Benchmark Metrics (Layer A)")
    print(f"Trigger Accuracy: {trigger_correct}/{total_turns} ({trigger_correct / total_turns:.1%})")
    print(f"Route Accuracy: {route_correct}/{triggered} ({route_correct / triggered:.1%})" if triggered else "Route Accuracy: n/a")
    print(f"Context Retention: {context_correct}/{context_turns} ({context_correct / context_turns:.1%})" if context_turns else "Context Retention: n/a")
    print(f"Transition Accuracy: {valid_transitions}/{transitions} ({valid_transitions / transitions:.1%})" if transitions else "Transition Accuracy: n/a")
    print(f"Risk Detection: {risk_correct}/{risk_turns} ({risk_correct / risk_turns:.1%})" if risk_turns else "Risk Detection: n/a")
    print(f"Route Coverage: {len(route_coverage)}/10 ({', '.join(route_coverage)})")
    print(f"Longest Stable Trajectory: {max(item['longest_stable'] for item in all_results)} turns")
    print(f"Historical Benchmark Coverage: {historical} ACCEPTED/VERIFIED historical trajectories")
    print(f"Trajectory Benchmark: {'PASS' if failures == 0 and len(route_coverage) == 10 else 'FAIL'} ({len(all_results)} trajectories, {total_turns} turns)")
    return 1 if failures or len(route_coverage) != 10 else 0


if __name__ == "__main__":
    sys.exit(main())
