# Objective Strategy Comparison

## What The Statement Requires

The stated score is a fixed weighted sum:

```text
0.4*O1 + 0.3*O2 + 0.2*O3 + 0.1*O4
```

O1 is the dominant component. The current best-found result has O1 = 0,
so almost any feasible schedule that improves O1 has high leverage even if
O2/O4 move modestly.

## Current Skill Strategy

- Run-002 computes the exact stated score on the realized schedule.
- Its source-order and simple greedy policies make essentially local
  decisions.
- The abstract target-sequence experiment optimizes a surrogate permutation
  score, but its realized schedule does not improve the official objective.
- Run-003 fixes state coupling but still uses a myopic one-step action
  priority. It can use the return lane, yet does not search for a sequence
  pattern over a horizon.

## Reference Strategies

The references do not agree on a single objective protocol, but several
patterns are clear:

1. **Direct weighted-score optimization**
   - R-02 states that the four objectives are converted by linear weights
     into a total-score maximization target.
   - R-06 states a weighted objective `W = 0.4*W1 + 0.3*W2 + 0.2*W3 + 0.1*W4`.
   - R-05 similarly uses the stated weighted multi-objective score.
2. **Constructive solution first, then structured improvement**
   - R-02 explicitly constructs a greedy feasible solution and then applies
     simulated annealing in its neighborhood.
   - R-04 develops grouped and stepwise resequencing methods and compares
     simulated annealing with genetic search.
3. **Sequence/location representation with a PBS decoder**
   - R-01 uses a per-second PBS simulation to evaluate lane/return decisions.
   - R-03 builds position/time matrices and changes the sequence iteratively.
   - R-06 formulates vehicle location transitions over OD pairs.
4. **Return decisions as part of the search object**
   - R-01 uses return probabilities as an explicit strategy parameter.
   - R-02 decides whether and how often a vehicle returns.
   - R-03 describes changing the sequence through return-lane usage.
   - R-04 reports return usage and Q2 behavior where return use can fall to
     zero.
   - R-05 says that a vehicle can return to the PBS receiving machine when
     the lane assignment is unsuitable.

## Diagnosis Of O1 = 0

The reference evidence does **not** show that O1 is mathematically
impossible on either attachment. R-01 explicitly analyzes the data mix and
states a lower/upper analysis for the hybrid pattern; references R-02,
R-03, R-04 and R-05 all report nontrivial O1 values (often negative but
not uniformly zero). Therefore the evidence supports:

```text
O1 = 0 is primarily a current-search/objective-structure limitation,
not proof that the data make O1 improvement impossible.
```

The limitation is not simply "no GA". The shared structure is:

- construct a realizable sequence;
- define local moves in the sequence/lane/return decision space;
- evaluate each move through the real PBS state or a feasible decoder;
- accept improvements using the true weighted objective;
- allow multi-step or neighborhood search rather than one-step scoring.

## Multi-Objective Caveats

- The references generally keep the statement's weights; some later use
  staged or algorithm-specific comparisons.
- R-01 explicitly adjusts Q2 strategy probabilities while still reporting
  objective components; this is a strategy change, not a change of the
  official weights.
- No reference is used here as proof that one weighting protocol is
  universally correct. The statement's fixed weights are retained.
