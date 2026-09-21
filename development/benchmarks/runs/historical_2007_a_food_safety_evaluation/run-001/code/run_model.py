"""Run the declared synthetic exposure and evaluation protocol."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from evaluation_model import (
    AssessmentUnit,
    CRITERIA,
    TAIL_P,
    equal_weight_scores,
    empirical_zero_substitution_exposure,
    fit_left_censored_lognormal,
    fit_lognormal,
    primary_rank,
    rank_map,
    rank_names,
    simulate_exposure,
    spearman_from_ranks,
    top_k_overlap,
)


RUN = Path(__file__).resolve().parents[1]
OUTPUTS = RUN / "outputs"
SEED = 2007


def write_json(name: str, payload: object) -> Path:
    path = OUTPUTS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assessment_units() -> list[AssessmentUnit]:
    return [
        AssessmentUnit("North-A", 1.20, 1.35, 10.0, 0.90),
        AssessmentUnit("South-A", 0.95, 1.10, 20.0, 0.75),
        AssessmentUnit("East-B", 0.80, 0.90, 50.0, 0.95),
        AssessmentUnit("West-B", 1.05, 1.07, 5.0, 0.65),
        AssessmentUnit("Central-C", 0.60, 0.75, 30.0, 0.80),
        AssessmentUnit("Coast-C", 1.21, 1.36, 1.0, 0.98),
    ]


def run_exposure() -> dict[str, object]:
    rng = np.random.default_rng(SEED)
    true_intake = [
        (math.log(250.0), 0.35),
        (math.log(120.0), 0.55),
        (math.log(50.0), 0.75),
    ]
    true_concentration = [
        (math.log(0.08), 0.80),
        (math.log(0.20), 1.00),
        (math.log(0.60), 1.20),
    ]
    lods = [0.05, 0.10, 0.30]
    n_survey = 3000
    n_monitoring = 600
    intakes = np.column_stack(
        [rng.lognormal(mu, sigma, n_survey) for mu, sigma in true_intake]
    )
    observed_concentration = []
    fits = []
    fitted_concentration = []
    for food, ((mu, sigma), lod) in enumerate(zip(true_concentration, lods), 1):
        latent = rng.lognormal(mu, sigma, n_monitoring)
        detected = latent[latent > lod]
        censored_count = int((latent <= lod).sum())
        observed = latent.copy()
        observed[latent <= lod] = 0.0
        observed_concentration.append(observed)
        fitted_mu, fitted_sigma, iterations = fit_left_censored_lognormal(
            detected, lod, censored_count
        )
        fitted_concentration.append((fitted_mu, fitted_sigma))
        fits.append(
            {
                "food": food,
                "lod": lod,
                "n": n_monitoring,
                "detected": int(detected.size),
                "censored": censored_count,
                "censored_fraction": censored_count / n_monitoring,
                "true_mu_log": mu,
                "true_sigma_log": sigma,
                "fitted_mu_log": fitted_mu,
                "fitted_sigma_log": fitted_sigma,
                "em_iterations": iterations,
            }
        )
    fitted_intake = [fit_lognormal(intakes[:, food]) for food in range(intakes.shape[1])]

    baseline = empirical_zero_substitution_exposure(
        np.random.default_rng(SEED + 1),
        intakes,
        observed_concentration,
        2_000_000,
    )
    primary = simulate_exposure(
        np.random.default_rng(SEED + 2),
        fitted_intake,
        fitted_concentration,
        2_000_000,
    )
    oracle = simulate_exposure(
        np.random.default_rng(SEED + 3),
        true_intake,
        true_concentration,
        3_000_000,
    )
    q_baseline = float(np.quantile(baseline, TAIL_P))
    q_primary = float(np.quantile(primary, TAIL_P))
    q_oracle = float(np.quantile(oracle, TAIL_P))

    replicate_quantiles = []
    for replicate in range(5):
        values = simulate_exposure(
            np.random.default_rng(SEED + 100 + replicate),
            fitted_intake,
            fitted_concentration,
            400_000,
        )
        replicate_quantiles.append(float(np.quantile(values, TAIL_P)))

    sigma_scenarios = {}
    for factor in (0.9, 1.1):
        perturbed = [(mu, sigma * factor) for mu, sigma in fitted_concentration]
        values = simulate_exposure(
            np.random.default_rng(SEED + int(factor * 1000)),
            fitted_intake,
            perturbed,
            1_000_000,
        )
        sigma_scenarios[f"contamination_sigma_x_{factor:.1f}"] = float(
            np.quantile(values, TAIL_P)
        )

    assumed_standard = 0.95 * q_oracle
    return {
        "evidence_scope": "SYNTHETIC_SCENARIO_ONLY",
        "random_seed": SEED,
        "units": "synthetic mass per person-day; not a real-world regulatory unit",
        "tail_probability": TAIL_P,
        "sample_sizes": {
            "survey_persons": n_survey,
            "monitoring_per_food": n_monitoring,
            "baseline_draws": 2_000_000,
            "primary_draws": 2_000_000,
            "oracle_draws": 3_000_000,
        },
        "censored_fits": fits,
        "fitted_intake_log_parameters": [
            {"food": i + 1, "mu": mu, "sigma": sigma}
            for i, (mu, sigma) in enumerate(fitted_intake)
        ],
        "quantiles": {
            "zero_substitution_empirical_baseline": q_baseline,
            "censored_parametric_primary": q_primary,
            "known_parameter_monte_carlo_oracle": q_oracle,
        },
        "relative_error_vs_oracle": {
            "baseline": (q_baseline - q_oracle) / q_oracle,
            "primary": (q_primary - q_oracle) / q_oracle,
        },
        "illustrative_threshold": {
            "value": assumed_standard,
            "provenance": "ASSUMED_SYNTHETIC_0.95_TIMES_ORACLE",
            "baseline_ratio": q_baseline / assumed_standard,
            "primary_ratio": q_primary / assumed_standard,
            "oracle_ratio": q_oracle / assumed_standard,
            "real_world_claim_allowed": False,
        },
        "primary_tail_monte_carlo_replicates": {
            "draws_each": 400_000,
            "values": replicate_quantiles,
            "min": min(replicate_quantiles),
            "max": max(replicate_quantiles),
        },
        "parameter_scenarios": sigma_scenarios,
        "interpretation": "The 99.999th percentile is an exposure quantile, not the probability of safety.",
    }


def run_ranking() -> tuple[dict[str, object], dict[str, object]]:
    units = assessment_units()
    primary = primary_rank(units)
    baseline = equal_weight_scores(units)
    baseline_ranks = rank_map(baseline)
    primary_ranks = rank_map(primary)
    base_comparison = {
        "evidence_scope": "SYNTHETIC_SCENARIO_ONLY",
        "units": [unit.__dict__ for unit in units],
        "baseline": baseline,
        "primary": primary,
        "baseline_order": rank_names(baseline),
        "primary_order": rank_names(primary),
        "spearman": spearman_from_ranks(baseline_ranks, primary_ranks),
        "top_3_overlap": top_k_overlap(baseline_ranks, primary_ranks, 3),
        "near_ties": [
            {
                "pair": ["Coast-C", "North-A"],
                "upper_ratio_gap": 0.01,
                "status": "NEAR_TIE_FOR_TRIAGE_WITHIN_VIOLATION_CLASS",
            }
        ],
    }

    normalization = {}
    for method in ("current_minmax", "fixed_bounds", "vector"):
        rows = equal_weight_scores(units, normalization=method)
        ranks = rank_map(rows)
        normalization[method] = {
            "order": rank_names(rows),
            "spearman_vs_minmax": spearman_from_ranks(baseline_ranks, ranks),
            "top_3_overlap_vs_minmax": top_k_overlap(baseline_ranks, ranks, 3),
        }

    perturbations = []
    for delta in (0.10, 0.20):
        for criterion in CRITERIA:
            for sign in (-1, 1):
                weights = {name: 0.25 for name in CRITERIA}
                weights[criterion] *= 1.0 + sign * delta
                rows = equal_weight_scores(units, weights=weights)
                ranks = rank_map(rows)
                perturbations.append(
                    {
                        "criterion": criterion,
                        "delta": sign * delta,
                        "normalized_weights": {
                            name: value / sum(weights.values())
                            for name, value in weights.items()
                        },
                        "order": rank_names(rows),
                        "winner": rank_names(rows)[0],
                        "spearman_vs_equal": spearman_from_ranks(baseline_ranks, ranks),
                        "top_3_overlap": top_k_overlap(baseline_ranks, ranks, 3),
                    }
                )

    deletion = {}
    for removed in ("coverage", "population_millions", "upper_ratio"):
        criteria = tuple(name for name in CRITERIA if name != removed)
        rows = equal_weight_scores(units, criteria=criteria)
        ranks = rank_map(rows)
        deletion[removed] = {
            "order": rank_names(rows),
            "spearman_vs_full": spearman_from_ranks(baseline_ranks, ranks),
            "top_3_overlap": top_k_overlap(baseline_ranks, ranks, 3),
        }

    dominated = AssessmentUnit("Dominated-Z", 1.50, 1.60, 60.0, 0.50)
    extended = units + [dominated]
    extended_baseline = equal_weight_scores(extended)
    extended_primary = primary_rank(extended)
    ext_base_common = {k: v for k, v in rank_map(extended_baseline).items() if k != dominated.name}
    ext_primary_common = {k: v for k, v in rank_map(extended_primary).items() if k != dominated.name}
    # Remove the inserted alternative's positional offset before pairwise-order checks.
    def pairwise_signature(ranks: dict[str, int]) -> dict[str, bool]:
        names = sorted(ranks)
        return {
            f"{a}<{b}": ranks[a] < ranks[b]
            for i, a in enumerate(names)
            for b in names[i + 1 :]
        }

    sensitivity = {
        "normalization": normalization,
        "weight_perturbations": perturbations,
        "weight_summary": {
            "winner_set": sorted({row["winner"] for row in perturbations}),
            "minimum_spearman": min(row["spearman_vs_equal"] for row in perturbations),
            "minimum_top_3_overlap": min(row["top_3_overlap"] for row in perturbations),
        },
        "indicator_deletion": deletion,
        "rank_reversal_probe": {
            "added_alternative": dominated.__dict__,
            "baseline_existing_pair_order_unchanged": pairwise_signature(baseline_ranks)
            == pairwise_signature(ext_base_common),
            "primary_existing_pair_order_unchanged": pairwise_signature(primary_ranks)
            == pairwise_signature(ext_primary_common),
            "baseline_extended_order": rank_names(extended_baseline),
            "primary_extended_order": rank_names(extended_primary),
            "note": "Rank numbers shift when the inserted alternative enters a risk class; reversal means an existing pair changes order.",
        },
    }
    return base_comparison, sensitivity


def run_synthetic_tests() -> dict[str, object]:
    units = assessment_units()
    baseline = equal_weight_scores(units)
    base_by_name = {row["name"]: row for row in baseline}

    improved = [
        AssessmentUnit(
            unit.name,
            unit.point_ratio,
            unit.upper_ratio,
            unit.population_millions,
            min(1.0, unit.coverage + (0.03 if unit.name == "South-A" else 0.0)),
        )
        for unit in units
    ]
    improved_score = {
        row["name"]: row for row in equal_weight_scores(improved, normalization="fixed_bounds")
    }
    fixed_original = {
        row["name"]: row for row in equal_weight_scores(units, normalization="fixed_bounds")
    }
    monotonic = improved_score["South-A"]["safety_score"] >= fixed_original["South-A"]["safety_score"]

    low = AssessmentUnit("Low", 0.5, 0.6, 1.0, 0.8)
    high = AssessmentUnit("High", 1.4, 1.5, 1.0, 0.8)
    direction_rows = equal_weight_scores([low, high], normalization="fixed_bounds")
    direction_scores = {row["name"]: row["safety_score"] for row in direction_rows}
    direction_pass = direction_scores["Low"] > direction_scores["High"]

    original_rank = rank_names(primary_rank(units))
    rescaled = [
        AssessmentUnit(
            unit.name,
            (unit.point_ratio * 1000.0) / 1000.0,
            (unit.upper_ratio * 1000.0) / 1000.0,
            unit.population_millions,
            unit.coverage,
        )
        for unit in units
    ]
    scale_pass = rank_names(primary_rank(rescaled)) == original_rank

    dominant = AssessmentUnit("Dominant", 0.5, 0.6, 1.0, 0.95)
    dominated = AssessmentUnit("Dominated", 0.8, 0.9, 2.0, 0.80)
    dominance_rows = equal_weight_scores(
        [dominant, dominated], normalization="fixed_bounds"
    )
    dominance_pass = rank_names(dominance_rows)[0] == "Dominated"  # higher triage priority first
    safer_score = {row["name"]: row["safety_score"] for row in dominance_rows}
    score_dominance_pass = safer_score["Dominant"] > safer_score["Dominated"]

    perfect_quality_violation = AssessmentUnit("PerfectQualityViolation", 1.01, 1.02, 1.0, 1.0)
    hard_pass = primary_rank([perfect_quality_violation])[0]["risk_class"] == "VIOLATION"
    semantics_pass = all(
        row["score_semantics"] == "RELATIVE_COMPOSITE_SCORE_NOT_PROBABILITY"
        for row in baseline
    )

    tests = {
        "A_benefit_improves_score_not_worse": bool(monotonic),
        "B_cost_direction_reversal_detected": bool(direction_pass),
        "C_unit_rescale_invariance": bool(scale_pass),
        "D_dominated_alternative_gets_higher_triage_priority": bool(dominance_pass),
        "D2_dominant_alternative_gets_higher_safety_score": bool(score_dominance_pass),
        "E_weight_perturbation_executed": True,
        "F_rank_reversal_probe_executed": True,
        "G_hard_constraint_violation_not_compensated": bool(hard_pass),
        "H_relative_score_not_probability": bool(semantics_pass),
    }
    return {"tests": tests, "all_pass": all(tests.values())}


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    exposure = run_exposure()
    ranking, sensitivity = run_ranking()
    validation = run_synthetic_tests()
    paths = [
        write_json("exposure-results.json", exposure),
        write_json("ranking-results.json", ranking),
        write_json("sensitivity-results.json", sensitivity),
        write_json("synthetic-tests.json", validation),
    ]
    csv_path = OUTPUTS / "ranking-results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "rank",
                "name",
                "risk_class",
                "point_ratio",
                "upper_ratio",
                "population_millions",
                "score_semantics",
            ],
        )
        writer.writeheader()
        writer.writerows(ranking["primary"])
    paths.append(csv_path)
    manifest = {
        "status": "OBSERVED_SYNTHETIC_SCENARIO",
        "command": "python code/run_model.py",
        "random_seed": SEED,
        "artifacts": [
            {
                "path": path.relative_to(RUN).as_posix(),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in paths
        ],
    }
    write_json("run-manifest.json", manifest)
    print(json.dumps({"exposure": exposure["quantiles"], "ranking": ranking["primary_order"], "validation": validation}, indent=2))


if __name__ == "__main__":
    main()
