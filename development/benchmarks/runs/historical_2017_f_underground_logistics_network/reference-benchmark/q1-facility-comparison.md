# Q1 Facility, Coverage And Hierarchy

| Reference | Primary / secondary count | Location and candidate rule | Coverage / capacity / allocation | Interpretation |
|---|---|---|---|---|
| F10256001 pp9-16 |8 /22 |ISODATA centre-based clustering; DEA comparison |3km circles,91.71% map-area score; group allocation; later ground-capacity contradictions pp23-24 |Shared secondary groups; not same full-centre/flow protocol |
| F10294003 pp7-17 |4 /25 |Moving circle centres, nearest-neighbor and K-means |Centre service, congestion-relief allocations; one secondary3576.821117>3000 |Continuous/constructed coordinates, not centre-only |
| F10486024 pp9-17 |4 selected from28 sites; secondary-layer rows28 |Set cover on110 centres, simplified CFLP among28 |3000 lower-layer cap, density-dependent coverage; each service site one parent |4+24 only under promoted-site deduplication; bill of materials ambiguous |
| F10703002 pp7-17 |5 /27 abstract,5 /24 body |Five geographic groups; AHP on centre candidates |3km and rounded service lists; secondary834=3200 |CONFLICTING_COUNTS; capacity not consistently enforced |
| F10710008 pp7-11 |4 /23 |Continuous weighted primary centres; greedy secondary cover/recentering |Centre coverage, congestion-relief demand; duplicate region labels not reconciled |Shared hierarchy with fixed stars; assignment evidence incomplete |
| F90005027 pp8-17 |4 /24 |Geometric circles/centres; near-park primary selection |Area<=9pi surrogate plus geometry; capacity-constrained hierarchy |Secondary ground-load violations under its own eq18; not full certificate |
| FK0263 pp10-20 |4 /23 |110 centre-only set cover;3^4 nearby-primary choices |Fractional Yij,3000 bound, congestion relief; nearest-parent groups |Explicit restriction; not a continuous-location optimum |
| run-002 |118 /118 |Original centres plus150m overflow and250m paired-primary offsets |All110 centres covered; split secondary allocation<=3000; primary ground0 |Each secondary paired with its own primary; full offdiagonal underground scope |

Source permits centre coverage, radius<=3km and unrestricted inter-node
distance. It does **not** say that all stations must lie at region centres or
that3km is a tunnel-adjacency threshold. Centres as candidate sites, clustering
centres and continuous facilities are distinct modeling choices. No paper's
coverage drawing is accepted here as an independent machine proof of its full
assignment. Polygon coverage is not required by the centre-coverage allowance.

## Why Run-002 Has So Many Nodes

The predominant explanation is **B: MODEL_SCOPE_LIMIT**, with
**ALGORITHM_QUALITY_LIMIT** in its bounded improvement phase. Run-002 simultaneously
requires full offdiagonal underground movement, no primary ground exchange,
one primary per secondary and aggregate station dispatch. References generally
divert only congestion-relief freight, give primaries local service, share hubs
and interpret dispatch per line/track. These change both demand and feasible set.

Reference D also contributes: some published compact assignments violate their
own ground bounds or leave allocation audit incomplete. C applies to specific
cluster/cover choices. A, a demonstrably missing generic Skill principle, is
**not established**. Current modeling rules already require dependency-aware
staged/joint choice; optimization and structured-improvement references allow
assignment, activation, route and resource changes. Run-002 explicitly labeled
its restrictive construction and did not claim minimal node count.

All seven references allow multiple secondary stations under one primary.
This is strong evidence that broader hierarchy search is useful. It is not
evidence that the legal one-to-one construction was structurally invalid or
that the Skill prescribes it. No new facility search was run in this benchmark.

## Transfer And Routing Semantics

Membership limits cross-parent access: a secondary must reach other primaries
through its parent. Most papers implement separate local subnets and a primary
core; F10486024 uses a local star assumption in Q1 then trees in Q2; FK0263
uses trees; run-002 uses direct paired feeders. Flow following those designs
still needs explicit validation. F10256001's eight primaries but only four
park-based transfer ratios support keeping non-gateway ratios N/A rather than
inventing a normalization. Lower node count does not by itself settle that issue.

Verdict: run-002 solution quality is weak, but no G1 causal deficiency has been
demonstrated. None of the reported counts is a same-protocol optimality bound
on the118+118 construction.
