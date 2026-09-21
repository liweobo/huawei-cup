# Uncertainty Comparison

| reference | confidence interval | bootstrap | sensitivity | parameter uncertainty | tail uncertainty | sample uncertainty | audit |
|---|---|---|---|---|---|---|---|
| `REF-01` | no q interval | used to enlarge/reconstruct sample, not interval estimation | qualitative model comparison | not propagated | not quantified | discussed qualitatively | `INSUFFICIENT` |
| `REF-02` | mentions 95% survey confidence/admissibility, not q CI | used for small-sample reconstruction | kernel/window simulation only | not propagated | not quantified | partly discussed | `INSUFFICIENT` |
| `REF-03` | none | none for final q | none | importance weights described, not uncertain | not quantified | required sample size discussed | `INSUFFICIENT`; no real data |
| `REF-04` | none | none | none | not propagated | not quantified | sparse data acknowledged | `INSUFFICIENT` |
| `REF-05` | none | none | none | not propagated | not quantified | representativeness assumed | `INSUFFICIENT` |
| `REF-06` | same as `REF-02` | same | same | same | same | same | duplicate |

No unique reference reports a confidence/credible interval or uncertainty upper bound for `Q_0.99999`; no work demonstrates coverage at the requested tail. Thus point estimates cannot establish a robust margin below a hard standard.

The frozen blind run is materially stronger: it labels all executed values synthetic, repeats rare-tail simulation, perturbs contamination scale, discloses threshold crossing, retains an `UNCERTAIN` class, and refuses six-decimal certainty. Its residual weaknesses - real data absent, real standard absent, dependence/crosswalk assumptions, and unstable tail - remain G5/G2 limitations rather than evidence for the semantics gap.
