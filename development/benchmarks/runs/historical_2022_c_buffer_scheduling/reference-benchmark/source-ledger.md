# Excellent-Solution Source Ledger

## Collection

- Repository: `https://github.com/zhanwen/MathModel`
- Directory:
  `国赛论文/2022年优秀论文/C`
- Collection status: `EXCELLENT_SOLUTION_REFERENCE_SET`
- Official award verification: not established from the supplied mirror.
  Unless separately verified, `award_level: UNKNOWN`, `award_verified: false`.

| reference_id | filename | title | authors | institution | url | full text | award | award verified | verification source | Q1 | Q2 | main modeling approach | search or solver | result available | confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R-01 | `C22103190082.pdf` | 汽车制造涂装-总装缓存调序区调度优化研究 | 薛亦晖、袁浩淼、丁乙 | 南京师范大学 | GitHub mirror path | true | UNKNOWN | false | not supplied | true | true | dynamic PBS simulation + 0-1 integer programming | heuristic initialization + improved GA with chaotic crossover/mutation | true | HIGH after text extraction |
| R-02 | `C22103360057.pdf` | 基于改进贪婪算法的 PBS 优化调度问题 | 陈盟昊、张琳翊、陈利超 | 杭州电子科技大学 | GitHub mirror path | true | UNKNOWN | false | not supplied | true | true | mixed-integer formulation of lane choice/return decisions | greedy constructive + simulated annealing improvement | true | HIGH |
| R-03 | `C22103560098.pdf` | 基于动态规划的 PBS 多目标优化调度问题研究 | not fully extracted | not fully extracted | GitHub mirror path | true | UNKNOWN | false | not supplied | true | true | time-position state matrices + multi-objective dynamic programming | iterated sequence changes + grey wolf optimization | true | HIGH for methods, medium for author metadata |
| R-04 | `C22105330245.pdf` | PBS 调度优化研究 | not fully extracted | not fully extracted | GitHub mirror path | true | UNKNOWN | false | not supplied | true | true | reverse solution + dynamic programming, sequence-time joint distribution | grouped resequencing, stepwise algorithm, SA and GA comparison | true | HIGH for methods, medium for author metadata |
| R-05 | `C22105930028.pdf` | 汽车制造涂装-总装缓存调序区调度优化问题 | not fully extracted | not fully extracted | GitHub mirror path | true | UNKNOWN | false | not supplied | true | true | vehicle-lane matching and multi-objective sequencing | genetic algorithm for Q1; Markov decision / multi-objective ranking for Q2 | true | HIGH for methods |
| R-06 | `C22106130232.pdf` | 涂装-总装缓存区调序调度优化问题 | 俞建民、赵松、冯聪 | 西南交通大学 | GitHub mirror path | true | UNKNOWN | false | not supplied | true | true | multi-objective location-transition model over OD pairs | improved genetic algorithm | true for Q1/Q2 aggregate scores | HIGH |
| R-07 | `C22106140003.pdf` | PBS 调度优化研究 | not reliably extracted | not reliably extracted | GitHub mirror path | degraded / partial | UNKNOWN | false | not supplied | true | true | simulation + heuristic metaheuristic variants | RRF/LWT/MTT heuristic policies and metaheuristic comparison | partial due extraction encoding | LOW-MEDIUM |

## Source Reliability Notes

- All seven PDFs were enumerated from the requested directory.
- All seven files were downloaded to a temporary directory and hashed; PDFs
  are intentionally not committed.
- Six files have usable extracted text. `C22106140003.pdf` has a damaged
  text layer and is marked low-confidence for fine-grained method claims.
- The mirror does not provide reliable award-level metadata. This report
  does not infer award levels from filenames or paper quality.
