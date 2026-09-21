# Q4 Results

Status: PARTIAL. Source day is t=0; construction year y demand multiplier1.05^y.
Q2 design stays frozen. Equal annual construction work is
1086.520217084km/year. Divisible work may span years, but tunnels
remain unusable until fully completed. All tunnels depend on commissioned
endpoints; station commissioning years are independently reconstructed.

| Year | Demand multiplier | Completed tunnels | Underground share | Regions above congestion4 | Full target |
| --- | --- | --- | --- | --- | --- |
| 1 | 1.050000000 | 581 | 0.177277 | 82 | False |
| 2 | 1.102500000 | 719 | 0.471822 | 37 | False |
| 3 | 1.157625000 | 815 | 0.637780 | 11 | False |
| 4 | 1.215506250 | 893 | 0.686736 | 8 | False |
| 5 | 1.276281563 | 962 | 0.703482 | 6 | False |
| 6 | 1.340095641 | 1024 | 0.731649 | 4 | False |
| 7 | 1.407100423 | 1078 | 0.724938 | 5 | False |
| 8 | 1.477455444 | 1120 | 0.730981 | 3 | False |

Commissioned primary backbones are connected. Usable saved routes are uniformly
throttled until ground/station/line capacity passes, and all remaining freight
is explicitly surface fallback. This is service accounting, not a full-target
construction recommendation. Every year fails the full target; no partial
network is called capable of clearing its total original demand underground.
Timed annual operations, station build durations and annual budgets are not
established by this static phasing model.

Unchanged full-design retained-routing first static saturation:
year2. This is not a reoptimized-routing upper bound.
Thirty-year multiplier=4.321942375; status SATURATES_BEFORE_30_YEARS.
At least432 additional parallel-equivalent
station modules would be needed under retained per-node loads. This is a
resource lower-bound scenario, not a feasible expansion layout or timetable.
Four tracks alone cannot cure a station-dispatch bottleneck. Any further design
must explicitly add locations/corridors, reallocate OD and validate yearly
operations; no such future expansion is silently inserted into Q2.
