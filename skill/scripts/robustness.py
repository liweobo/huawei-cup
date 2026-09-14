"""Named-scenario runner for a basic robustness check.

This module does not implement bootstrap, adversarial testing or a general
Monte Carlo engine.  It compares user-supplied scenarios and leaves scenario
design and conclusion validity to the modelling workflow.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
from typing import Any


def run_robustness(
    model_fn: Callable[[Any], Any],
    scenarios: Mapping[str, Any] | Sequence[tuple[str, Any]],
    evaluate_fn: Callable[[Any], float] | None = None,
) -> dict[str, Any]:
    """Evaluate a model across named scenarios and compare to the first scenario.

    The first item is the documented baseline.  Results are scenario-based
    diagnostics, not proof of robustness outside the supplied scenarios.
    """
    items = list(scenarios.items()) if isinstance(scenarios, Mapping) else list(scenarios)
    if not items:
        raise ValueError("at least one scenario is required")
    evaluate = evaluate_fn or (lambda result: float(result))
    baseline_name, baseline_input = items[0]
    baseline_value = float(evaluate(model_fn(baseline_input)))
    scale = abs(baseline_value) or 1.0
    results = []
    for name, scenario in items:
        value = float(evaluate(model_fn(scenario)))
        results.append({
            "scenario": name,
            "value": value,
            "absolute_change": value - baseline_value,
            "relative_change": (value - baseline_value) / scale,
        })
    return {"baseline_scenario": baseline_name, "baseline_value": baseline_value, "results": results}


def main() -> None:
    """Run a small robustness demo."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if not args.demo:
        parser.error("use --demo or import run_robustness")
    print(run_robustness(lambda x: x * x, {"baseline": 2, "noise": 2.2, "extreme": 4}))


if __name__ == "__main__":
    main()
