# Problem Interpretation Comparison

Status: **MIXED_REFERENCES**. Authority is frozen run-002's independently
extracted original DOC/XLS, not majority voting among papers. Relevant source
facts are F03-F08,F12,F14-F19,F23-F27 in sibling
`run-002-source-complete/problem-facts.md`.

## Shared Source Versus Modeled Objects

Original114 endpoints comprise four parks1-4 and110 regions791-900. They are
not114 pre-existing underground stations. All seven papers discuss parks,
primary stations, secondary stations and regions, but constructed stations,
regions served and underground service demand differ materially.

| Reference | Original endpoints and parks | Region/node interpretation | Direction and diagonal handling | Main qualification |
|---|---|---|---|---|
| F10256001 pp6-16,51-52 | Four gateways plus110 regions | Cluster centres,8 primary/22 secondary | Equal-return assumption; clustering symmetrizes; final directed preservation not audited | Area coverage91.71%; diagonal disposition not explicit |
| F10294003 pp7-19,49 | Four park groups | Moving service circles;4 primary selected from29 sites | Original matrix adjusted/rebalanced; appendix axis convention unreconciled | Low-congestion exemptions and redistributed residuals |
| F10486024 pp8-17 | Four one-to-one park gateways | 28 lower-level sites, four selected primary roles | Aggregate node OD; transfer denominator uses two-way park throughput |28 secondary rows coexist with four primary roles; diagonal not separately reconciled |
| F10703002 pp7-17,33 | Mentions115 points; processes110 regions; five primary groups | Centre nodes and rounded manual assignments | Says diagonal all0; exact directed aggregation not supplied | Contradicts original114 and nonzero diagonal; count disagreement |
| F10710008 pp6-12 | Four park groups | Continuous primary centres,23 secondary | Explicitly ignores intrazonal OD; symmetric regional table lacks reconciliation | Original asymmetric demand cannot be inferred preserved |
| F90005027 pp8-17 | Four parks and110 regions | Geometric service zones;4 primary/24 secondary | p9 rows=outgoing, columns=incoming without documented transpose | Source has column origin; area-average congestion changes target |
| FK0263 pp6-20,22,26-27 | Four parks,110 regions;107 with positive relief need |27 sites, fractional service assignments,4 primary roles | Balanced underground park service and common aggregation ratios | Selected underground subset is not original full OD; zero-need regions not zero-demand |
| Frozen run-002 |114 endpoints mapped separately to constructed236 stations |118 primary+118 secondary; split assignment, no primary ground service | Column-origin preserved; total163406.46t/day;3.44t diagonal surface-local |Full off-diagonal underground service is an explicit stronger modeling scope |

`AGGREGATION_PROVENANCE_WEAK` applies where the paper lacks a trace from every
original directed OD entry through allocation, underground/surface split,
station-local freight and final routes. It is an evidence label, not an assertion
that all freight was definitely lost. A symmetric table is not automatically
wrong if it represents a declared two-way total; it becomes unsuitable for a
directional capacity claim without disaggregation.

## Area, Congestion And Scope

| Reference | Area / congestion use | Source versus assumption |
|---|---|---|
| F10256001 pp9,14,17-20 | Image-area coverage; congestion and freight in clustering/design |0.5/0.5 preferences author-selected; normalized features in appendix |
| F10294003 pp7-16 | Congestion4 relief demand; density and moving coverage circles |500t/km2 selection rule is not a source constraint |
| F10486024 pp9-11 | Congestion4 target and density-dependent coverage method |2000 density boundary is author-selected; centre-only candidates are a restriction |
| F10703002 pp9-11 | Congestion, freight and distance AHP scores |0.6/0.3/0.1 preferences and ordering ambiguity; not source utility |
| F10710008 pp7-10 | Congestion relief subset and freight-weighted centres |Continuous siting and omission of low-congestion underground need are modeling choices |
| F90005027 pp10,13-15 | Area-sum circle surrogate and area-weighted congestion |Aggregated congestion<=4 does not establish every source region<=4 |
| FK0263 pp8-11 |Relief max(S-4S/k,0); area not central to centre cover |Zero relief is not zero original OD; ground growth5% in Q4 is assumed |
| run-002 | Retains original areas/index11.54 without clipping; centre cover; all offdiagonal flow |Surface/internal-zone engineering costs unresolved; stricter service scope documented |

There is no evidence that every paper clips congestion. Do not infer clipping
from a displayed0-10 band table. Common target4 follows the interpretation of
basic congestion relief; the chosen underground share is still a decision.

## Dependencies And Transfer Ratios

All seven link Q1 location/hierarchy to Q2 channels and flow, then propose Q3
improvements and Q4 growth. None supplies a uniformly audited end-to-end chain
at run-002's evidence granularity. Sequential solution is not inherently wrong;
fixing earlier decisions narrows any later optimum claim.

Source ratio is a **park's outgoing** freight relayed by its nearest primary to
other primaries, divided by that park's outgoing freight. It is not a generic
centrality or all-primary throughput fraction. F10256001 p15 reports four
nearest-park ratios despite eight primaries. F10486024 p14 uses park inbound+
outbound; FK0263 pp17-18 changes to underground-output denominators;
F90005027 p16 states the outgoing definition but p9 direction is unreconciled.
F10294003 uses adjusted demand; F10703002 has a fifth primary ratio under a
split-park mapping; F10710008's group flows are not a reconciled source ratio.

Consequently run-002's many N/A primary entries have two causes: an overlarge
primary hierarchy, and a source ratio tied to only park-associated gateways.
The former is a model-scope quality issue; the latter is genuine output-semantic
ambiguity. Inventing denominators for other primaries would not solve it.
