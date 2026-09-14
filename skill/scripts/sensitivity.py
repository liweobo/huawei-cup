"""One-factor parameter sensitivity analysis."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
from typing import Any


def run_sensitivity(
    model_fn: Callable[..., Any],
    parameters: Mapping[str, float],
    deltas: Sequence[float] = (0.05, 0.10, 0.20),
    evaluate_fn: Callable[[Any], float] | None = None,
    *,
    stability_threshold: float = 0.10,
    normalization_scale: float | None = None,
) -> dict[str, Any]:
    """Perturb parameters and assess changes without inventing a zero baseline.

    When the evaluated baseline is zero, relative change is undefined unless
    the caller supplies a positive ``normalization_scale`` with domain meaning.
    Absolute change is always reported.
    """
    if not parameters:
        raise ValueError("parameters cannot be empty")
    if any(not isinstance(value, (int, float)) for value in parameters.values()):
        raise TypeError("sensitivity parameters must be numeric")
    if not deltas or any(delta < 0 for delta in deltas):
        raise ValueError("deltas must be a non-empty sequence of non-negative values")
    if normalization_scale is not None and normalization_scale <= 0:
        raise ValueError("normalization_scale must be positive when provided")
    evaluate = evaluate_fn or (lambda result: float(result))
    baseline = float(evaluate(model_fn(**dict(parameters))))
    relative_change_defined = baseline != 0 or normalization_scale is not None
    baseline_scale = normalization_scale if normalization_scale is not None else abs(baseline)
    rows: list[dict[str, Any]] = []
    for name, value in parameters.items():
        for delta in deltas:
            for direction in (-1, 1):
                changed = dict(parameters)
                changed[name] = value * (1 + direction * delta)
                result = float(evaluate(model_fn(**changed)))
                absolute_change = result - baseline
                relative_change = (
                    absolute_change / baseline_scale
                    if relative_change_defined and baseline_scale > 0
                    else None
                )
                rows.append({
                    "parameter": name,
                    "delta": float(delta),
                    "direction": "down" if direction < 0 else "up",
                    "value": changed[name],
                    "result": result,
                    "absolute_change": absolute_change,
                    "relative_change": relative_change,
                    "relative_change_defined": relative_change is not None,
                    "stable": abs(relative_change) <= stability_threshold if relative_change is not None else None,
                })
    assessed = [row["stable"] for row in rows if row["stable"] is not None]
    return {
        "baseline": baseline,
        "normalization_scale": normalization_scale,
        "relative_change_defined": relative_change_defined,
        "stability_threshold": stability_threshold,
        "results": rows,
        "stability_judgement": (
            "not_assessed" if not assessed else "stable" if all(assessed) else "sensitive"
        ),
    }


def main() -> None:
    """Run a small sensitivity demo."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if not args.demo:
        parser.error("use --demo or import run_sensitivity")
    print(run_sensitivity(lambda a, b: a * b, {"a": 10.0, "b": 2.0}))


if __name__ == "__main__":
    main()
