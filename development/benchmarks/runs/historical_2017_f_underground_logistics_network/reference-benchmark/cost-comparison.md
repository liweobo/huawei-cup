# Cost Definition And Accounting

## Common Units, Different Boundaries

Source construction rates are yuan/km of **physical** tunnel:10t double/four
track4e8/5e8;5t double/four track3e8/3.5e8. Primary/secondary stations cost
1.5e8/1e8yuan each. Park/internal park node capital is excluded. Transport
rate1yuan/(t km) includes vehicles/equipment depreciation. Source life100years
and annual1% depreciation do not require adding both amortization and another
1% charge. Run-002 uses capital*0.01/365 once.

| Reference | Transport / tunnel / station treatment | Daily conversion | Numerical evidence and accounting qualification |
|---|---|---|---|
| F10256001 p20,25 |Flow-distance /2; upper-triangular capital plus station count |Annual1% shown; annual result versus daily flow needs reconciliation |5,756,533,247yuan annual claim; no supported daily total comparison |
| F10294003 pp25-26 |Transport1,124,925.52/day;597.04yi-yuan capital |1%/360 |2,783,300yuan/day claim; unit-price/rate inconsistencies and rounding |
| F10486024 pp17-22 |Ring and local transport plus capital-recovery annuity |Annuity/365 rather than simple1%/365 |Park component7,261,591.85; core transport108,210.3; local component tables, no reconciled common total |
| F10703002 pp19-24 |Cost/time objective and construction result |Time basis insufficiently explicit |182yi-yuan; not treated as a daily total |
| F10710008 pp13-14 |Physical link expressions, transport factor2 on some directed sums |1%/365 stated |407wan-yuan/day claim; displayed component units/totals do not cleanly reconcile |
| F90005027 pp22-30 |Explicit triangular physical links; inverse-path allocation; station term separately defined |Depreciation objective requires term reconciliation |No consistently auditable common total adopted; not invented by summing unlike table values |
| FK0263 pp21-32 |Physical links once; core directional flow sums; balanced local flows doubled |1/(365*100), equivalent to1%/365 |248.13wan-yuan/day=128.78 capital+119.35 transport from rounded components; surface residual outside boundary |

No definite case of **physical tunnel double counting** is established by this
review. Triangular sums and explicit unique link lists in several papers argue
against a blanket accusation. F10703002's double-index notation and other
transport factors remain ambiguous without a reconciled physical-edge ledger.

## Frozen Cost Reconstruction

| Component | Yuan/day |
|---|---:|
| Underground transport |1,997,272.066880 |
| Euclidean surface access proxy |47,318.678926 |
| Physical-tunnel depreciation |90,370,340.288598 |
| Station depreciation |808,219.178082 |
| Total conditional cost |93,223,150.212486 |

Components sum to the stated total at printed precision. Frozen independent
full-precision objective reconstruction residual is7.45e-8yuan/day. These
numbers remain conditional on design, service and static feasibility; no
operationally feasible global minimum is implied.

Run-002 includes a measurable local-access proxy but lacks unknown intra-zone
road distance. References commonly omit a separately reconciled surface
residual/access cost. Restoring all service and surface terms could change any
ranking, and is outside this no-resolve benchmark.

## Allowed Arithmetic, Not New Optimization

`formula-checks.json` records only printed-component additions, nominal payload/
dispatch arithmetic, a growth-index check and displayed reference contradictions.
It does not run location, routing, dispatch or expansion search. FK0263's
35.29+55.15+29=119.44km is a sum of its reported physical lengths, not a new
geometric network reconstruction or proof of coverage.
