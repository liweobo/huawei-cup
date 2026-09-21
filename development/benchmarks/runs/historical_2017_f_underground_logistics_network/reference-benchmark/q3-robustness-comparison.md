# Q3 Operations, Failure And Surge

| Reference | Operational evaluation | Failure object and evidence | Surge and uncertainty | Audit judgment |
|---|---|---|---|---|
| F10256001 pp26-33 |Risk/satisfaction/cost metrics; SA distance/network improvement |Network-risk reasoning, not an exhaustive physical-tunnel paired-arc removal ledger |Risk coefficients/preferences not calibrated failure probabilities |No timed or capacity-restored failure certificate |
| F10294003 pp27-30 |Load utilization and location/distance refinement |No auditable tunnel-failure flow replay located |No same-protocol directional surge experiment located |STATIC_ONLY; utilization does not prove delivery |
| F10486024 pp23-25 |Relay-node alternative and detour analysis |Recognizes a remaining connected route can overload after interruption |Capacity limitation discussed, not a complete surge/run ledger |Useful qualitative strength; no validated restored multicommodity flow |
| F10703002 pp25-29 |Distance/time expressions and centrality-based load propagation |Selected secondary/node failure; Dijkstra reroute; degree/betweenness capacity proxy |Surge dismissed by asserted reserve, not specified magnitude |Capacity has no physical t/day calibration |
| F10710008 pp14-19,31 |Availability/accessibility/residual-capacity metrics |Surface fallback or promotion; route-probability formulas |No calibrated failure model; independence not justified |Reported probabilities>1 invalidate probability claim, not merely weak uncertainty |
| F90005027 pp35-42 |Selected paths, deterioration factor and backup links |Before/after route/flow tables for selected deletion; adds fifth primary |Scenario-specific improvement, not matched directional surge protocol |Some concrete rerouting evidence; no exhaustive capacity/restoration certificate |
| FK0263 pp33-38 |Cost search, reserve redesign and cycle additions |Five backup links; qualitative chain/ring interruption comparison |20% reserve chosen by authors: SCENARIO_ASSUMED |Alternate route existence not proof that all displaced flow fits |
| run-002 |Real-network timed queue replay with0/12min handling |1120 physical-tunnel removals, both arcs removed;118 disconnect service |Park1 outgoing+10%/+25% assumed; retained-route static checks |Reachability audited; restored-capacity and timed failure recovery unproved |

## Metric Interpretation

Connectivity, reachable OD fraction, capacity-feasible delivered flow and
delivered-by18h flow are different outcomes. Run-002's worst reachable routed
demand fraction0.988972493976 is not a resilience guarantee. Its nominal
connectivity check and1120 removals are broader systematic topological evidence
than the selected reference scenarios, but cannot certify failure recovery.

F10703002's degree/betweenness formula (p26) may define an abstract sensitivity
model; it is not an engineering capacity without calibration. F10710008's
residual-capacity fraction is not a reliability probability; values above1
(p31) and shared-path dependence defeat the interpretation. F90005027's
selected distance gain is not a whole-network time or cost benefit under the
frozen OD. Centrality or a cycle drawing alone does not justify a build decision.

No paper is accused of leaving the reverse arc of a failed physical tunnel
alive without evidence. Their physical-to-directed-failure mapping is generally
not explicit enough to audit at run-002's paired-arc level. This is a lack of
evidence, not a verified implementation defect in all seven papers.

## Existing Contract Versus New Capability

`simulation-network.md:17` already asks for reachability, constraints and
edge-removal stability. The optimization feasibility and evidence rules require
that any stronger claim be supported. Run-002 explicitly stops short of
capacity-restored robustness, so the post-hoc set does not expose a false claim
caused by a missing robustness rule. A better future solution should include
capacity-feasible rerouting and timed recovery if those outcomes are claimed;
this benchmark does not execute either.
