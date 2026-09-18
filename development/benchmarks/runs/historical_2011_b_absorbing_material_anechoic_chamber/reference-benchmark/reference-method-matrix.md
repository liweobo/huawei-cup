# Reference method matrix

| ID | Q1 physical abstraction | Q1 closure choice | Q2 abstraction | Q2 closure / truncation | Numerical verification visible in paper |
|---|---|---|---|---|---|
| B10145011 | wedge rotation group + energy vector | auxiliary wedge construction | Fresnel-Huygens / Fresnel main zone | finite dominant reflection region | limited from extracted report |
| B10247007 | ray sampling and weighted statistics | entry position sampled, not fixed | wall-zone coupling | 5,400 regions, SOR | grid and energy checks |
| B10286058 | recursive 2D ray model, 3D extension | left tip entry explicitly assumed | radiosity / global illumination | about 146,400 cells, progressive refinement | simulation tables; convergence detail limited |
| B10293022 | image method with incidence-angle distribution | normalized image geometry | dynamic wall balance | 1,464 1 m cells | no strong grid-convergence evidence found |
| B10319002 | recursive geometry and projection | special x=0 / vertex cases | surface-to-surface radiation + centroid simplification | six-centroid linear system | two models compared; no independent validation |
| B10386003 | virtual images in circular/cylindrical extension | image-line geometry | infinite virtual-image chamber | 600 reflections, -100..100 indices | no systematic truncation convergence |
| B10699002 | geometric optics and image paths | explicit ray examples | image paths plus Huygens wall elements | tested cell edge sizes down to 0.5 m | strongest visible grid-convergence table |
| B10699008 | characteristic rays | entry position is a model variable; analytic and simulated regimes separated | wall exitance coupling | linear system A M=b | qualitative range comparison; limited grid evidence |
| B90002072 | angle recursion | general entry not fully closed | view factors / radiation coefficients | six-wall equations, numerical integration | limited integration/grid evidence |
| B90005018 | critical-state piecewise ray model | critical cases and coordinate decomposition | direct + one-bounce micro-integrals | multi-reflection term left unknown | no closure for all reflections |
| B90045020 | image model, tip then arbitrary entry | progressive entry generalization | weighted limiting model + Monte Carlo | finite random histories | model discrepancy visible; statistical error details limited |

The matrix shows no single reference formulation. The common structure is geometric ray attenuation for Q1 and a power/radiosity approximation for Q2, but the treatment of entry data, secondary reflections, finite-area effects and truncation varies materially.
