# Reference Source Ledger

## Scope And Reliability

Reference set: https://github.com/zhanwen/MathModel/tree/master/国赛论文/2017年优秀论文/F

The directory was enumerated, not sampled. Its seven PDFs were downloaded from
commit `cd5be91735ebf11d5ee52eb170e86a6d07131977`. Exact download URLs, timestamps,
sizes, Git blob IDs and SHA256 values are in [reference-manifest.json](reference-manifest.json).
Each local PDF matches both the pinned Git blob and SHA256. This establishes
reference-set identity, not correctness, official award rank or reproducibility.

Common fields applying to **each** entry below:

- `full_text_available: YES`; all pages, including appendices, read as native text.
- `text_extraction_quality: GOOD_NATIVE_TEXT_WITH_FORMULA_LAYOUT_CAVEATS`.
- `visual_verification: SELECTED_IDENTITY_FORMULA_TABLE_AND_FIGURE_PAGES`;
  final page-level record: [review-audit.json](review-audit.json).
- `award_level: UNKNOWN`; `award_verified: false`. No official award list was
  authenticated. No rank is inferred from the directory, institution or team ID.
- `Q1_covered: YES`, `Q2_covered: YES`, `Q3_covered: YES`, `Q4_covered: YES`.
  Covered means discussed, not solved or validated.
- `confidence`: HIGH for identity and quoted methods/results; MEDIUM for
  methodological interpretation; LOW/UNVERIFIED for unreplicated feasibility
  and optimum claims. These are references, never ground truth.

Page citations throughout this benchmark are **one-based PDF pages**, including
cover sheets, not the paper's printed page number. Review means full section and
appendix review plus targeted visual checks, not reproduction of every cell or
execution of the authors' programs. PDFs, native extraction and renders remain
in ignored `work/`; none is part of the commit.

## F10256001

- `filename`: F10256001.pdf; `page_count`: 68.
- `title`: 地下物流系统的构建研究.
- `authors`: 李阮、牛玺童、董娜; `institution`: 上海电力学院 (PDF p1).
- `url`: https://raw.githubusercontent.com/zhanwen/MathModel/cd5be91735ebf11d5ee52eb170e86a6d07131977/国赛论文/2017年优秀论文/F/F10256001.pdf
- `sha256`: `2f92fcfd13be4035a19c2c8b0dc723366fc54fc58672493553c12ef96690772b`.
- `facility_model`: modified ISODATA, distance/freight features, DEA comparison.
- `network_model`: hierarchical/bilevel congestion and cost design.
- `routing_model`: flow/distance allocation, PSO/SA improvement.
- `operation_model`: STATIC_ONLY; daily inflow=outflow used for clearing (p20).
- `expansion_model`: eight annual drawings, DP-style prioritization and named
  later upgrades; annual operational feasibility admitted unverified (p44).
- `optimization_method`: clustering, DEA, PSO/SA, dynamic-programming exposition.
- `reported_results`: 8 primary+22 secondary; 91.71% map-area coverage;
  5,756,533,247 yuan annual cost claim (pp13-14,25). Not a comparable daily cost.

## F10294003

- `filename`: F10294003.pdf; `page_count`: 50.
- `title`: 构建地下物流系统网络.
- `authors`: 王旭、尹紫依、丁毓蓝; `institution`: 河海大学 (p1).
- `url`: https://raw.githubusercontent.com/zhanwen/MathModel/cd5be91735ebf11d5ee52eb170e86a6d07131977/国赛论文/2017年优秀论文/F/F10294003.pdf
- `sha256`: `9ae63510cf1979885d9aa8464c664c26d2cdd3c579480ac458081d93c515beb6`.
- `facility_model`: moving coverage circles/centroids, nearest-neighbor merging,
  K-means hierarchy, congestion relief subset.
