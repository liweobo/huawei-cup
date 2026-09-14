"""Tests for one-factor sensitivity analysis."""

import pytest

from skill.scripts.sensitivity import run_sensitivity


def test_sensitivity_returns_both_directions() -> None:
    """Each parameter/delta combination should have up and down records."""
    result = run_sensitivity(lambda a, b: a + b, {"a": 10.0, "b": 5.0}, deltas=[0.1])
    assert result["baseline"] == 15.0
    assert len(result["results"]) == 4
    assert {row["direction"] for row in result["results"]} == {"up", "down"}


def test_sensitivity_supports_custom_evaluation() -> None:
    """A model may return a structured result evaluated by a callback."""
    result = run_sensitivity(
        lambda scale: {"score": scale**2},
        {"scale": 2.0},
        deltas=[0.05],
        evaluate_fn=lambda output: output["score"],
        stability_threshold=0.2,
    )
    assert result["baseline"] == 4.0
    assert len(result["results"]) == 2


def test_sensitivity_rejects_invalid_parameters() -> None:
    """Empty, non-numeric and negative-delta inputs should fail explicitly."""
    with pytest.raises(ValueError):
        run_sensitivity(lambda: 1, {})
    with pytest.raises(TypeError):
        run_sensitivity(lambda a: 1, {"a": "bad"})
    with pytest.raises(ValueError):
        run_sensitivity(lambda a: a, {"a": 1.0}, deltas=[-0.1])


def test_sensitivity_zero_baseline_does_not_fabricate_relative_change() -> None:
    """A zero baseline must produce undefined relative changes by default."""
    result = run_sensitivity(lambda a: a - 1.0, {"a": 1.0}, deltas=[0.1])
    assert result["baseline"] == 0.0
    assert result["relative_change_defined"] is False
    assert result["stability_judgement"] == "not_assessed"
    assert all(row["relative_change"] is None for row in result["results"])
    assert all(row["absolute_change"] != 0 for row in result["results"])


def test_sensitivity_zero_baseline_accepts_explicit_scale() -> None:
    """A caller may provide a meaningful normalization scale explicitly."""
    result = run_sensitivity(
        lambda a: a - 1.0,
        {"a": 1.0},
        deltas=[0.1],
        normalization_scale=2.0,
    )
    assert result["relative_change_defined"] is True
    assert all(row["relative_change"] is not None for row in result["results"])
