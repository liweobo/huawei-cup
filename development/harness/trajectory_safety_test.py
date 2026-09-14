"""Focused Layer A safety assertions for blocking states."""

from __future__ import annotations

import sys

from trajectory_test import _route_transition_valid, _validate_state


CASES = (
    ({"status": "COMPLETE", "p0_risks": ["leakage"]}, "COMPLETE is not allowed"),
    ({"status": "IN PROGRESS", "blocked": True}, "blocked=true requires"),
    ({"status": "BLOCKED", "blocked": False}, "BLOCKED status must"),
    ({"experiment_status": "COMPLETE"}, "experiment COMPLETE requires"),
    ({"historical_coverage": True, "source_status": "MISSING"}, "historical coverage requires"),
    ({"accuracy": 0.9}, "experiment numbers require"),
)


def main() -> int:
    failures: list[str] = []
    for state, expected in CASES:
        errors = _validate_state(state)
        ok = any(expected in error for error in errors)
        print(f"{'PASS' if ok else 'FAIL'} | {expected}")
        if not ok:
            failures.append(expected)
    regression_blocked = not _route_transition_valid("final_check", "select_problem", {"p0_risks": []})
    print(f"{'PASS' if regression_blocked else 'FAIL'} | final_check to select_problem requires a new risk")
    if not regression_blocked:
        failures.append("suspicious final_check regression")
    risk_allows_iteration = _route_transition_valid("final_check", "select_problem", {"p0_risks": ["problem-invalidated"]})
    print(f"{'PASS' if risk_allows_iteration else 'FAIL'} | new P0 risk permits problem reselection")
    if not risk_allows_iteration:
        failures.append("risk-driven problem reselection")
    total = len(CASES) + 2
    print(f"\nTrajectory Safety Test: {total - len(failures)}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
