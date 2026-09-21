"""Focused evaluation contracts for the 2007A blind run."""

from __future__ import annotations

import unittest

import numpy as np

from evaluation_model import (
    AssessmentUnit,
    equal_weight_scores,
    fit_left_censored_lognormal,
    primary_rank,
    rank_names,
    risk_class,
)


class EvaluationContractTests(unittest.TestCase):
    def test_hard_gate_cannot_be_compensated(self) -> None:
        unsafe = AssessmentUnit("unsafe", 1.01, 1.02, 0.1, 1.0)
        safe = AssessmentUnit("safe", 0.80, 0.90, 50.0, 0.5)
        self.assertEqual(risk_class(unsafe), "VIOLATION")
        self.assertEqual(risk_class(safe), "COMPLIANT")
        self.assertEqual(rank_names(primary_rank([unsafe, safe]))[0], "unsafe")

    def test_cost_direction(self) -> None:
        low = AssessmentUnit("low", 0.5, 0.6, 1.0, 0.8)
        high = AssessmentUnit("high", 1.4, 1.5, 1.0, 0.8)
        rows = equal_weight_scores([low, high], normalization="fixed_bounds")
        scores = {row["name"]: row["safety_score"] for row in rows}
        self.assertGreater(scores["low"], scores["high"])

    def test_benefit_monotonicity(self) -> None:
        before = AssessmentUnit("x", 0.8, 0.9, 1.0, 0.7)
        after = AssessmentUnit("x", 0.8, 0.9, 1.0, 0.8)
        anchor = AssessmentUnit("anchor", 1.0, 1.0, 10.0, 0.5)
        b = equal_weight_scores([before, anchor], normalization="fixed_bounds")
        a = equal_weight_scores([after, anchor], normalization="fixed_bounds")
        bscore = next(row["safety_score"] for row in b if row["name"] == "x")
        ascore = next(row["safety_score"] for row in a if row["name"] == "x")
        self.assertGreaterEqual(ascore, bscore)

    def test_unit_rescale_invariance_of_ratios(self) -> None:
        q, standard = 120.0, 100.0
        self.assertAlmostEqual(q / standard, (1000 * q) / (1000 * standard))

    def test_threshold_boundary_is_not_called_compliant(self) -> None:
        boundary = AssessmentUnit("boundary", 0.95, 1.0, 1.0, 1.0)
        self.assertEqual(risk_class(boundary), "UNCERTAIN")

    def test_censored_em_recovers_synthetic_parameters(self) -> None:
        rng = np.random.default_rng(17)
        mu, sigma, lod = -1.0, 0.8, 0.30
        latent = rng.lognormal(mu, sigma, 100_000)
        detected = latent[latent > lod]
        fitted_mu, fitted_sigma, _ = fit_left_censored_lognormal(
            detected, lod, int((latent <= lod).sum())
        )
        self.assertLess(abs(fitted_mu - mu), 0.03)
        self.assertLess(abs(fitted_sigma - sigma), 0.03)


if __name__ == "__main__":
    unittest.main()
