# Q1 Feature Analysis

## Descriptor audit

- Shape: 1,974×729 training and 50×729 prediction.
- Constant columns: 225; modal frequency ≥0.99: 278.
- Exact duplicate columns: 264; absolute-correlation pairs ≥0.95: 658.
- Standard-deviation scale ratio: 6.34e+06; robust |z|>10 cells: 2016.
- Nonfinite or missing training cells: 0 / 0.

Fold-local filtering removes columns with training-fold modal frequency ≥0.995 and exact duplicates, then an F-regression screen selects 20 columns. This learned policy is fitted inside every inner and outer training fold. The final list is fitted only after model selection freezes; test rows never participate.

## Final full-training Q1 list

| Descriptor | Supplied meaning | F score | Fold frequency | Elite empirical 10–90% |
| --- | --- | --- | --- | --- |
| MDEC-23 | Molecular distance edge between all secondary and tertiary carbons | 803.5 | 1.00 | [15.944, 37.238] |
| MLogP | Mannhold LogP | 767.6 | 1.00 | [2.560, 4.100] |
| LipoaffinityIndex | Lipoaffinity index | 629.3 | 1.00 | [6.090, 12.097] |
| maxsOH | Maximum atom-type E-State: -OH | 548.9 | 1.00 | [0.000, 10.105] |
| minsOH | Minimum atom-type E-State: -OH | 547.4 | 1.00 | [0.000, 9.934] |
| nC | Number of carbon atoms | 528.0 | 1.00 | [16.000, 29.000] |
| nT6Ring | Number of 6-membered rings (includes counts from fused rings) | 474.6 | 1.00 | [2.000, 4.000] |
| n6Ring | Number of 6-membered rings | 452.7 | 1.00 | [2.000, 4.000] |
| minsssN | Minimum atom-type E-State: >N- | 449.1 | 1.00 | [0.000, 2.356] |
| BCUTp-1h | nlow highest polarizability weighted BCUTS  | 443.6 | 1.00 | [10.353, 13.700] |
| C2SP2 | Doubly bound carbon bound to two other carbons  | 438.8 | 1.00 | [5.000, 17.000] |
| hmin | Minimum H E-State | 438.1 | 1.00 | [-0.273, 0.281] |
| AMR | Molar refractivity | 435.1 | 1.00 | [83.152, 146.246] |
| SwHBa | Sum of E-States for weak Hydrogen Bond acceptors | 430.2 | 1.00 | [9.866, 33.208] |
| maxsssN | Maximum atom-type E-State: >N- | 424.0 | 1.00 | [0.000, 2.356] |
| MDEC-22 | Molecular distance edge between all secondary carbons  | 422.6 | 0.80 | [5.900, 25.573] |
| SP-5 | Simple path, order 5 | 420.7 | 0.80 | [4.880, 9.308] |
| SaaCH | Sum of atom-type E-State: :CH: | 419.5 | 1.00 | [5.954, 25.966] |
| CrippenLogP | Crippen's LogP | 403.9 | 0.60 | [3.767, 6.186] |
| maxHsOH | Maximum atom-type H E-State: -OH | 395.6 | 0.40 | [0.000, 0.639] |

The mean pairwise fold Jaccard is 0.812 (range 0.739–0.905). Nineteen of the final features appear in at least three of five folds; `maxHsOH` appears in two, while `C1SP2` is the stable alternative excluded by the final full-training cut. The list is interpreted as predictive association and model importance. It is not evidence of a molecular causal mechanism.
