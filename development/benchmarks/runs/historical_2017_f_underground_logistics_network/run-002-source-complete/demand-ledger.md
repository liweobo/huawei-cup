# Directed Demand Ledger

Source: `现状OD数据及其他数据.xls`, sheet `现状全天OD`, data B2:DK115. Original orientation COLUMN=ORIGIN, ROW=DESTINATION. Units: DOC final paragraph says tonnes; sheet title says full day. `inputs/directed-demand.csv` retains origin, destination, tonnes_per_day and original source_cell for every value, including zeros and diagonal entries.

| Quantity | Meaning | Status |
|---|---|---|
| D[o,d] | Original directed full-day demand | GIVEN, independently transposed from XLS orientation |
| D[i,i] | 895:2.92t;896:0.52t; all other original diagonal entries zero | GIVEN; preserved surface-local in A03 |
| a_is | Fraction of region endpoint freight assigned to secondary | ASSUMED model decision; rows sum1 |
| M | Park identity plus region/secondary allocation matrix | DERIVED from selected allocation |
| B=M^T D' M | Aggregated directed network endpoint demand | DERIVED, not symmetrized |
| B[k,k] | Both endpoints use one station; ground/local handling but no tunnel | DERIVED; tracked separately, not dropped |
| f[k,u,v] | Origin-commodity flow along a constructed directed arc | OPTIMIZED; not original demand |
| 1.05^y D | Future original OD, y=0 source year | GIVEN growth applied as DERIVED scenario projection |

Original source audit reports 163,406.46 tonnes/day total and 128,865.538 park-related tonnes/day. Counts/totals are checked from the CSV independently of the primary solver. Demand and topology are separate: zero OD does not delete a candidate corridor; a corridor does not create freight. Each failure/growth case accounts for served, retained surface/local and unserved freight explicitly. No upper-triangle reduction or averaging.