- `network_model`: geometric main/subnetwork construction with track selection.
- `routing_model`: adjusted/aggregated OD, fixed-network transport allocation.
- `operation_model`: STATIC_ONLY; nominal 90 trains/day, no network timetable.
- `expansion_model`: additional primaries, larger vehicles/longer operation;
  three-year primary, two-year park, three-year feeder stages (pp31-32).
- `optimization_method`: clustering and sequential approximate optimization;
  p34 explicitly qualifies optimality.
- `reported_results`: 4 primary+25 secondary; 597.04 yi-yuan capital,
  2,783,300 yuan/day total (pp16,25-26), using a 360-day conversion.

## F10486024

- `filename`: F10486024.pdf; `page_count`: 49.
- `title`: 构建地下物流系统网络.
- `authors`: 张黎明、徐业琰、杨铮; `institution`: 武汉大学 (p1).
- `url`: https://raw.githubusercontent.com/zhanwen/MathModel/cd5be91735ebf11d5ee52eb170e86a6d07131977/国赛论文/2017年优秀论文/F/F10486024.pdf
- `sha256`: `dce94f07503feba9b32e751eb7ae686dee7ef1cb1a5a6944f869ea43b883e6e3`.
- `facility_model`: 110 centre candidates, capacitated set cover followed by
  simplified CFLP selection of four primaries from 28 sites.
- `network_model`: fixed primary ring plus local spanning-tree construction.
- `routing_model`: clockwise/counterclockwise flow and track-type MIP on ring.
- `operation_model`: STATIC_ONLY; maximum directional daily flow constraint.
- `expansion_model`: relay/extra nodes, AHP/entropy/TOPSIS annual priority maps.
- `optimization_method`: LINGO integer models, MST, multicriteria ranking;
  no unrestricted network optimum certificate.
- `reported_results`: 28 lower-level sites, four promoted/selected primary
  locations; paper continues to list 28 secondary-layer rows (pp12-17).
  `4+24` is only a deduplicated-site interpretation, not an unqualified reported
  construction count. Ring transport 108,210.3 yuan and park-channel cost
  7,261,591.85 yuan are components (pp17,19), not a verified common total.

## F10703002

- `filename`: F10703002.pdf; `page_count`: 36.
- `title`: 构建分层优化的城市地下物流系统网络.
- `authors`: 杜琳、赵莎、毕成功; `institution`: 西安建筑科技大学 (p1).
- `url`: https://raw.githubusercontent.com/zhanwen/MathModel/cd5be91735ebf11d5ee52eb170e86a6d07131977/国赛论文/2017年优秀论文/F/F10703002.pdf
- `sha256`: `9b934cde189d873db7925db2992ce0db2f6f935b88a2808681cf4f50974a956b`.
- `facility_model`: five geographical partitions, AHP station importance,
  region-centre sites and manual service groups.
- `network_model`: star/grid hierarchical geometry with GA route encoding.
- `routing_model`: Dijkstra after selected failure, capacity proxies from
  degree/betweenness, symbolic travel/wait objective.
- `operation_model`: PARTIAL_OPERATION_MODEL; time/vehicle fragments pp35-36
  have no demonstrated correspondence to a full network timetable.
- `expansion_model`: greedy growth and ACO discussion, extra stations;
  no auditable eight-year commissioning sequence.
- `optimization_method`: AHP, GA, Dijkstra, greedy/ACO.
- `reported_results`: 5+27 in abstract versus 5+24 in body;
  `CONFLICTING_COUNTS`; 182 yi-yuan cost with insufficient time-basis clarity.

## F10710008

- `filename`: F10710008.pdf; `page_count`: 34.
- `title`: 构建地下物流系统网络.
- `authors`: 杨菲、付耀、谢宁猛; `institution`: 长安大学 (p1).
- `url`: https://raw.githubusercontent.com/zhanwen/MathModel/cd5be91735ebf11d5ee52eb170e86a6d07131977/国赛论文/2017年优秀论文/F/F10710008.pdf
- `sha256`: `233a111d85170dee9a658bed985f6747726a8ffa7a0b4c940779ca7460dea925`.
- `facility_model`: continuous freight-weighted primary centres, greedy
  secondary centre coverage followed by recentering.
