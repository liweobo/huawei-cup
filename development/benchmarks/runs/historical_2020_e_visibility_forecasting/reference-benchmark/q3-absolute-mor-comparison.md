# Q3 absolute-MOR comparison

| ID | Claimed output | Scale source | Provenance | Independent highway MOR validation | Identifiability |
|---|---|---|---|---|---|
| Frozen | RELATIVE_VISIBILITY_PROXY | fixed ROI contrast, dimensionless | recovered image only | unavailable | absolute MOR correctly refused |
| R1 | ABSOLUTE_MOR_METRES, 105–140m | dark-channel beta from two regions assumed 9m apart | external road-marking dimension + author scene assumption | none | PARTIALLY_SUPPORTED |
| R2 | ABSOLUTE_MOR_METRES, figure ≈30–65m | `d=λ/(v−vh)`, 3.5m scene segment assumption | external lane width + author longitudinal equivalence | none | PARTIALLY_SUPPORTED |
| R3 | ABSOLUTE_MOR_METRES, 75–90m | dark channel, cross ratio, 6m/9m markings, 6m camera height, C0=1 | author assumptions/external dimensions | none | PARTIALLY_SUPPORTED |
| R4 | ABSOLUTE_MOR_METRES, ≈47±10m | 6m divider calibration, contrast threshold, dark channel, C0=1 | external dimension + author scene points/assumptions | none | PARTIALLY_SUPPORTED |
| R5 | ABSOLUTE_MOR_METRES, 30–68m | 6m/9m markings, 10m camera height, dark channel | external ranges + author fixed height/scene mapping | none | PARTIALLY_SUPPORTED |
| R6 | ABSOLUTE_MOR_METRES, 89–95m | prose promises calibration; printed code hard-codes distance 30m | AUTHOR_ASSUMPTION / UNSTATED | none | UNSUPPORTED |

Every reference imports a physical scale or contrast convention that the frozen source recovery did not independently obtain. Five provide a conditional physical chain but leave scene applicability and error unverified. R6's disclosed implementation breaks its prose calibration chain. No consensus can upgrade any dimension or constant to `PROBLEM_GIVEN_FACT` or `RECOVERED_SOURCE_FACT`.
