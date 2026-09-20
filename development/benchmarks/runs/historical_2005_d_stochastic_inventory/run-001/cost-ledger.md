# Cost ledger

Let I_i(t) be item units for Q1/Q2 and m³ for Q3/Q4; d_i is the corresponding units/day rate. a_i is own capacity, b_i is arrival target; h_i,g_i,p_i are costs in those same stock units.

| component | formula per cycle | unit | timing | source / qualification |
|---|---|---|---|---|
| fixed order | k per order, once for the entire joint order | yuan/order -> yuan/cycle | charged at order time | c1 GIVEN |
| own holding | h_i integral min(I_i(t),a_i) dt | yuan/(stock unit.day) × stock unit.day | continuous accrual | c2 GIVEN; own-first operation ASSUMED |
| rented holding / overflow | g_i integral max(I_i(t)-a_i,0) dt | same | continuous accrual | c3 and renting overflow GIVEN; no clipping |
| lost sales, primary | p_i × lost quantity | yuan/stock unit × stock unit | when unmet demand occurs | Q1 interpretation; SOURCE_UNIT_CONFLICT in Q2/Q3 |
| alternative shortage exposure | p_i integral cumulative_lost_since_stockout(t) dt | yuan/(stock unit.day) × stock unit.day | until replenishment resets exposure | SCENARIO interpretation of printed time unit |
| purchase, disposal, rejection, backlog, delayed-service charge | not included | no supplied price/charge | N/A | NOT_GIVEN; not estimated as zero-valued facts |

Q4 converts h=c2/v, g=c3/v and p=c4/v before multiplying by inventory volume. Rates are d=r*v. Summing components yields total cost exactly. Cost/day divides total yuan by actual calendar days, not by number of cycles. Joint c1=10 yuan is charged once per joint order, never three times. Q5 uses the primary lost-sale interpretation and charges orders placed before the finite terminal boundary; outstanding orders are not dropped from the cost record.

No service constraint appears in the source. Service metrics are descriptive: cycle stockout probability P(any unmet demand during cycle), per-item demand fill rate E[fulfilled]/E[requested], and time fraction empty are different quantities. Joint aggregate fill is volume-weighted and labeled accordingly. No probability-of-no-stockout target is invented.
