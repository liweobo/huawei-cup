# Numerical Comparability

Direct numerical comparison requires the same data, population, contaminant, standard, units, quantile, censoring treatment, and time scope. No pair of reported reference results satisfies this contract.

| reference | reported q | population/geography | food/contaminant | comparator | comparability decision |
|---|---:|---|---|---|---|
| `REF-01` | `41.9259 µg/person-day` | Beijing Dongcheng illustrative sample | mixed foods / lead | blood-lead concentration | `NOT_DIRECTLY_COMPARABLE`; comparator invalid |
| `REF-02` | none | simulated/unspecified | generic | unspecified national intake standard | `NOT_DIRECTLY_COMPARABLE` |
| `REF-03` | none | unspecified | generic | unspecified authority standard | `NOT_DIRECTLY_COMPARABLE` |
| `REF-04` | `0.027 mg/person-day` | assumed `60 kg`; region unspecified | meat / lead | converted PTWI `0.214 mg/person-day` | `NOT_DIRECTLY_COMPARABLE` to other papers |
| `REF-05` | `0.989689 µg` | North-I region, spring | cereals / lead | reported cereal-content limit `0.2 mg` | `NOT_DIRECTLY_COMPARABLE`; comparator invalid |
| `REF-06` | none | same as `REF-02` | same | same | exact duplicate |

The frozen run's values are synthetic in a deliberately unspecified mass/person-day unit and therefore cannot be numerically compared with any reference result. Only structural comparisons - target, formulas, assumptions, validation, and semantics - are legitimate.
