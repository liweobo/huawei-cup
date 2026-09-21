# Evaluation Target Contract

| Field | Contract |
|---|---|
| `evaluation_object` | One declared population × geography × time window × food taxonomy × contaminant assessment cell. National, regional, and food-specific results are separate cells, not silently pooled. |
| `decision_question` | Is the high-exposure tail below the applicable authority standard with adequate uncertainty margin, and which cells require monitoring/action first? |
| `score_or_rank_or_class` | Primary output: absolute exposure quantile plus threshold-based compliance/uncertainty class. Optional secondary output: relative triage rank. No free-standing composite “safety probability.” |
| `stakeholder` | Food-hygiene safety authorities and decision-makers responsible for sampling, monitoring, warning, and intervention. |
| `comparison_scope` | Compare each assessment cell with its applicable threshold; compare cells with each other only for triage after units, contaminant, time, and target population are made commensurable. |
| `time_scope` | A declared monitoring/survey window. Source text says “at a certain time” but supplies no dates; operational runs must record survey year, monitoring year, and standard year. |
| `geographic_scope` | National, region, or other explicitly declared domain. Provincial/municipal samples do not automatically represent the country. |
| `allowed_claim` | This run may claim that the modelling and evaluation contracts work on synthetic scenarios. It may not claim actual national/regional safety, actual exceedance probability, or legal compliance. |

## Risk semantics

`risk` in the source is operationalized here as a distribution of daily contaminant intake and its upper-tail relationship to an authority threshold. It is not a generic weighted “risk value.” The core quantity is

`q = Q_0.99999(D)`, where `D` is daily intake in a declared physical unit.

The dimensionless ratio `ρ = q/T` is a threshold margin, not a probability. If a fitted distribution is valid, `P(D > T)` may be computed separately and labelled as an exceedance probability. AHP weights, TOPSIS closeness, normalized scores, and ranks cannot acquire probability semantics.

## Hard classification

For a point estimate `ρ` and an uncertainty upper bound `ρ_U`:

- `VIOLATION`: `ρ > 1`;
- `UNCERTAIN`: `ρ ≤ 1 ≤ ρ_U` (including the boundary because the source asks for the quantile to be clearly below the standard);
- `COMPLIANT_UNDER_MODEL`: `ρ_U < 1`.

The threshold `1` is **DERIVED** from the ratio definition, not an assumed `0.3/0.6` grading rule. `T` itself must be **GIVEN**, **REGULATION**, or a clearly labelled scenario value. A real-world compliance label is forbidden until the standard version, contaminant, food/population applicability, unit, and effective date are verified.

## Secondary triage

The source does not require ranking. If authorities need triage, this run uses a noncompensatory lexicographic order:

1. risk class (`VIOLATION > UNCERTAIN > COMPLIANT_UNDER_MODEL` for action priority);
2. uncertainty-upper ratio, descending;
3. point ratio, descending;
4. affected population, descending.

This rank is relative monitoring priority. It is not absolute risk, safety probability, or regulatory compliance. A near tie is retained when uncertainty can plausibly reverse adjacent cells.
