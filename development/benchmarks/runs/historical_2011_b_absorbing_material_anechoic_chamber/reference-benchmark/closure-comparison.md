# Closure comparison

## What must be specified

For a reproducible Q1/Q2 calculation, the state must include geometry, source location and direction, entry or emission distribution, material law, receiver/quiet-zone geometry, interface rules and a termination or convergence rule. The problem statement gives substantial chamber dimensions and two reflectivities, but it does not uniquely specify every Q1 entry state or the full electromagnetic material response.

## Reference evidence

- Entry position is sampled or parameterized in B10247007, B10699008 and B90045020.
- Tip or vertex entry is fixed in B10286058 and in special derivations of B10319002.
- Normalized image constructions are used by B10145011 and B10293022 without a universal arbitrary-entry mapping being visible.
- B90002072 and B90005018 leave parts of the general path population implicit.
- B10386003 closes Q2 with an infinite image construction but uses a fixed 600-reflection cutoff.
- B90005018 explicitly says that multiple reflections are not computed and are left as an unknown small correction.

## Assessment

The reference papers confirm a domain-neutral closure issue rather than a missing electromagnetic formula. Different authors close the same under-specified parts by adding a canonical entry, averaging over entry, truncating a path family, or leaving an uncomputed correction. Those choices change the answer by more than the displayed numerical precision.

The frozen Blind Run handled this better than a silent canonical choice by adding `y0` as an assumption and returning a parametric Q1 result. It still exposed that the Skill did not force an early closure gate before model construction.

## Gate candidate

`MECHANISM_MODEL_CLOSURE_GATE` should be the TOP-1 gap. Before simulation, a mechanism task should answer:

1. Is the initial/source state uniquely given, or is a distribution/parameterization required?
2. Are all interfaces and receiver conditions specified?
3. Is the material law sufficient for the chosen abstraction?
4. Is the path/iteration termination rule part of the model and numerically verified?

If any answer is no, the output must be labelled parametric, scenario-based or partial, and the added closure assumption must be provenance-tagged.
