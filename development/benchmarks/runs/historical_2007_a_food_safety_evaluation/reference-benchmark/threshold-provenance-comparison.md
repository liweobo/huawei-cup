# Threshold Provenance Comparison

| reference | threshold as reported | unit/scope | source/version/date | provenance class | applicability audit |
|---|---|---|---|---|---|
| `REF-01` | PTDI concept; numerical conclusion uses blood lead `<60` relative-safe and `>=100` diagnostic | PTDI should be intake; example uses `µg/L` blood concentration against `µg/person-day` dietary intake | “international” blood-lead standard; no document/version/date | `UNVERIFIED` | `FAIL`: different physical quantity and unit |
| `REF-02` | national warning / daily per-capita pollutant-intake standard | intended intake/person-day | no identifier, value, version, date, food/contaminant scope | `UNSTATED` | `PARTIAL`: semantic type is suitable, provenance unavailable |
| `REF-03` | food-hygiene authority safety standard | intended daily intake | no identifier, value, version, or date | `UNSTATED` | `PARTIAL` |
| `REF-04` | lead `PTWI=0.025 mg/week/kg`; converted at `60 kg` to `0.214 mg/person-day` | toxicological intake by body weight/time, converted to person-day | external references cited; edition/effective date not stated | `EXTERNAL_REFERENCE` / `UNVERIFIED_VERSION` | `PASS` dimensionally for the displayed scenario; provenance incomplete |
| `REF-05` | reported cereal lead limit `0.2 mg` | food-content limit (denominator not retained in comparison) versus daily intake `µg` | `GB 2762-2005`, paper reports issue date `2005-01-25` | `OFFICIAL_STANDARD` | `FAIL`: correct existence/type of source does not make it applicable to the output |
| `REF-06` | same as `REF-02` | same | same | `UNSTATED` | duplicate |

## Boundary audit

- The references do not use arbitrary `0.3/0.6` risk-class boundaries.
- `0.99999` is problem-given probability content, not an author-created risk threshold.
- A ratio boundary of `1` would be mathematically derived from `q/T`; none of the references explicitly constructs this ratio.
- `REF-02/06`'s `10,9,7,5,3,1,0` scale is a fuzzy similarity encoding for data matching, not a safety-class threshold. Its calibration is author-assumed and should not be promoted to probability.
- `REF-03`'s convergence distance threshold and `REF-04`'s numerical tolerance `theta` are algorithmic accuracy thresholds, not regulatory thresholds.

## Implication

Threshold provenance requires both source traceability and semantic applicability. `REF-05` names a formal standard yet still reaches an invalid compliance claim because its threshold governs a different quantity. A source-only checklist is therefore insufficient; the target/output contract must bind threshold, unit, scope, and allowed claim.
