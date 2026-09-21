# Baseline

## Definition

The simplest runnable exposure baseline follows the source's explicitly criticized shortcut so its failure is measurable:

1. resample observed household intake rows empirically;
2. replace every nondetect with zero;
3. resample food concentrations empirically and independently of intake;
4. compute `D = Σ_j I_j C_j`;
5. take the empirical `0.99999` quantile from 2,000,000 draws.

For the secondary synthetic triage matrix, the baseline first preserves the hard compliance class and then uses an equal-weight normalized safety score inside each class. The four weights are `0.25` each and mean only “no preference supplied.” They are not learned importance or policy priorities.

## Actual run

Command: `python code/run_model.py`

Evidence scope: `SYNTHETIC_SCENARIO_ONLY`.

- Baseline extreme quantile: approximately `5,305` synthetic mass/person-day.
- Known-parameter Monte Carlo oracle: approximately `13,162` in the same synthetic unit.
- Relative error: approximately `-59.7%`.

The baseline therefore demonstrates the source's warning: coding nondetects as zero can materially understate the upper tail. The number is not a real food-safety estimate.

## Equal-weight triage baseline

After applying the hard class gate, the baseline action-priority order is:

`North-A > West-B > Coast-C > South-A > East-B > Central-C`.

The score itself is a relative composite. It is not a probability and cannot determine compliance. Per-indicator contributions are retained in `outputs/ranking-results.json`; they also show that high coverage/population terms can materially move an intra-class score, which is why this compensatory baseline is not the primary rule.

## Comparison target

The primary exposure model must reduce the known nondetect bias without claiming unjustified tail precision. The primary evaluation rule must prevent ordinary criteria from offsetting a threshold violation and must preserve absolute-versus-relative semantics.
