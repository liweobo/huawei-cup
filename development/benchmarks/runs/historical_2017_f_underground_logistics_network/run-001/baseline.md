# Baseline

Original-instance baseline: NOT RUN. Missing OD, centres, parks and congestion inputs prevent a legal actual node/corridor allocation. No fabricated direct-distance city graph is substituted.

Executed verification baseline: SYNTHETIC_CODE_VALIDATION, eight fixed artificial nodes. Construct the five mandatory park/local corridors plus backbone A-B and B-C, then assign the six directed demands to shortest positive-length paths. All eight nodes form one component; all six OD pairs are reachable. Check own-primary mediation, directional running capacities, conservative station departures, ground exchange, per-commodity conservation and reconstructed capital/transport cost.

Saved output: `results/baseline.json`. It contains seven physical tunnels, fourteen directed arcs, capital 4,281,665,382.639196 yuan, daily depreciation 117,305.900894 yuan/day, transport 9,395.273712 yuan/day and static objective 126,701.174606 yuan/day. These are artificial test results, not 2017F answers or an operationally certified network.

The primary oracle uses identical nodes/demand/costs/validation and changes only which three eligible backbone links are selected. Eight build combinations are exhaustive; no heuristic search claims. Full result components, including failed disconnected designs, are retained in `results/candidate-enumeration.json`.
