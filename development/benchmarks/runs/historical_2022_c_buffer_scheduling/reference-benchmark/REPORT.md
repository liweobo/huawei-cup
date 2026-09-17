# 2022C Excellent-Solution Post-hoc Benchmark

## 1. Reference Set

The requested `国赛论文/2022年优秀论文/C` directory was enumerated from
GitHub. It contains exactly seven PDFs; all seven were downloaded to a
temporary directory, hashed, and text-extracted. The PDFs and extraction
cache are intentionally not committed.

The set is treated as `EXCELLENT_SOLUTION_REFERENCE_SET`, not as a single
ground-truth answer. Award levels are `UNKNOWN` unless the supplied mirror
independently verifies them.

## 2. Source Reliability

All seven files were readable as PDFs. Six have usable text extraction.
`C22106140003.pdf` has a damaged text layer, so fine-grained claims from
that paper are marked low-confidence/partial rather than treated as
verified.

The source ledger records the discovered filename, URL, text availability,
confidence, Q1/Q2 coverage, method family, and result availability.

## 3. Current Blind Solution

The frozen run-002 solution is a discrete-event PBS model with a
source-order baseline, greedy dispatch, and a limited abstract
target-sequence experiment. It is independently audited and feasible.

Best-found scores:

| scenario | weighted | O1 | O2 | O3 | O4 |
|---|---:|---:|---:|---:|---:|
| Q1 | 53.367 | 0 | 80 | 100 | 93.67 |
| Q2 | 53.643 | 0 | 81 | 100 | 93.43 |

Limitations: O1 is zero, return use is zero in the selected results, and
search quality is weak despite feasible construction.

## 4. Current Post-Fix Solution

Run-003-postfix uses `STATE_COUPLED` search: legal actions are enumerated
from the current PBS state, the complete frozen event loop performs the
transition, and the realized schedule objective is evaluated. Both
workbooks pass an independent audit with zero hard violations.

State-coupled results:

| scenario | weighted | O1 | O2 | O3 | O4 |
|---|---:|---:|---:|---:|---:|
| Q1 | 51.801 | 0 | 80 | 94 | 90.01 |
| Q2 | 53.058 | 0 | 80 | 100 | 90.58 |

The contract is valid, but the candidate remains a myopic one-step policy.

## 5. Reference Modeling Approaches

The detailed matrices are in `reference-method-matrix.md`. The common
patterns are:

- sequence/lane/return decisions followed by a simulator or decoder;
- a heuristic or constructive initial schedule;
- iterative, neighborhood, population, or multi-step search;
- repeated evaluation on a real or decoded schedule;
- explicit use of the return lane as a searchable decision in most papers.

Algorithm names vary widely: GA, SA, grey wolf, dynamic programming,
Markov decision, greedy and hybrid variants. The shared modeling idea is
more important than the algorithm label.

## 6. Objective Strategy Comparison

Detailed analysis is in `objective-comparison.md`.

References generally retain the official weighted score or explicitly
compute its four components. They do not provide evidence that the current
Skill's exact objective definition is wrong.

The current Skill's failure is not objective formulation. It is search
coverage: one-step dispatch and an abstract sequence surrogate do not
explore the sequence/lane/return changes that could improve O1.

## 7. Search Representation Comparison

The current `STATE_COUPLED` representation is valid and should be kept.
The references often use a sequence/assignment representation with a
simulator or constructive decoder. This is a legitimate alternate
representation, not a recurrence of the old decoupling gap.

The missing capability is not a replacement representation. It is a
search phase over a representation that already has real feasibility.

## 8. Neighborhood / Action Design Comparison

Detailed comparison is in `search-design-comparison.md`.

Current run-003 has actions but no structured improvement neighborhood:

- lane assignment choices;
- return/no-return decisions;
- sequence swaps or insertions;
- block moves;
- dispatch choices;
- future-state lookahead.

References R-01, R-02, R-03, R-04, R-05 and R-06 repeatedly use
problem-structured changes after construction. This is the strongest
generalizable evidence in the benchmark.

## 9. Lookahead / Search Horizon Comparison

The current post-fix policy is myopic: it ranks legal actions using the
current output context. References use multi-step, iterated, population,
or Markov-style decisions. The recommendation is not to mandate a
particular horizon or algorithm; the contract should require that a formal
improvement phase be able to evaluate changes beyond the immediate action.

Lookahead is therefore treated as part of the TOP-1 structured
improvement gap, not a separate Skill module.

## 10. Return-Lane Strategy Comparison

The references do not support “always use the return lane.” They support
modeling it as a decision whose value depends on the sequence.

- R-01 uses return probability as a strategy variable.
- R-02 decides whether and how often to return.
- R-03 changes the sequence through return-related iteration.
- R-04 reports return use and can reduce it to zero in Q2.
- R-05 uses return when lane assignment is unsuitable.

