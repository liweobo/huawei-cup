# Risk Semantics Comparison

| reference | mathematical meaning of “risk” | explicit formula/object | probability semantics | principal interpretation | audit |
|---|---|---|---|---|---|
| `REF-01` | mixed: adverse-event possibility/consequence, sample exceedance frequency, extreme-tail exposure, and a Pareto-style index | `P = count(X>PTDI)/N`; tail CDF and `Q_0.99999`; `F=S*W^alpha` | valid only for the sample exceedance statistic under its sampling assumptions; later poisoning-probability claim is not established | probability + quantile + other | `SEMANTICALLY_MIXED`; probability promotion in numerical conclusion |
| `REF-02` | daily pollutant-intake distribution and its extreme quantile | `Z=XY`, `F_Z(z)`, solve `F_Z(z)=0.99999` | CDF probability only; the quantile itself is not a probability | quantile / threshold | coherent but threshold unverified |
| `REF-03` | daily pollutant-intake distribution and quantile | product CDF plus Monte Carlo/order statistic | CDF probability only | quantile / threshold | coherent; no validated numeric output |
| `REF-04` | age-specific absolute intake distribution and quantile relative to PTWI-derived tolerance | moment/matrix exposure distribution; Monte Carlo `Q_0.99999` | CDF probability only | quantile / threshold | dimensionally aligned in displayed example |
| `REF-05` | fitted exposure CDF `Pq` and selected root for `Q_0.99999` | polynomial `F(x)`; solve `F(x)=0.99999` | `Pq` is a CDF value, not harm probability | quantile / purported compliance | comparator has wrong physical scope/unit |
| `REF-06` | same as `REF-02` | same as `REF-02` | same | same | exact duplicate |

## Findings

1. None of the references uses an AHP/TOPSIS/weighted composite score as an absolute risk probability.
2. The observed semantic failures are nevertheless material:
   - `REF-01` moves from an exposure quantile to a statement about lead-poisoning probability while comparing dietary intake with blood concentration.
   - `REF-05` moves from daily intake to regulatory compliance using a food-concentration limit, then generalizes from one region/season/food to national safety.
3. Being bounded in `[0,1]` is not sufficient for probability semantics. The fuzzy similarity weights in `REF-02/06` are matching coefficients; they are not event probabilities.
4. A threshold ratio or quantile comparison can support a conditional decision only when units, scope, population, time, contaminant, and standard applicability match.

The frozen blind run correctly labels `rho=q/T` as a dimensionless margin rather than a probability and forbids a real-world compliance claim without a verified `T`.
