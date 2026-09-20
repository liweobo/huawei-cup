# Demand Ledger

Real-data status: MISSING_REQUIRED_ATTACHMENT. No original OD cells were loaded. A zero-sized table would misrepresent unavailable data, so counts/totals are null in the audit.

| origin | destination | flow/demand | unit | time basis | source |
|---|---|---|---|---|---|
| Horizontal-axis original label (missing) | Vertical-axis original label (missing) | UNKNOWN | tonne | Not printed in accessible body; daily interpretation unverified | Attachment description, rendered p6 |

If supplied as rows=vertical and columns=horizontal, D[origin,destination] = cell[destination,origin]. Verify original axis labels, rather than automatically treating rows as origins. D_ij and D_ji are distinct; symmetry must be tested, not imposed. Inbound and outbound may be added only for the specific region total and ground-exchange capacity, preserving directional flows for routing and design.

Topology and demand are independent: a zero OD does not remove a corridor, and a constructed corridor need not carry direct OD demand. Intrazonal cells require explicit local handling, not self-loop tunnels. Missing/negative/duplicate cells, park labels, totals and period cannot be audited until the table exists.

The six directed oracle records in `inputs/oracle.json` and `inputs/oracle-od.csv` are artificial tonnes/day, with source `SCENARIO_ASSUMED`. They are audited and reported only under SYNTHETIC_CODE_VALIDATION. They must never populate an official 2017F answer table.
