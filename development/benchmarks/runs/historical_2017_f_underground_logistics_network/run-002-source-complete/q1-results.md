# Q1 Results

Status: PARTIAL at whole-question level; valid conditional allocation/count/
location/throughput outputs. All110 centres are served within3km. The restricted
layout has118 primary and118 secondary stations; primaries have zero ground
exchange, while secondaries handle the allocated regional exchange.
This expensive one-to-one hierarchy is not a recommended optimal facility plan.

| Design | Primary | Secondary | Physical tunnels | Daily yuan (conditional static objective) |
| --- | --- | --- | --- | --- |
| Real-data baseline | 150 | 150 | 1452 | 118,950,629.848876 |
| Consolidated | 118 | 118 | 1128 | 96,191,691.812863 |
| Eight deletions | 118 | 118 | 1120 | 93,223,150.212486 |

Every station's actual coordinates, source seed, parent, region allocation,
radius, ground exchange and underground inbound/outbound are saved in
results/primary/node-results.json. A readable complete table is node-results.md.
Regions may split across stations; assignment fractions sum to one.
B=M.T D_offdiag M preserves all off-diagonal demand.

Park transfer ratios use Euclidean nearest-primary distance:

| Park | Nearest primary | Numerator t/day | Denominator t/day | Ratio |
| --- | --- | --- | --- | --- |
| K1 | P060 | 0.000000 | 19299.366000 | 0.000000000 |
| K2 | P088 | 0.000000 | 18981.112000 | 0.000000000 |
| K3 | P076 | 0.000000 | 18684.818000 | 0.000000000 |
| K4 | P091 | 0.000000 | 8923.678000 | 0.000000000 |

For primary stations nearest to no park the source denominator is undefined.
All are explicitly listed as NOT_APPLICABLE_NO_ASSOCIATED_PARK_DENOMINATOR,
not assigned a fictitious0 ratio. This unresolved meaning of the requested
per-primary ratio prevents claiming all Q1 outputs unconditionally complete.
Known region diagonal3.44t/day remains local surface freight. Co-assigned
station-local174.816260543t/day has no tunnel movement but
remains accounted as station ground handling.
