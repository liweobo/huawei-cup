"""Behavioral route checks using realistic and ambiguous competition requests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from router import classify


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    """Run fixture route cases and print a compact report."""
    cases = json.loads((ROOT / "development/harness/fixtures/routing_cases.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in cases:
        decision = classify(case["text"], case.get("state"))
        actual = decision.route
        ok = actual == case["expected"]
        status = "PASS" if ok else "FAIL"
        category = case.get("category", "uncategorized")
        print(f"{status} | {category} | {case['text']} -> {actual} (expected {case['expected']})")
        if not ok:
            failures.append(case["text"])
    counts: dict[str, int] = {}
    for case in cases:
        category = case.get("category", "uncategorized")
        counts[category] = counts.get(category, 0) + 1
    print(f"\nRouting Heuristic Test: {len(cases) - len(failures)}/{len(cases)} passed | {counts}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
