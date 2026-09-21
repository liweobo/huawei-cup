"""Deterministic risk and ranking helpers for the 2007A blind-run scenario."""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist
from typing import Iterable

import numpy as np


TAIL_P = 0.99999
CRITERIA = ("point_ratio", "upper_ratio", "population_millions", "coverage")
DIRECTIONS = {
    "point_ratio": "COST",
    "upper_ratio": "COST",
    "population_millions": "COST",
    "coverage": "BENEFIT",
}
CLASS_PRIORITY = {"COMPLIANT": 0, "UNCERTAIN": 1, "VIOLATION": 2}


@dataclass(frozen=True)
class AssessmentUnit:
    name: str
    point_ratio: float
    upper_ratio: float
    population_millions: float
    coverage: float


def risk_class(unit: AssessmentUnit) -> str:
    """Hard/noncompensatory classification; thresholds are ratio=1 by definition."""
    if unit.point_ratio > 1.0:
        return "VIOLATION"
    if unit.upper_ratio >= 1.0:
        return "UNCERTAIN"
    return "COMPLIANT"


def primary_rank(units: Iterable[AssessmentUnit]) -> list[dict[str, object]]:
    """Rank monitoring priority without turning the rank into safety probability."""
    ordered = sorted(
        units,
        key=lambda u: (
            CLASS_PRIORITY[risk_class(u)],
            u.upper_ratio,
            u.point_ratio,
            u.population_millions,
        ),
        reverse=True,
    )
    rows = []
    for rank, unit in enumerate(ordered, 1):
        rows.append(
            {
                "rank": rank,
                "name": unit.name,
                "risk_class": risk_class(unit),
                "point_ratio": unit.point_ratio,
                "upper_ratio": unit.upper_ratio,
                "population_millions": unit.population_millions,
                "score_semantics": "LEXICOGRAPHIC_TRIAGE_PRIORITY_NOT_PROBABILITY",
            }
        )
    return rows


def _benefit_values(
    units: list[AssessmentUnit], criterion: str, normalization: str
) -> np.ndarray:
    values = np.array([getattr(unit, criterion) for unit in units], dtype=float)
    direction = DIRECTIONS[criterion]
    if normalization == "current_minmax":
        low, high = float(values.min()), float(values.max())
        if math.isclose(low, high):
            return np.ones_like(values)
        result = (values - low) / (high - low)
        return result if direction == "BENEFIT" else 1.0 - result
    if normalization == "fixed_bounds":
        bounds = {
            "point_ratio": (0.0, 1.5),
            "upper_ratio": (0.0, 1.6),
            "population_millions": (0.0, 60.0),
            "coverage": (0.0, 1.0),
        }
        low, high = bounds[criterion]
        clipped = np.clip((values - low) / (high - low), 0.0, 1.0)
        return clipped if direction == "BENEFIT" else 1.0 - clipped
    if normalization == "vector":
        norm = float(np.linalg.norm(values))
        if math.isclose(norm, 0.0):
            return np.ones_like(values)
        scaled = values / norm
        return scaled if direction == "BENEFIT" else 1.0 - scaled
    raise ValueError(f"Unknown normalization: {normalization}")


def equal_weight_scores(
    units: list[AssessmentUnit],
    normalization: str = "current_minmax",
    weights: dict[str, float] | None = None,
    criteria: tuple[str, ...] = CRITERIA,
) -> list[dict[str, object]]:
    """Compensatory secondary score; higher means safer/lower triage priority."""
    if weights is None:
        weights = {criterion: 1.0 / len(criteria) for criterion in criteria}
    total = sum(weights[criterion] for criterion in criteria)
    if total <= 0:
        raise ValueError("Weights must sum to a positive value")
    normalized_weights = {criterion: weights[criterion] / total for criterion in criteria}
    columns = {
        criterion: _benefit_values(units, criterion, normalization)
        for criterion in criteria
    }
    rows = []
    for index, unit in enumerate(units):
        contributions = {
            criterion: float(normalized_weights[criterion] * columns[criterion][index])
            for criterion in criteria
        }
        rows.append(
            {
                "name": unit.name,
                "risk_class": risk_class(unit),
                "safety_score": float(sum(contributions.values())),
                "contributions": contributions,
                "normalization": normalization,
                "score_semantics": "RELATIVE_COMPOSITE_SCORE_NOT_PROBABILITY",
            }
        )
    # Preserve the hard gate: compare score only inside each risk class.
    rows.sort(
        key=lambda row: (
            CLASS_PRIORITY[str(row["risk_class"])],
            -float(row["safety_score"]),
        ),
        reverse=True,
    )
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    return rows


