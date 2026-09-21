# Output Semantics Comparison

| reference/output | formula | range | unit | interpretation | absolute/relative | probability semantics | compliance semantics | ranking | classification |
|---|---|---|---|---|---|---|---|---|---|
| `REF-01` PI | `count(X>PTDI)/N` | `[0,1]` | dimensionless | empirical exceedance share | absolute conditional on sample design | yes, as an empirical proportion; not automatically harm probability | screening only | may prioritize regions | no fixed class |
| `REF-01` tail quantile | `F^-1(0.99999)` | physical support | `µg/person-day` in example | extreme dietary intake | absolute | no | only with a matched intake threshold | no | safe language used |
| `REF-01` reported conclusion | compare `41.9259 µg/person-day` with `100 µg/L` blood lead | not coherent | incompatible | claimed poisoning probability/compliance | neither valid | unsupported | unsupported | no | invalidly “safe” |
| `REF-02` / `REF-06` CDF and quantile | `F_Z(z)`, `F_Z(q)=0.99999` | CDF `[0,1]`; q physical | intake mass/person-day | exposure distribution and right quantile | absolute | CDF has probability semantics; q does not | warning if q exceeds applicable daily standard | no | binary warning |
| `REF-03` CDF and quantile | product CDF; weighted/order-statistic MC | CDF `[0,1]`; q physical | intake mass/person-day | exposure distribution and right quantile | absolute | CDF only | safe if q below applicable standard | no | binary safe/warning |
| `REF-04` quantile | MC histogram/order statistic | physical support | `mg/person-day` | age/body-weight scoped exposure tail | absolute | no | comparison with converted `mg/person-day` tolerance | no | binary safety |
| `REF-05` `Pq` | polynomial integral | intended `[0,1]`, not demonstrated globally | dimensionless | exposure CDF | absolute | yes as intended CDF, subject to validity | none by itself | no | none |
| `REF-05` selected q and conclusion | solve `Pq=0.99999`; compare `0.989689 µg` with reported `0.2 mg` food limit | physical support | daily intake vs food content | claimed quantile and national safety | invalid comparison | q is not probability | unsupported due scope/unit mismatch | no | invalidly “safe” |

## Score-to-probability audit

- `weighted score -> safety probability`: not observed.
- `TOPSIS closeness -> probability`: not applicable; no reference uses TOPSIS.
- `fuzzy membership -> real probability`: not observed; `REF-02/06` use fuzzy similarity for matching, then compute a separate probabilistic exposure model.
- `quantile/threshold relation -> harm probability`: observed in `REF-01`.
- `mismatched regulatory threshold -> compliance`: observed in `REF-01` and `REF-05`.

The demonstrated failure is therefore broader than the illustrative “0.82 score = 82% safe” example. It is a mismatch between the mathematical object, comparator, and allowed decision claim.
