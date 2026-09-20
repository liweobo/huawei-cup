# Simulation Protocol Comparison

## Did each analysis simulate?

| aspect | Blind run | R1 | R2 | R3 |
|---|---|---|---|---|
| Primary method | analytic renewal-reward | analytic per-cycle expectation | analytic `E[f(L,X)]` + exhaustive search | analytic per-cycle expectation + iteration |
| Monte Carlo used | yes, as independent verification | no | no | no |
| Simulation role | cross-check of the analytic result | n/a | n/a | n/a |
| Replication unit | one complete regenerative trajectory of N cycles | n/a | n/a | n/a |
| RNG provenance | `numpy.Generator(PCG64)`, `SeedSequence`, seed 20260920 recorded | none | none | none |
| Horizon refinement | 512 vs 1024 cycles | none | none | none |
| Replication refinement | 128 vs 256 | none | none | none |
| Convergence reported | yes, with bias versus analytic | none | none | none |

None of the three references uses Monte Carlo. All work analytically or by deterministic search
over a discrete support. That is the correct choice for this problem, because a cycle cost is
integrable in closed form under a known law, and it is the same choice the blind run made:
analytic primary, simulation only as an independent check.

## Consequence for the "simulation is necessary" question

The instruction warned against concluding that the Skill must simulate merely because stochastic
problems often are simulated. The reference set confirms the opposite: for 2005D the references
obtained their answers with no simulation at all. The blind run's analytic-first ordering
therefore matches the reference practice, and its added simulator is a verification layer that
none of the references has.

## Where the references' analytic approach is weaker

Because they are analytic, the references obtain no uncertainty estimate. R2's exhaustive search
gives a definite minimum over a finite integer grid, which is a legitimate exactness claim for
Q2, but it is an exactness over the wrong object if the law is wrong. R1 and R3's iterative solves
similarly report a point value with no interval.

The blind run's simulator is what makes it possible to say that the analytic value and an
independent path-based estimate agree, and to attach an interval to the path-based estimate. The
analytic value remains the headline number.

## Classification

- Analytic-before-simulation: `SKILL_STRENGTH`.
- Independent simulator cross-check: `SKILL_STRENGTH`.
- RNG and convergence provenance: `SKILL_STRENGTH` (no reference reports any, though none needed
  to since none simulates).
- Choice to simulate at all: consistent with reference practice, so not a difference and not a
  gap.
