# Reference weaknesses observed post-hoc

The following are observations about the reference set, not corrections to those papers.

1. **Closure assumptions are unevenly surfaced.** Tip entry, vertex crossing, normalized image geometry and incidence distributions can make Q1 computable, but are not always separated from problem facts.
2. **Q2 mechanism depth is heterogeneous.** One-bounce, dominant-zone, view-factor, radiosity, infinite-image and Monte Carlo models answer slightly different approximations to the same physical question.
3. **Truncation is often unverified.** B10386003 states 600 reflections without a tail study; similar gaps occur for numerical integration and wall-cell refinement.
4. **Model error is mixed with numerical error.** A finer grid cannot compensate for omitted multiple reflections or an assumed random reflection direction.
5. **Parameter provenance is mostly qualitative.** Effective rho is treated as a scalar given case; angle/frequency dependence, phase and scattering are not identified.
6. **No independent validation data are present.** Physical sanity, symmetry and internal tables are useful but weaker than measurements or a held-out experiment.
7. **Reported precision exceeds evidence in places.** Plots and tables can show several decimal places even when the mechanism and truncation are not established to that precision.

These weaknesses are useful for assessing Skill behavior. They do not justify changing the frozen Skill during this benchmark.
