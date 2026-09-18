# Numerical-method comparison

| family | examples | discretization / solver | convergence evidence | principal numerical risk |
|---|---|---|---|---|
| ray tracing / sampling | B10247007, B10699002, B10699008 | 1000 rays per beam, deterministic recurrences or image paths | partial to strong depending on paper | entry sampling and finite ray population |
| radiosity / wall coupling | B10247007, B10286058, B10699008 | wall cells, SOR or linear system | B10247007 and B10699002 strongest | cell-center approximation and conditioning |
| view factors / numerical integration | B90002072, B10319002 | surface integrals and centroid reductions | generally limited | quadrature and geometric visibility |
| image-path truncation | B10386003, Blind Run | finite reflection order or image index range | Blind Run checks K; B10386003 does not show a truncation study | unreported tail bias |
| one-bounce / dominant-zone | B10319002, B90005018 | direct numerical integrals | local checks only | omitted secondary reflections are model error, not numerical error |
| stochastic / weighted | B90045020 | limiting mixture and Monte Carlo histories | statistical spread shown, uncertainty incomplete | random-reflection law and Monte Carlo sampling error |

The references make the numerical-error/model-error distinction essential. Increasing the grid or reflection count cannot repair an omitted physical mechanism. Conversely, a physically richer model is not trustworthy if the discretization or truncation is not converged.

The Blind Run recorded K, area quadrature, time-grid and image-vs-explicit-path checks. This is a strength relative to most references, but it verifies only the selected model.
