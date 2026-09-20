# 2017F Seventh-Problem Blind Run

Final decision: **C. BLIND_RUN_PARTIAL**. The authorized .doc is verified, but its referenced map, OD, coordinates/areas and congestion attachments are absent from the authorized directory and from the document's embedded objects. Four original subproblems therefore have no justified numerical city solution. Executed synthetic checks are useful code evidence only. No generalizable Skill gap is established.

## 1. Source Provenance

Source directory: https://github.com/zhanwen/MathModel/tree/master/国赛试题/2017年研究生数学建模竞赛试题 . Only the original F .doc content was fetched. Blob `c2dd56c208cf3c7f80f2e52ff1f58ee0a758166f`, SHA256 `7cd51bdf0c6a0392eef93fc84efaf16090262fe94e7bae97d385fee67be28719`, 2,579,456 bytes. Fresh download equals retained source. See `source-provenance/source.json` and `source-provenance/README.md`.

Legacy extraction verified three Word text pieces and 57 visible paragraphs against an independent engine; all six rendered pages inspected. Five original images, two original text boxes, zero native Word tables and zero embedded data files. A renderer-added logo was excluded. Conceptual map node IDs, legend, calibration and coordinates remain EXTRACTION_UNVERIFIED. No excellent solution, answer, competition code or solution blog was accessed.

## 2. Problem Facts

`problem-facts.md` freezes four subproblems and 34 source facts separately from `assumptions.md`. Q1 selects stations/service/transfer rates; Q2 designs tunnels/flows/cost; Q3 improves operation and risk; Q4 phases construction and capacity over time. Essential attachments are missing. Facts were not supplied from the seven future reference papers.

## 3. Graph Definition

`graph-ledger.md` separates parks, underground primaries/secondaries, surface demand zones, access connections and roads. Candidate, existing, built and forbidden sets are distinct. The actual graph is uninstantiated, not an empty graph with zero demand.

## 4. Node Semantics

Four parks are given; primary count is a decision, not automatically four. Region centres are demand representatives, not automatically stations. Coverage of a centre is expressly permitted; no clustering, hidden merge, dropped low-demand region or ignored original intrazonal freight is performed.

## 5. Edge Construction

Each possible real tunnel needs eligibility and endpoint-type provenance before a construction decision. No all-pairs or distance-threshold real graph is generated. The 3 km radius limits service coverage, not tunnel adjacency. Own-primary mediation of secondary connections and connected primary backbone are retained.

## 6. Geometry / Coordinates

The referenced coordinate unit is metres, but values/CRS/origin/projection are missing. No figure pixels become engineering length. Euclidean, geographic, road, tunnel and network-path lengths remain separate. The eight-node oracle explicitly defines its own artificial Cartesian kilometre geometry.

## 7. Weight / Unit Audit

Transport = directed tonnes/day * route km * 1 yuan/(tonne km). Capital costs are yuan per physical tunnel km or per station. Depreciation uses 1%/year and the explicit 365-day assumption. Capacity is never a path weight; direction-sensitive OD is never averaged. Full multimodal cost needs missing surface distances.

## 8. Demand / OD

Original labels/cells/period are absent. Text states horizontal-axis origins send to vertical-axis destinations, so row-origin convention cannot be assumed. `demand-ledger.md` records this. Artificial OD has six directional entries, each unequal to its reverse, and is separately audited by the unchanged `data_audit.py`.

## 9. Capacity

Ground exchange limits 4000/3000 tonnes differ from transit/dispatch capacity; their period still needs verification. Park tunnels use 10t vehicles; others 5t; trains have 4-8 vehicles. Same-direction headway >=2 minutes differs from node dispatch <=5/hour for 18 hours/day. Symmetric tunnel dimensions are designed for max directional load. Daily clearing needs more than these aggregate limits.

## 10. Baseline

Original baseline NOT RUN due to missing inputs. Real execution exists for the explicitly artificial baseline, with fixed eight sites and five local/park corridors plus A-B/B-C backbone. It has seven physical tunnels, one component and six reachable OD pairs. See `baseline.md` and `results/baseline.json`.

## 11. Primary Model

`model.md` defines a conditional facility/coverage/assignment/corridor/commodity-flow formulation. Its real-instance objective and eligibility are not numerically closed. No solver is called for the unavailable original instance.

## 12. Network Design

Build variables differ from route/flow variables. The oracle enumerates three backbone binary choices, all eight subsets, with four connected statically feasible alternatives. Primary selects B-C/A-C. Fixed sites/levels/local corridors are an explicit synthetic restriction, not an original-site optimum.

## 13. Routing / Flow

SciPy Dijkstra uses nonnegative static lengths and `directed=True` on paired arcs. Every design is rerouted before evaluation. The four connected designs' shortest assignments all satisfy the declared static capacities, which makes their unconstrained routing lower bounds attainable and justifies this limited decomposition. It is not a general shortcut for capacity-bound network design.

## 14. Feasibility

Disconnected candidates are rejected and their selectable objectives are null. Hierarchy, reachability, ground exchange, directional running capacity and station departure bounds are checked. No abstract feasible graph is called a surveyed buildable or daily-clearing network. No original feasible solution is claimed.

## 15. Objective

Daily cost has transport plus tunnel/station depreciation, without arbitrary objective weights. Park construction is excluded, outgoing park tunnels included. Vehicle depreciation is already in the given per-tonne-km rate. Q1 congestion/park-priority policy is explicitly an assumption, not a manufactured weighted score.

## 16. Small-Graph Verification

A separate four-node directed graph has 0->2 shortest length 5 (direct edge 9), reverse 2->0 length 8, and isolated node 3. Manual expected distances match Dijkstra and Floyd. This verifies algorithms, not the original instance.

