# Modeling assumptions / domain knowledge (not problem facts)

| ID | Assumption / choice | Why needed; reasonable range | Dependence / status |
|---|---|---|---|
| A1 | Smooth planar, specular interface; u'=u−2(u·n)n | Closes reflection direction; equal-angle law verified from OpenStax | EXTERNAL_DOMAIN_KNOWLEDGE; compatible with no scattering. No diffuse re-emission invented from M=ρE |
| A2 | Only the reflected branch is followed in Q1; lost fraction is absorbed/removed from the modeled ray channel | Q1 restricts interface reflection in one air gap; no transmission law supplied | Removed energy need not all be microscopic heat. Cannot predict transmitted return paths |
| A3 | Wedge gap is the triangular void between identical touching ridges; d=2h tanα | Derives Fig2 geometry; h,d,α not independently adjustable | DERIVED, no fitted dimensions; normalized h=1 m examples merely choose a geometric scale |
| A4 | Add entry y₀ as an input; no unique ray result follows from angles alone | Landing coordinate controls reflection count | DERIVED required state; uniform y₀ sampling used only as explicitly labeled SIMULATED_ILLUMINATION, not as a measured incidence distribution |
| A5 | Source emission zero outside forward cosine hemisphere | Closes F03's stated −π/2…π/2 domain, avoids negative power | ASSUMED extension; no isotropic/backside source added |
| A6 | Quiet square is at y=L, x,z∈[−s/2,s/2]; measure incident power without perturbing propagation | Fig6 locates patch on end wall; receiver's own influence excluded by problem | Geometric interpretation supported by figure; receiver is a nonperturbing monitor, reflected waves may later return |
| A7 | Use the problem's sum of reflected powers, without coherent cross terms | F05 explicitly defines power-sum metric; no frequency or reflection phase supplied | No complex variable arises. This is not proof of coherent field cancellation or actual instrument error |
| A8 | Initial I_*=1 W/sr for normalized output; retain symbolic scale in interpretation | Absolute scale unspecified; cancels from γ exactly | ASSUMED normalization, not a measured source power; scale-invariance checked |
| A9 | Quasi-static snapshots during the 4 s motion | Prescribed geometrical/radiometric model; no transient field model supplied | No claim about nanosecond waveform dynamics; t is an input coordinate, no train/test split |
| A10 | Q2 effective ρ=0.05 obeys the same cosine-incidence law | The problem explicitly calls it an equivalent flat normal reflectivity | GIVEN modeling substitution; not independently validated by Q1 |
| A11 | Edges/apex hits treated as undefined, not assigned arbitrary normals | Edge diffraction is excluded, facet normal is not unique there | Measure-zero ray inputs; logged explicitly, not silently counted as absorption |

Numerical K, area quadrature order, tolerance and time grid are in the experiment protocol and checked by refinement; they are not physical parameters. Sensitivity scenarios for ρ and angular opening are transparent perturbations, not uncertainty confidence intervals. No unobserved permittivity, magnetic permeability, refractive index, wavelength, or chamber roughness is filled in.

**PARAMETER_IDENTIFIABILITY_LIMITED** applies to any attempted reconstruction of complex material response: two effective power coefficients cannot identify complex ε,μ, phase, or thickness. None is estimated here. There are no calibration data; physical tests and alternate geometric calculations provide weaker validation evidence only.
