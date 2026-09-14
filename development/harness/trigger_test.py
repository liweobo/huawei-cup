"""Trigger-boundary tests for the V2 Skill."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from router import classify, should_trigger


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    """Run positive and negative trigger fixtures."""
    cases = json.loads((ROOT / "development/harness/fixtures/trigger_cases.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in cases:
        state = case.get("state")
        actual = should_trigger(case["text"], state)
        actual_route = classify(case["text"], state).route if "expected_route" in case else None
        ok = actual == case["should_trigger"] and actual_route == case.get("expected_route")
        status = "PASS" if ok else "FAIL"
        route_output = f", route={actual_route}" if "expected_route" in case else ""
        print(f"{status} | {case['text']} -> trigger={actual}{route_output}")
        if not ok:
            failures.append(case["text"])
    print(f"\nTrigger Boundary Test: {len(cases) - len(failures)}/{len(cases)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
