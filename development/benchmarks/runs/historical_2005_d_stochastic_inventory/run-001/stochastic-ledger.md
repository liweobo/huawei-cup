# Stochastic primitive ledger

| name | meaning | support | distribution / parameters | provenance / source | iid_or_dependent | time_dependence / correlation | observed_or_assumed | sampling_method |
|---|---|---|---|---|---|---|---|---|
| X in Q1/Q3 | supplier lead time, days | nonnegative; exact support unspecified | unspecified F; no automatic parametric family | GIVEN randomness, PARAMETERIZED law; Q1/Q3 | unspecified | unspecified | random mechanism given, joint law unknown | symbolic expectation only until F supplied |
| X1 in Q2 | product 1 lead time | empirical support in inputs.json, 0..7 days | empirical probability count/n, n=36 | ESTIMATED from Q2 ordered list | iid over cycles ASSUMED | stationarity ASSUMED; lag-1 and split-half diagnostics retained | observations given; population law estimated | uniform U mapped through ordered empirical inverse CDF |
| X2 in Q2 | product 2 lead time | empirical support 1..5 days | empirical probability count/n, n=43 | ESTIMATED | iid over cycles ASSUMED | same qualifications; not synchronized with X1/X3 | same | same |
| X3 in Q2 | product 3 lead time | empirical support 1..6 days | empirical probability count/n, n=61 | ESTIMATED | iid over cycles ASSUMED | same qualifications | same | same |
| X in Q4 | common lead for joint arrival | [1,3] days | Uniform(1,3) | GIVEN uniform/range; continuous interpretation ASSUMED | iid over cycles ASSUMED | perfect common arrival dependence between products; no cross-order correlation given | source law + declared independence | 1+2U |
| X discrete alternative | integer-day interpretation | {1,2,3} | masses 1/3 each | SCENARIO; ambiguity sensitivity | iid | common across products | scenario | inverse CDF |
| U | pseudo-uniform auxiliary | [0,1) | uniform | DERIVED implementation primitive | independent streams per replication | reused across compared policies at matching cycle/order index | RNG | NumPy PCG64 |
| M_d in Q5 | shared daily demand multiplier | {.5,1.5} | equal mass | SCENARIO; no empirical demand data | iid over days, common across products | deterministic multiplier 1.25 after day 60; hence nonstationary demand rates | explicit assumed stress scenario | U<.5 selects .5, otherwise 1.5 |

The Q2 PMFs do not assert zero real probability above the sample maximum. No Normal, Poisson or Exponential distribution is used. Block-resampling diagnostics retain local observation order; short histories cannot establish independence or reliably estimate rare tail risk. Empirical-law optimization is conditional on that estimated law.

Q5 uses a bounded, transparent two-point scenario to test event handling/adaptation, not because Monte Carlo requires that law. Alternatives include independent product multipliers or constant demand; the deterministic multiplier-one special case is checked. Scenario means are conditional expectations under the explicitly selected probability law; they are not expectations inferred from real demand observations.

RNG provenance: NumPy version and generator implementation are in results/environment.json. SeedSequence([20260920, namespace, replication_id]) assigns independent replication streams. Policy comparisons reuse the same lead U per cycle index (Q1-Q4) or order index (Q5). Q5 demand uses a separate stream from lead time. Unused lead draws are not consumed by demand draws. Search uses exact expectations, hence has no finite random search scenarios to reuse as evaluation data.
