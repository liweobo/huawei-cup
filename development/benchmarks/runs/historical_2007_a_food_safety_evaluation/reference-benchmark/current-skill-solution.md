# Frozen Current-Skill Solution

Status: `PRE_REFERENCE_SNAPSHOT`

This file was written from the frozen `run-001` artifacts before any excellent-solution PDF was opened or extracted. It summarizes the blind-run result; it does not revise or re-solve 2007A.

## Source target

The blind run interprets the source's main quantitative target as the distribution of daily contaminant intake for an explicitly declared population, geography, time window, food taxonomy, and contaminant. Its formal tail target is the `99.999%` right quantile

`q = Q_0.99999(D)`, where `D = sum_j I_j C_j` in a declared physical unit.

## Threshold and claims

The primary decision compares `q` and an uncertainty upper bound `q_U` with an applicable authority threshold `T`. The ratios `rho = q/T` and `rho_U = q_U/T` are dimensionless threshold margins, not probabilities. The threshold value `1` is derived from the ratio; `T` must be problem-given, an applicable verified regulation, or an explicitly illustrative assumption.

Because the problem supplied no operational survey, monitoring, taxonomy, or regulatory dataset, all executed numerical results are synthetic. The frozen run permits claims about model behavior under synthetic scenarios only; it forbids claims about actual national or regional safety, actual exceedance probability, or legal compliance.

## Hard compliance gate and optional triage

The frozen decision rule is noncompensatory:

- `VIOLATION` if `rho > 1`;
- `UNCERTAIN` if `rho <= 1 <= rho_U`;
- `COMPLIANT_UNDER_MODEL` if `rho_U < 1`.

Ordinary indicators cannot offset a threshold violation. Ranking is not treated as a problem requirement. If authorities need monitoring triage, the optional relative order is lexicographic by hard class, `rho_U`, `rho`, and affected population. It is not a safety probability or a compliance finding, and near ties are retained.

## Baseline

The simplest runnable exposure baseline empirically resamples intake and concentration, substitutes zero for nondetects, assumes independence, and estimates the `0.99999` quantile with two million draws. In the synthetic scenario it underestimates the known-parameter Monte Carlo oracle by about `59.7%`.

The secondary ranking baseline first preserves the hard class and then uses an equal-weight normalized score within class. Equal weights mean only that no preference was supplied. The score is relative, compensatory, candidate-set dependent, and not a probability.

## Primary risk chain

The primary conditional chain is:

`sampling frames -> intake model + censored contamination model -> taxonomy/unit bridge -> exposure distribution -> uncertainty -> hard compliance gate -> optional warning/triage`.

It uses survey-design weights, a left-censored likelihood for nondetects, explicit taxonomy crosswalks, declared conditional-independence/dependence scenarios for unpaired intake and contamination data, population transport for regional aggregation, and extreme-tail estimation with uncertainty. The executable synthetic example uses a censored lognormal model; that family is an illustration, not a universal prescription.

## Uncertainty and stability

The frozen run discloses material tail uncertainty. Repeated tail estimates and contamination-scale perturbations vary widely and can cross the illustrative threshold, so the valid synthetic conclusion is `UNCERTAIN`, not safe. Operational use would require tail diagnostics, adequate rare-event computation, cluster/stratum bootstrap, model-form sensitivity, dependence scenarios, and a verified standard.

Ranking stability is `PARTIAL`: the hard violating set is stable in the declared probes, but the equal-weight winner changes under weight or indicator perturbations, and the primary top two form a practical near tie. The run includes dominance, monotonicity, cost-direction, unit-rescaling, hard-gate, weight, normalization, indicator-deletion, and rank-reversal checks.

## Frozen gap candidate

The blind run records `EVALUATION_OUTPUT_SEMANTICS_CONTRACT_MISSING` at missing-guard severity `P0`. The candidate is a lightweight pre-weighting contract that declares evaluation object, decision question, output type, absolute-versus-relative semantics, probability/compliance semantics, threshold provenance, hard gate, and allowed claim. It forbids promoting a relative composite score to a probability or compliance conclusion.

The blind run itself remains `VALID`; the P0 label concerns the possible consequence of the missing frozen-Skill guard. Whether this is a generalizable evaluation gap, a 2007A-specific issue, a prompt-added guard, or a broader risk-modeling issue is deliberately unresolved until the post-hoc reference and Skill coverage audit.