def rank_map(rows: list[dict[str, object]]) -> dict[str, int]:
    return {str(row["name"]): int(row["rank"]) for row in rows}


def spearman_from_ranks(a: dict[str, int], b: dict[str, int]) -> float:
    names = sorted(set(a) & set(b))
    n = len(names)
    if n < 2:
        return 1.0
    d2 = sum((a[name] - b[name]) ** 2 for name in names)
    return 1.0 - 6.0 * d2 / (n * (n * n - 1))


def top_k_overlap(a: dict[str, int], b: dict[str, int], k: int) -> float:
    top_a = {name for name, rank in a.items() if rank <= k}
    top_b = {name for name, rank in b.items() if rank <= k}
    return len(top_a & top_b) / k


def fit_lognormal(values: np.ndarray) -> tuple[float, float]:
    logs = np.log(np.asarray(values, dtype=float))
    return float(logs.mean()), float(logs.std(ddof=0))


def _phi(value: float) -> float:
    return math.exp(-0.5 * value * value) / math.sqrt(2.0 * math.pi)


def _Phi(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def fit_left_censored_lognormal(
    detected: np.ndarray,
    lod: float,
    censored_count: int,
    max_iter: int = 1000,
    tolerance: float = 1e-11,
) -> tuple[float, float, int]:
    """EM maximum-likelihood fit for constant-LOD left-censored lognormal data."""
    logs = np.log(np.asarray(detected, dtype=float))
    if logs.size < 2 or censored_count < 0:
        raise ValueError("Need at least two detections and a nonnegative censored count")
    threshold = math.log(lod)
    mu = float(logs.mean())
    sigma = max(float(logs.std(ddof=0)), 1e-6)
    n_total = logs.size + censored_count
    for iteration in range(1, max_iter + 1):
        alpha = (threshold - mu) / sigma
        cdf = max(_Phi(alpha), 1e-300)
        ratio = _phi(alpha) / cdf
        expected_z = mu - sigma * ratio
        conditional_var = sigma * sigma * max(
            1.0 - alpha * ratio - ratio * ratio, 1e-12
        )
        expected_z2 = conditional_var + expected_z * expected_z
        mu_new = float((logs.sum() + censored_count * expected_z) / n_total)
        second = float(((logs * logs).sum() + censored_count * expected_z2) / n_total)
        sigma_new = math.sqrt(max(second - mu_new * mu_new, 1e-12))
        if max(abs(mu_new - mu), abs(sigma_new - sigma)) < tolerance:
            return mu_new, sigma_new, iteration
        mu, sigma = mu_new, sigma_new
    raise RuntimeError("Censored lognormal EM did not converge")


def simulate_exposure(
    rng: np.random.Generator,
    intake_parameters: list[tuple[float, float]],
    concentration_parameters: list[tuple[float, float]],
    draws: int,
    chunk: int = 250_000,
) -> np.ndarray:
    if len(intake_parameters) != len(concentration_parameters):
        raise ValueError("Food dimensions differ")
    exposure = np.empty(draws, dtype=np.float64)
    for start in range(0, draws, chunk):
        end = min(start + chunk, draws)
        size = end - start
        subtotal = np.zeros(size, dtype=np.float64)
        for (imu, isig), (cmu, csig) in zip(
            intake_parameters, concentration_parameters
        ):
            subtotal += rng.lognormal(imu, isig, size) * rng.lognormal(cmu, csig, size)
        exposure[start:end] = subtotal
    return exposure


def empirical_zero_substitution_exposure(
    rng: np.random.Generator,
    intakes: np.ndarray,
    concentration_observations: list[np.ndarray],
    draws: int,
    chunk: int = 250_000,
) -> np.ndarray:
    exposure = np.empty(draws, dtype=np.float64)
    for start in range(0, draws, chunk):
        end = min(start + chunk, draws)
        size = end - start
        persons = rng.integers(0, intakes.shape[0], size=size)
        subtotal = np.zeros(size, dtype=np.float64)
        for food, observations in enumerate(concentration_observations):
            samples = rng.integers(0, observations.size, size=size)
            subtotal += intakes[persons, food] * observations[samples]
        exposure[start:end] = subtotal
    return exposure


def lognormal_quantile(mu: float, sigma: float, probability: float) -> float:
    return math.exp(mu + sigma * NormalDist().inv_cdf(probability))


def rank_names(rows: list[dict[str, object]]) -> list[str]:
    return [str(row["name"]) for row in sorted(rows, key=lambda row: int(row["rank"]))]
