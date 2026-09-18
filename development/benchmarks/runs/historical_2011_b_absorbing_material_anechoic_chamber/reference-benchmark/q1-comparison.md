# Q1 comparison: wedge reflection model

## Common content

All eleven papers model Q1 as geometric reflection in the empty space between two wedge faces. Common outputs are reflection count, final direction and surviving intensity/power. Most use the problem's cosine-type incidence dependence for the per-hit reflectivity. The papers generally avoid diffraction and edge scattering.

## Closure differences

- B10286058 explicitly fixes a ray entering from the left wedge tip. This makes its recurrence computable, but it is an added initial condition rather than an unambiguous fact in the statement.
- B10319002 derives useful special cases with `x=0` and a ray through the vertex, then projects to 3D. The visual pages show that these are validation cases, not a full arbitrary-entry closure.
- B10145011 and B10293022 use auxiliary or normalized image geometry. They give a usable algorithm, but the mapping from an arbitrary physical entry point to the normalized construction is not always explicit.
- B10247007 samples entry positions and reports that the entry location changes the direction, count and intensity. This is the clearest evidence that entry position is a state variable.
- B10699008 makes entry position part of the characteristic-ray model and separates the analytic large-angle regime from the simulated small-angle regime.
- B90045020 first handles tip entry and then extends to arbitrary height, showing that the initial-condition issue is recognized but requires an extra generalization.

## Agreement with the Blind Run

The frozen Blind Run added an entry coordinate `y0` and retained a parametric Q1 result because the problem statement does not provide a unique entry point or numerical wedge dimensions. The reference set supports this decision. The difference is methodological: some references silently choose a canonical entry, while the more careful ones sample or expose entry dependence.

## Post-hoc conclusion

Q1 is not a single numerical benchmark. A defensible answer must either (a) state a canonical entry and call it an assumption, (b) provide a family of results over entry positions, or (c) report the result as under-specified. The references do not remove this ambiguity; they demonstrate it.
