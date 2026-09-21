# Sensitivity and Ranking Stability

All results are from the declared synthetic scenario and are tagged `SIMULATED_PERTURBATION`.

## Exposure-tail sensitivity

- Primary `0.99999` quantile from 2,000,000 draws: about `11,158` synthetic units.
- Known-parameter 3,000,000-draw oracle: about `13,162`.
- Five primary repeats with 400,000 draws each: about `9,301` to `11,726`.
- Contamination log-scale ×0.9 scenario: about `6,918`.
- Contamination log-scale ×1.1 scenario: about `18,834`.

This is high sensitivity. A real-world extreme-tail conclusion requires a fitted-tail/importance-sampling protocol plus full design/bootstrap/model-form uncertainty. Reporting one six-decimal point estimate would be misleading.

In the illustrative assumed-threshold case, the primary point ratio is below one while the known-parameter oracle ratio exceeds one. The parameter/tail uncertainty scenario crosses one. The correct result is therefore `UNCERTAIN`, not “safe.”

## Weight sensitivity

The four equal baseline weights were perturbed one at a time by ±10% and ±20%, then renormalized.

- minimum Spearman correlation with equal weights: `0.943`;
- minimum top-three overlap: `1.00`;
- first-ranked unit set across perturbations: `{North-A, West-B}`.

The hard violating set is stable; the compensatory winner is not. The primary lexicographic rule has no numerical weights.

## Normalization sensitivity

Current-set min-max, declared fixed-bound scaling, and vector normalization all produced the same baseline order:

`North-A > West-B > Coast-C > South-A > East-B > Central-C`.

Spearman correlation and top-three overlap with min-max were both `1.00` for the two alternatives. This is scenario-specific and does not convert the score into an absolute scale.

## Indicator-set sensitivity

Deleting one indicator at a time produced:

- delete coverage: `North-A > Coast-C > West-B > ...`;
- delete population: `West-B > North-A > Coast-C > ...`;
- delete upper ratio: `West-B > North-A > Coast-C > ...`.

Each comparison has Spearman `0.943` and top-three overlap `1.00`. The exact winner/order inside the violating class is indicator-set sensitive. `point_ratio` and `upper_ratio` also have derived-variable overlap, confirming the baseline's `DOUBLE_WEIGHTING_RISK`.

## Rank-reversal probe

Adding the obviously worse synthetic `Dominated-Z` changed numeric rank positions by inserting a new violation, but changed no existing pairwise order under either baseline or primary rule. The probe therefore passes. Current-set min-max values still changed, so the baseline scores remain alternative-set dependent.

## Stability conclusion

- hard class and top-three violating set: stable in declared probes;
- primary pairwise order under irrelevant-alternative probe: stable;
- baseline exact winner: unstable to weight/indicator changes;
- primary top two: practical near tie;
- extreme exposure quantile: materially uncertain.

Overall: `RANKING_STABILITY = PARTIAL`. The actionable conclusion is the violating/uncertain set and its drivers, not a unique fine-grained winner.
