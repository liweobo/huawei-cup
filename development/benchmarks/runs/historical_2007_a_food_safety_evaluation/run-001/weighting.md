# Weighting Contract

## Primary rule

The formal hard gate and lexicographic triage use no numerical weights. Their priority order comes from decision semantics:

1. compliance/uncertainty class;
2. uncertainty-upper ratio;
3. point ratio;
4. affected population.

This order is policy-relevant but still must be declared; it is not inferred from dispersion.

## Baseline weights

| Criterion | Weight | Source | Meaning | Normalized | Subjective/data-driven |
|---|---:|---|---|---|---|
| point ratio | 0.25 | equal-weight baseline | no preference supplied | yes | neutral comparator, not objective truth |
| upper ratio | 0.25 | equal-weight baseline | no preference supplied | yes | neutral comparator |
| affected population | 0.25 | equal-weight baseline | no preference supplied | yes | neutral comparator |
| monitoring coverage | 0.25 | equal-weight baseline | no preference supplied | yes | neutral comparator |

The weights sum to one. They are neither expert judgments nor policy priorities. No experts were consulted or invented.

## Guards

- Entropy weighting is not used. If it were, its dispersion weight would not equal importance.
- AHP is not used; there is no pairwise matrix, expert provenance, or consistency ratio.
- TOPSIS is not used; no closeness value is reported as probability.
- `point_ratio` and `upper_ratio` are correlated derived indicators. Their simultaneous additive use creates `DOUBLE_WEIGHTING_RISK`; the baseline retains them only to expose this risk, and indicator deletion is reported.
- Intake/concentration contributions are already inside `D`. They are not weighted a second time as separate “importance” indicators in the compliance score.

## Sensitivity

Each baseline weight was changed one at a time by ±10% and ±20%, then all weights were renormalized. The top-three violating set remained the same, but the first-ranked baseline unit changed between `North-A` and `West-B`. Consequently the compensatory winner is not stable enough for a unique recommendation. The primary hard/lexicographic result has no weight parameter to perturb.
