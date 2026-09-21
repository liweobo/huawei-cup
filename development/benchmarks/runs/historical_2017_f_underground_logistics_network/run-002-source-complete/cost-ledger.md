# Cost And Capacity Ledger

| Parameter | Value | Unit | Source / status |
|---|---:|---|---|
| Transport | 1 | yuan/(tonne km) | GIVEN, DOC Q2 item3 |
| 10t double-track | 400000000 | yuan/physical km | GIVEN |
| 10t four-track | 500000000 | yuan/physical km | GIVEN |
| 5t double-track | 300000000 | yuan/physical km | GIVEN |
| 5t four-track | 350000000 | yuan/physical km | GIVEN |
| Primary station | 150000000 | yuan/node | GIVEN |
| Secondary station | 100000000 | yuan/node | GIVEN |
| Annual depreciation | 0.01 | per year | GIVEN, not multiplied by another 1/100 |
| Days/year | 365 | days/year | ASSUMED A10 |
| Primary ground exchange | 4000 | tonnes/day | GIVEN tonnes + declared daily interpretation |
| Secondary ground exchange | 3000 | tonnes/day | GIVEN tonnes + declared daily interpretation |
| Vehicle count/train | 8 | vehicles/train | ASSUMED choice within GIVEN4-8 |
| Payload/train | 80 or40 | tonnes/train | DERIVED, park-primary versus other arcs |
| Same-direction line limit | 540 | trains/day/direction | DERIVED upper bound from 18h and2min; not timetable proof |
| Constructed station limit | 90 | departures/day aggregate | DERIVED upper bound from18h and5/h; explicitly not per outgoing edge |
| Speed reference | 48.6 | km/h | DERIVED from GIVEN13.5m/s |

Physical tunnel capital is counted once despite two routing arcs. Directed transport cost counts actual tonne-km in both directions. Daily objective components are saved individually; the independent audit recomputes them from raw coordinates, selected edges, node counts and commodity flows rather than trusting the solver scalar. Local access is a separate Euclidean-rate proxy; park construction and internal park nodes are excluded. Original intra-region travel cost cannot be measured from the centre table and is outside the reported evaluable boundary.
