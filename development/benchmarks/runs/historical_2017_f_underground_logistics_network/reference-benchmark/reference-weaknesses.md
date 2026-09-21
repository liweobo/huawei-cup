# Reference Weaknesses

Status vocabulary: **CONFIRMED** is a visible contradiction to a printed
definition or source requirement; **UNVERIFIED** is missing evidence;
**ASSUMED** is a declared alternative scenario, not necessarily an error.
Page numbers are PDF pages. Reproduction of the papers is outside scope.

| Check | Evidence / paper | Finding and confidence |
|---|---|---|
| OD direction implicit/reversed |F90005027 p9;F10294003 appendix p49 |Row-origin stated/apparent versus source column-origin, without demonstrated transpose; HIGH/MEDIUM respectively |
| Symmetric demand replacing direction |F10256001 p6,51-52;FK0263 p22 |Assumed balanced/symmetric freight must not be called original-directed preservation; HIGH |
| Lost/ignored diagonal |F10703002 p7;F10710008 p6 |Zero-diagonal claim / explicit omission differs from source3.44t; HIGH |
| Hidden/restrictive candidate sites |F10486024 pp9-12;FK0263 p10 |Explicit centre restriction is not source necessity; restriction itself legal, lossless/global claim unproved |
| Arbitrary preference weights |F10256001 p9;F10703002 pp10-11;F10710008 pp20-23 |Preference sources weak; first paper's features **are normalized** in appendix; do not claim otherwise |
| Static balance presented as clearance |F10256001 p20 eq34;F90005027 p29 |UNVERIFIED timed completion; daily equality cannot imply every shipment arrives by18h |
| Incomplete timing |F10703002 pp35-36;FK0263 p22 |Credit partial timing, not a full-network schedule |
| Ground-capacity violations |F10256001 pp23-24;F10294003 p16;F10703002 p14;F90005027 pp14-16 |CONFIRMED displayed quantities exceed their stated ground bounds; see formula checks |
| Train/vehicle and dispatch ambiguity |F10294003 pp25-26;F10486024 p19 |10 multiplier in5t formula;8/hour vs5;10t interprimary table vs5t source/constraint |
| Physical tunnel double counting |All7 reviewed |NOT ESTABLISHED. Several use upper-triangle/unique links; unresolved notation is not proof of double counting |
| No complete flow conservation certificate |All7 |UNVERIFIED original-directed allocation/route report; some contain balance equations or selected flow tables |
| No independent complete objective reconstruction |All7 |UNVERIFIED; transparent components in FK0263 and others are useful but not full independent audit |
| Wrong arithmetic in displayed components |F10256001 p24 row894-898 |1708.511+3201.405=4909.916, printed4099.405; CONFIRMED |
| Capacity from centrality without unit calibration |F10703002 p26 |Degree/betweenness-derivedCij is not physical t/day without mapping; HIGH |
| Connectivity equated with robust service |FK0263 pp37-38, portions of other failure discussions |Alternative paths do not show displaced flow can fit; UNVERIFIED capacity recovery |
| Probability/availability misuse |F10710008 pp15,31 |Residual capacity called probability; values1.003/1.087/1.045/1.176>1; CONFIRMED inconsistency |
| Spatial averaging hides hotspots |F90005027 pp13-15 |Area-average congestion target differs from per-original-region target; HIGH |
| No full annual service feasibility |All7 Q4 |PHASED_NETWORK_FEASIBILITY_UNVERIFIED; credit maps, locations and node-first rule where present |
| Misaligned construction horizon |F10710008 pp20-28 |Three10year phases do not satisfy an8year annual construction plan |
| Changed expansion constraints |F10294003 pp31-32;F10486024 p35;FK0263 p39 |All10t/longer daily hours or doubled station limits are assumptions, not source-constrained certificates |
| Saturation inconsistency |F90005027 p44 |Narrative first18 while F4/S16 table17; CONFIRMED, not a max-year calculation |
| Heuristic labeled optimal |F10256001 pp22-23;F10703002 Q2; scoped uses elsewhere |Global proof unavailable. F10294003 p34 explicitly qualifies approximation and must receive credit |
| Inadequate uncertainty/sensitivity |Across7 |Scenario choices and omitted operational/engineering factors not jointly tested; do not infer no sensitivity at all |

## Do Not Overcorrect References

Symmetric **physical** tracks are required; symmetric **OD** is not. An
underground balanced subset with declared surface residual may be a legal
policy, although it cannot replace all original demand. Exceeding3000 in a
transit-inclusive secondary throughput table is not automatically a ground
violation. The F90005027 finding specifically relies on its Q1 eq18 defining
that quantity as ground diversion. Q2 transit-inclusive tables are not used
for that allegation.

Smaller node counts, trees, stars and restricted candidate sets are not themselves
mistakes. References are weaker only where claims exceed their explicit
assumptions, constraints, numerical consistency or evidence.