## 17. Connectivity / Reachability

Normal oracle baseline, primary and redundant triangle are connected with all six OD pairs reachable. Independent traversal rebuilds components/isolates from saved edges. Failures list unreachable OD explicitly. Real connectivity and OD reachability remain NOT CHECKED because no grounded graph is available.

## 18. Flow Conservation

Each full-demand solution records 48 commodity-node equations including source/sink RHS. Residuals are zero. `results/independent-audit.json` reconstructs 33 saved graphs/flows without importing the generator; all checks pass. Official flow conservation is NOT_APPLICABLE until actual assignment exists.

## 19. Objective Reconstruction

Physical capital is counted once per tunnel/station; directional route tonne-km and summed arc flow costs agree. All 33 audited saved networks reconstruct consistently; unreachable/infeasible all-demand objectives stay null. The individual components remain machine-readable in each result, not only a solver scalar.

## 20. Robustness / Sensitivity

Twenty-two single-physical-tunnel removals disable both directions. The redundant primary triangle preserves all OD under any one backbone outage, but its worst all-edge reachable-demand fraction is only 0.2635658915 because branches fail. Primary tree worst fraction is 0.1937984496. Neither is globally single-edge robust. One directed demand is increased 50% as GENERIC_SENSITIVITY_SCENARIO, using the existing named-scenario runner; no random failure model or probability claim.

## 21. Solver / Algorithm Status

Oracle: OPTIMAL_WITHIN_ENUMERATED_SYNTHETIC_STATIC_MODEL; exhaustive eight-subset proof with feasible shortest-route lower bounds. Original problem: NOT RUN / no optimum claim. No heuristic gap, large MILP scale, scheduling search or new framework is invented. Actual n,m,K, variables and constraints remain UNKNOWN; oracle counts are explicitly recorded in `model.md`.

## 22. Real Results

These are executed computations, all explicitly synthetic except the source-derived growth multipliers:

| Oracle design | Physical tunnels | Transport yuan/day | Depreciation yuan/day | Total yuan/day |
|---|---:|---:|---:|---:|
| Baseline | 7 | 9395.273712 | 117305.900894 | 126701.174606 |
| Primary | 7 | 7687.048579 | 114063.856583 | 121750.905162 |
| Redundant backbone | 8 | 6595.273712 | 146940.568912 | 153535.842623 |

Primary reduction versus baseline: 4950.269444 yuan/day in the artificial static model. Given annual 5% growth, D(8)/D(0)=1.477455443789063 and D(30)/D(0)=4.321942375150668 under t=0 convention. No real node count, route, flow, congestion reduction, transfer ratio, saturation year or construction sequence is produced.

## 23. Skill Strengths

Source closure, provenance gates, assumption separation, baseline comparison, hard feasibility, conserved resources, units, solver status and bounded scenario claims were usable unchanged. Current network reference already names graph construction rules, edge meanings, reachability and edge-deletion stability.

## 24. Skill Weaknesses

No demonstrated generalizable missing rule in this incomplete instance. The run cannot assess original-scale siting, congested joint routing, actual operations or phased building. The detailed user audit prompt also assists behavior, so synthetic success cannot establish unaided Skill readiness across network problems.

## 25. First Meaningful Failure

`MISSING_REQUIRED_ATTACHMENTS` at input audit is the first limiting event. It prevents actual-data graph construction. No implementation failure or incompatible solver choice is mislabeled as a general Skill defect.

## 26. Failure Classification

Failure owner: INPUT_AVAILABILITY. Skill failure level: NONE. Result status: PARTIAL. Publishing a made-up actual network would be P0, but it did not occur. Routine URL-encoding and renderer-added-image classification issues were corrected before final freeze.

## 27. Generalizable Gap Candidate

TOP-1: NONE. G1 criteria 1 and 2 are not established: no demonstrated missing current Skill rule causing an actual 2017F result defect. In particular, ordinary feasibility/conservation/claim issues are already covered by optimization rules. No stochastic or network capability is added.

## 28. Remaining Uncertainty

Missing original attachments; OD period; nearest-primary metric; primary surface access/congestion; surface costs; eligibility geometry; station dispatch interpretation; timed clearing; annual length tolerance. The eight-year/30-year formulation is only conditional. Human review should precede any additional source scope or future run.

## 29. Historical Integrity

Frozen start HEAD: `dfcf471d8e32506e81c8b4a6ff8a44e2a57ac7d0`. Skill tree before/after: `2b29e8ffa7c15d33bf81e675e8f1dcb240c226a6`. 744 protected tracked/nonignored existing files match SHA256; no tracked historical diff. 2005D run-001/run-002/reference, 2020A, 2011B, 2022C, 2023E and 2024C remain unchanged.

305 development tests and 19 standalone harnesses pass, including requested routing, behavior, trajectory, problem facts, historical integrity and skill-only self-contained coverage. DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING and prior smoke archive/placeholder failures remain recorded. Existing `.tmp`, frozen test duplicates and unrelated historical untracked artifacts were not repaired or submitted.

## 30. Final Decision

**C. BLIND_RUN_PARTIAL**. SEVENTH_PROBLEM_BLIND_RUN_COMPLETE means this bounded evaluation and archive are complete, not that the missing-data original problem is solved. Machine-readable fields are in `completion.json`; the audit scope there defaults to the original instance, with separate synthetic checks. Commit only current benchmark artifacts, preserve original .doc, exclude extraction caches. Stop after authorized Git publication and verification. No post-hoc paper access, Skill patch or eighth problem.
