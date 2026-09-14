"""Tests for robustness scenario execution."""

import pytest

from skill.scripts.robustness import run_robustness


def test_robustness_compares_named_scenarios() -> None:
    """The first scenario should act as a documented baseline."""
    result = run_robustness(lambda x: x * 2, {"baseline": 2, "noise": 2.2})
    assert result["baseline_value"] == 4.0
    assert result["results"][1]["relative_change"] == pytest.approx(0.1)


def test_robustness_requires_scenarios() -> None:
    """An empty scenario collection has no meaningful baseline."""
    with pytest.raises(ValueError):
        run_robustness(lambda x: x, {})
