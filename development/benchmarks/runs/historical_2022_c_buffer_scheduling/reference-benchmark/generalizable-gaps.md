# Generalizable Gaps

## Classification

### G1: Feasibility-Preserving Structured Improvement

**Definition**: after constructing a feasible state-coupled or
decoder-based schedule, search a problem-structured but
feasibility-preserving neighborhood of moves (swap, insertion, block move,
lane reassignment, return/no-return, dispatch choice), evaluate every move
through the real schedule or feasible decoder, and retain only real
objective improvements.

**Evidence**:

- R-02 explicitly constructs a greedy feasible solution and applies
  simulated annealing to a neighboring solution.
- R-04 defines grouped/stepwise resequencing algorithms and compares SA/GA
  over those structures.
- R-01 uses heuristic scheduling strategies as an initial population and
  then genetic crossover/mutation.
- R-05 uses GA for Q1 and a Markov multi-objective ranking policy for Q2.
- R-03 and R-06 use iterative/improved search over sequence/location state
  rather than a single dispatch decision.

**Current Skill failure**:

- run-002 can construct a feasible schedule and even tests abstract
  sequence swaps, but its chosen improved search does not improve the real
  weighted objective.
- run-003 is state-coupled but only chooses one legal action at a time
  using a local priority. It has no feasible swap/insertion/block/lane/
  return improvement phase.

**Why generalizable**:

- The principle applies to scheduling, routing, resource allocation and
  other discrete optimization problems with a feasible decoder or state
  transition.
- It does not rely on PBS, six lanes, nine seconds, or automotive
  terminology.
- It is a modeling/search-space principle, not an algorithm recommendation.

**Why not problem-specific**:

- The exact move set is instantiated per problem; the contract only
  requires moves to be feasible under the problem's state/decoder.
- The same principle would apply to a generic machine-buffer scheduling
  instance or a routing/resource problem.

**Expected competition impact**: high, because the current solution is
feasible but leaves the dominant objective O1 at zero; a feasible
improvement phase can search for sequence changes while preserving the
hard constraints already modeled.

**Implementation constraint**: the Skill should not add a solver platform;
it should require the search contract to state how legal improvement moves
are generated and evaluated.

### G2: PBS-Specific Return/Lane Policies

The exact return probability, lane assignment for hybrid/fuel vehicles,
and six-lane handoff schedules are 2022C-specific. They belong only in the
benchmark implementation, not in generic Skill guidance.

### G3: Algorithm-Name Differences

The references use GA, SA, grey wolf, dynamic programming and Markov
decision processes. These names alone are not evidence that the Skill must
implement any one of them. The Skill may choose greedy, beam, local
search, dynamic programming, MILP/CP or a metaheuristic according to
scale.

### G4: Reference Weaknesses

Several references do not provide independent workbook replay, exact
bounds, or defensible global-optimum evidence. The current Skill's
independent audit and optimality-language discipline should be preserved,
not relaxed in pursuit of a higher reported score.

## Candidate Comparison

| candidate | supported by references | current Skill missing | generalizable | top-1? |
|---|---:|---:|---:|---:|
| feasibility-preserving local search | 5+ | yes | yes | YES |
| lookahead / rolling horizon | several | yes | yes | subsumed as a possible move generator |
| structure-aware neighborhood design | most references | yes, as part of the same gap | yes | merged into TOP-1 |
| objective decomposition | some | partial | yes | not the first repair; do not add another module |
| exact/bound benchmark | none proved | yes | useful but not the immediate quality failure | no |

## Top-1

```text
TOP-1 GAP:
FEASIBILITY_PRESERVING_STRUCTURED_IMPROVEMENT
```

This does not replace the stateful scheduling contract. It extends it:
state-coupled or decoder-valid construction remains mandatory; the missing
piece is a structured, feasible improvement/search phase that can change
the schedule rather than only choose the next myopic legal action.