- `network_model`: four park gateways, complete primary core, star feeders.
- `routing_model`: aggregate OD, predetermined connections, static path metrics.
- `operation_model`: STATIC_ONLY; utilization-derived availability indices.
- `expansion_model`: fuzzy-DP choice of three ten-year phases, located candidate
  stations; not an eight-year annual commissioning proof.
- `optimization_method`: gravity-centre heuristic, greedy cover, fuzzy DP.
- `reported_results`: 4+23; 407 wan-yuan/day claimed;
  15%/35% availability/accessibility improvements (pp13-19), not clearance gains.

## F90005027

- `filename`: F90005027.pdf; `page_count`: 54.
- `title`: 关于南京仙林地区ULS的建设方案探析.
- `authors`: 曲彤洲、尹安琪、邓元豪; `institution`: 战略支援部队信息工程大学 (p1).
- `url`: https://raw.githubusercontent.com/zhanwen/MathModel/cd5be91735ebf11d5ee52eb170e86a6d07131977/国赛论文/2017年优秀论文/F/F90005027.pdf
- `sha256`: `80aebf0e1709e99056cd0da192cec068a49a437cc42f4f2efe5e52daa3d275a7`.
- `facility_model`: geometric covering circles, area surrogate, nearest-park
  primary selection and capacity-constrained hierarchy.
- `network_model`: enumerate adjacency in fixed local groups, prescribed core.
- `routing_model`: BFS path enumeration and inverse-length splitting,
  candidate node-flow rejection; not jointly optimized arbitrary routing.
- `operation_model`: STATIC_ONLY; balance and nominal dispatch inequalities.
- `expansion_model`: five primary groups after Q3; 30-year OD and extra links,
  eight-year node-before-link priority lists.
- `optimization_method`: restricted exhaustive adjacency search, geometric
  heuristics, deterministic route allocation and priority ranking.
- `reported_results`: Q1 4+24; selected route distance improvement about25%;
  saturation claimed year18, but Table7.1 has F4/S16 at17 (p44).
  Cost evidence retained as component/formula comparison, not normalized total.

## FK0263

- `filename`: FK0263.pdf; `page_count`: 63.
- `title`: 构建地下物流系统网络.
- `authors`: 赵笑阳、龚欢、张兴艺; `institution`: 清华大学 (p1).
- `url`: https://raw.githubusercontent.com/zhanwen/MathModel/cd5be91735ebf11d5ee52eb170e86a6d07131977/国赛论文/2017年优秀论文/F/FK0263.pdf
- `sha256`: `8264250eddab48e6cb12d92adb00c6405bb2436d4d30975b5cc20ed3385e790f`.
- `facility_model`: centre-only fractional-assignment capacitated set cover;
  primary choice in 3^4 nearest-site combinations, expanded to5^4 for Q3.
- `network_model`: local MSTs; primary chain compared by capital+flow cost.
- `routing_model`: balanced underground park exchange, approximate aggregate
  directed core flows, tree/chain routes.
- `operation_model`: PARTIAL_OPERATION_MODEL; single-trip end-of-day correction
  gives89/90 departures (p22), but no transfer/queue network replay.
- `expansion_model`: 55 sites including a fifth relay, assumed doubled station
  ground limits; cycle drawings and seven-nodes/year rule (pp39-41).
- `optimization_method`: Matlab/LINGO set cover, Prim, bounded enumeration;
  Q4 names Fleury, without a demonstrated shortest-cycle optimization proof.
- `reported_results`: Q1 4+23, Q2 30 tunnels and248.13 wan-yuan/day;
  Q3 228.6081 wan-yuan/day, separate20% reserve scenario211.48 (pp32-37).

## Reading Boundary

The references were first accessed only after the immutable current solution
summary was written and hashed. No paper was used to supply source data, revise
run-002 or execute new optimization. General arithmetic and existing Skill
contracts are used to review claims, not to repair reference solutions.
