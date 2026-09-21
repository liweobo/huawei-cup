# Real-Data Baseline

Per-region allocations with2000t constructive fill target, one primary per
secondary, four park spokes and a connected sparse primary backbone. Every
original directed off-diagonal OD is preserved. This is a real-data static
baseline, not a synthetic oracle or certified operating timetable.

| Design | Primary | Secondary | Physical tunnels | Daily yuan (conditional static objective) |
| --- | --- | --- | --- | --- |
| Real-data baseline | 150 | 150 | 1452 | 118,950,629.848876 |
| Consolidated | 118 | 118 | 1128 | 96,191,691.812863 |
| Eight deletions | 118 | 118 | 1120 | 93,223,150.212486 |

The3000/2400t attempts were rejected as LP-INFEASIBLE. Changing source station
capacity was not allowed. The diagnostic900-departure relaxation is excluded.
The baseline and primary have identical source bytes, service policy, resource
limits, train configuration and objective boundary. Consolidation changes only
design/assignments; accepted tunnel deletions reroute all commodities.
The baseline is a valid static relaxation comparator, not a fully legal
daily-clearing solution to all of Q2.
