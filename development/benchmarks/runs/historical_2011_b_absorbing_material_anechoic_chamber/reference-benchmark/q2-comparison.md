# Q2 comparison: chamber reflected/direct power ratio

## Reported ranges

| reference | rho=0.50 | rho=0.05 | time of minimum |
|---|---:|---:|---:|
| B10145011 | min about 0.207469 | about 0.0203-0.0218 | 2 s |
| B10247007 | about 0.2015-0.2063 | about 0.01247-0.01272 | 2 s |
| B10286058 | min 0.207469 | about 0.0203-0.0218 | 2 s |
| B10293022 | 0.2034-0.2089 | 0.0203-0.0208 | 2 s |
| B10319002 | about 0.142-0.168 in its one-reflection calculation | about 0.014-0.017 | 2 s |
| B10386003 | about 0.0619-0.1011 | about 1.0e-6-1.9e-6 | 2 s |
| B10699002 geometric | about 0.344 | max about 0.0295 | 2 s |
| B10699002 Huygens | about 0.15 | about 0.011 | 2 s |
| B10699008 | 0.1934-0.2117 | 0.0120-0.0136 | 2 s |
| B90002072 | min about 0.2067 | max about 0.011 | 2 s |
| B90005018 | min about 0.039 | min about 0.004 | about 2.2 s |
| B90045020 weighted | about 0.2090 | about 0.0169 | 2 s |
| B90045020 Monte Carlo | about 0.0388 | about 0.0035 | about 1.91-1.96 s |
| Frozen Blind Run | 0.39246-0.39486 | 0.02967-0.02974 | 2 s |

The values are transcribed at the precision supported by tables, plots and extracted text. They are not treated as a common ground truth. The spread is evidence about model choice, not a simple numerical error bar.

## Mechanism families

1. **One-bounce or dominant-zone approximations.** These tend to produce the larger rho=0.05 values near 0.014-0.022 and may omit or bound later interactions.
2. **Finite wall radiosity / view-factor models.** These solve coupled wall equations and usually report rho=0.05 around 0.011-0.0136.
3. **Infinite image-path models.** These can be much smaller, especially when the path truncation and cosine factors suppress most images; B10386003 is the extreme example.
4. **Geometry-plus-Huygens hybrids.** B10699002 shows that a geometric path model and a wall-element wave-inspired model can differ by a factor of several while both are internally coherent.
5. **Weighted or stochastic approximations.** B90045020 exposes the largest model-form discrepancy: its limiting weighted model and Monte Carlo model produce different scales.

## Comparison with the Blind Run

The Blind Run's finite-area image-path power sum is numerically converged for its stated assumptions, but it sits at the high end of the rho=0.05 reference range and is not validated by the reference set. This does not invalidate the run. It means that the reported pass margin (`0.02987` upper certificate versus `0.03`) is conditional on a particular mechanism model and should not be presented as a material certification.