The current Skill can use the lane but lacks a structured rule or search
for when a return improves the realized objective.

## 11. Feasibility Discipline Comparison

Detailed evidence is in `feasibility-comparison.md`.

The current Skill is stronger than the supplied papers in:

- hard constraints as gates;
- state transition legality;
- independent workbook replay;
- explicit zero-hard-violation audit;
- refusal to claim global optimality without proof.

This advantage must be preserved. It is not a reason to keep the myopic
search.

## 12. Numerical Result Comparison

Numerical values are recorded in `numerical-comparison.md`, but they are
mostly `NOT DIRECTLY COMPARABLE` because rule interpretations, timing
conventions, simulator assumptions and reporting variants differ.

The qualitative comparison is sufficient for the gap diagnosis: reference
methods report nontrivial O1 behavior and structured search, while the
current best-found and post-fix candidates keep O1 at zero.

## 13. Reference Consensus

Detailed counts are in `reference-consensus.md`.

- 7/7 papers use a sequence/assignment or equivalent candidate structure.
- At least 6/7 use a real simulator, decoder, state matrix or state
  evaluation.
- At least 5/7 construct a feasible initial schedule before improving it.
- At least 5/7 use an iterative/neighborhood/population search.
- 6/7 include return-lane decisions explicitly.
- 0/7 provide a proven global bound in the supplied text.

Consensus is evidence, not a vote on truth. It strongly supports one
missing modeling principle: structure-aware feasible improvement.

## 14. Skill Strengths

The current Skill should be credited for:

- statement-first modeling;
- traceable constraints;
- state-coupled feasibility after the previous fix;
- hard constraints not disguised as penalties;
- surrogate scores rejected as final objectives;
- infeasible candidates excluded from incumbent selection;
- independent final workbook audits;
- correct `BEST FOUND` optimality language;
- reproducible experiment provenance.

These are genuine advantages over what is documented in most references.

## 15. Skill Weaknesses

Evidence-supported weaknesses:

- no reusable feasible-neighborhood design principle;
- no required improvement phase after construction;
- no search-horizon/lookahead requirement beyond immediate actions;
- weak objective-aware sequence/lane/return decomposition;
- weak initialization/search balance for large combinatorial instances;
- no systematic bound or exact small-instance evidence.

The first three are different facets of the same TOP-1 gap.

## 16. Reference Weaknesses

Detailed notes are in `reference-weaknesses.md`.

Several papers call heuristic results optimal-like without an exact bound,
do not independently replay final workbooks, or use altered/variant
score reporting. These references should not force the Skill to lower its
feasibility or optimality standards.

## 17. Generalizable Gaps

Full classification is in `generalizable-gaps.md`.

The only selected G1 is:

```text
FEASIBILITY_PRESERVING_STRUCTURED_IMPROVEMENT
```

It requires a construction phase to be followed by feasible,
problem-structured moves whose realized/decoded objective can improve the
incumbent. It subsumes structure-aware neighborhoods and permits—but does
not mandate—lookahead, beam search, local search, dynamic programming,
metaheuristics, or exact methods.

## 18. Problem-Specific Techniques

The exact PBS lane mapping, return probabilities, six-lane specific
heuristics, nine-second movement details and 2022C-specific schedule
patterns are classified G2 and must not enter generic Skill guidance.

Likewise, the paper-reported scores are not a universal benchmark and are
not a reason to tune the Skill to 2022C.

## 19. Top-1 Candidate

**TOP-1 GAP: `FEASIBILITY_PRESERVING_STRUCTURED_IMPROVEMENT`**

Required contract-level principle:

1. construct or decode a feasible schedule;
2. define a domain-valid move set over the actual decision structure;
3. reject moves that violate hard constraints before evaluation;
4. evaluate the move on the realized/decoded schedule;
5. retain only improvements under the true objective;
6. record the search neighborhood, incumbent and stopping rule.

This is a modeling/search-contract extension, not a request to add a
solver platform or a specific metaheuristic.

## 20. Final Decision

**B. GENERALIZABLE_OPTIMIZATION_GAP_FOUND**

The current Skill is strong on formulation, feasibility and search
validity, but reference evidence shows a common missing modeling layer:
after feasible construction, improve the schedule through a
problem-structured, feasibility-preserving neighborhood evaluated on the
real objective.

This is more specific than “use GA” and broader than “fix PBS.” It is
generalizable to other discrete scheduling, routing and resource
configuration problems. Do not modify `skill/` in this benchmark phase.

## Skill Level

```text
FORMULATION: STRONG
FEASIBILITY: STRONG
SEARCH_VALIDITY: STRONG
SOLUTION_QUALITY: WEAK
OVERALL: NEEDS_OPTIMIZATION_IMPROVEMENT
```

Each judgment is supported by the current run artifacts, the reference
method matrices, and the separation between feasibility correctness and
solution quality above.
