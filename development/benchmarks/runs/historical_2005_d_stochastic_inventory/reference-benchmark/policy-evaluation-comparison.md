# Policy Evaluation Comparison

## Search versus evaluation

| aspect | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Policy search | exact finite-support minimisation plus bounded multistart for the joint case | Lingo NLP | exhaustive search over `L` (and staged search over allocation) | iterative solve and 6^m state enumeration |
| Separate evaluation draws | yes, search draws distinct from evaluation draws | not applicable, deterministic | not applicable, deterministic | not applicable, deterministic |
| Risk of seed overfitting | addressed: no policy is called best from one seed | none, since deterministic | none, since deterministic | none, since deterministic |
| Policy comparison method | common random numbers with paired differences | pairwise values not compared with uncertainty | not compared | not compared |
| Difference uncertainty | reported for Q5 and for the joint comparison | none | none | none |

The instruction's key concern, searching a policy on the same random realisations used to report
it as best, does not arise for the references, because none of them uses random search. Their
optimisation is deterministic given the fitted or empirical law, so each reported optimum is an
optimum of a fixed objective rather than a lucky draw. The blind run also does not search
stochastically for Q1-Q4; its joint search is over a deterministic objective.

For Q5, where the blind run does simulate, it separates search draws from evaluation draws and
uses common random numbers, so the Q5 comparison is not a single-realisation artefact. No
reference reaches this stage at all.

## Comparing two policies

The blind run reports differences with uncertainty:

| comparison | difference | interval | conclusion |
|---|---:|---|---|
| Joint primary vs baseline | -2.7434 | [-2.7627, -2.7240] | clear advantage |
| Q5 adaptive vs static | -0.4724 | [-0.6207, -0.3241] | clear advantage |

No reference reports a difference between two policies, so there is no reference standard to
compare against here. The blind run's method, pairing on common random numbers and reporting the
difference interval, is the appropriate one for this problem, and it is prepared to return
`NO_CLEAR_POLICY_ADVANTAGE` when the interval covers zero.

## Classification

- Search/evaluation separation: `SKILL_STRENGTH` (and not applicable to the deterministic
  references, so no reference weakness is claimed).
- Common random numbers and paired intervals: `SKILL_STRENGTH`.
- Policy-comparison conclusions: the blind run is the only analysis that states any, so no
  reference evidence supports or contradicts it.
- Allowing a negative result: `SKILL_STRENGTH`. The framework permits `NO_CLEAR_POLICY_ADVANTAGE`
  rather than forcing a winner.
