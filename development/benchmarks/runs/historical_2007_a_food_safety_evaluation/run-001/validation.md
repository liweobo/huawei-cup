# Validation

## Executed synthetic tests

| Test | Expected behavior | Result |
|---|---|---|
| A benefit indicator improves | increasing coverage with other raw inputs fixed must not reduce fixed-bound safety score | PASS |
| B cost direction reversal | larger point/upper ratios must lower safety score | PASS |
| C unit rescale invariance | multiplying exposure and standard by the same unit factor must not change ratio/class/rank | PASS |
| D dominated alternative sanity | an alternative worse on every risk/quality dimension gets higher action priority and lower safety score | PASS |
| E weight perturbation | execute ±10% and ±20%, report winner/top-k/rank correlation | PASS |
| F rank reversal | add an obviously worse alternative and compare all existing pairwise orders | PASS |
| G hard constraint | perfect coverage cannot make a ratio-above-one unit compliant | PASS |
| H score semantics | every baseline score declares `RELATIVE_COMPOSITE_SCORE_NOT_PROBABILITY` | PASS |

Machine evidence: `outputs/synthetic-tests.json`; focused unit tests: `code/test_evaluation.py`.

## Censoring model validation

The EM censored-lognormal fit was tested on 100,000 synthetic observations with known log parameters. Both fitted log mean and log standard deviation were within `0.03` of truth. In the integrated three-food run, censoring fractions were approximately 25%–29%, and all EM fits converged in 25–29 iterations.

The integrated extreme-tail result is less accurate than the body-parameter fit: the primary tail estimate is about `15.2%` below the known-parameter Monte Carlo oracle, versus about `59.7%` low for the zero-substitution baseline. This supports the improvement but also rejects a precise/safe point claim.

## Dominance and monotonicity

The additive baseline is monotone in every declared normalized benefit column with nonnegative weights. The hard/lexicographic primary is monotone in the decision direction: lowering a cost ratio cannot worsen class unless another field changes, and increasing only coverage cannot erase or create a hard violation.

## Known-threshold synthetic case

The illustrative threshold is explicitly `ASSUMED_SYNTHETIC`, not regulation. It demonstrates a crucial oracle case: baseline and primary point estimates can lie below the threshold while the true generating model lies above it. The uncertainty scenario crosses the threshold, so the gate produces `UNCERTAIN`. This is the intended conservative behavior.

## What is not validated

- no real survey frame, monitoring design, standard, taxonomy, dependence structure, or geographic transport data were supplied;
- no real `0.99999` coverage study was possible;
- no modern standard was substituted for a 2007 scope;
- no actual national/regional safety, probability, or compliance claim is validated.

The operational model remains conditional until these inputs and a full sampling/tail uncertainty protocol are available.
