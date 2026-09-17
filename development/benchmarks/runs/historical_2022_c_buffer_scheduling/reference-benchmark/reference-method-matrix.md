# Reference Method Matrix

The matrix records what the supplied PDFs actually state. `UNVERIFIED`
means the available text extraction did not provide enough evidence.
Algorithm names alone are not treated as evidence of a Skill gap.

| structural question | R-01 `C22103190082` | R-02 `C22103360057` | R-03 `C22103560098` | R-04 `C22105330245` | R-05 `C22105930028` | R-06 `C22106130232` | R-07 `C22106140003` |
|---|---|---|---|---|---|---|---|
| state/decision object | PBS position/state matrix; per-vehicle lane choice | lane choice + whether/how many times to return | per-second inbound/return position state matrices; target lane + return decision | sequence-time joint distribution; lane assignment | vehicle-lane matching; multi-objective sequence | OD-pair vehicle location transitions | state/time matrices and PBS programs |
| direct schedule or target sequence first | target/sequence optimization plus dynamic PBS simulation | target sequence and return decisions then construction | output sequence changes then state simulation | reordering and sequence-time assignment | sequence/matching then scheduling | position-transition schedule model | sequence plus simulation |
| feasible decoder | implicit PBS simulator, not a formally verified decoder | constructive greedy plus simulated-annealing neighborhood; feasibility checked during construction | state/time simulation evaluates sequence changes | stepwise/grouped resequencing with schedule evaluation | GA sequence then matching/route construction | schedule-generation position transitions | heuristic schedule-generation programs |
| six inbound lanes | lane selection in the simulation/GA chromosome | lane assignment decisions | lane position matrices | lane assignment and resequencing | lane matching rules | lane-specific OD transitions | lane state matrices |
| return lane | probabilistic return strategies and explicit return probability | explicit return/no-return decisions and returns in Q1/Q2 | target-lane/return decision; return count iteratively changes sequence | reports return count/usage and uses it in joint objective; Q2 can reduce to 0 | return lane used to remedy wrong lane assignment | return lane is part of OD transition model | RRF/LWT/MTT strategies include return-related movement |
| two transfer machines | simulated machine actions and timing | modeled ordering/timing constraints in MIP | time matrices for both machines | time/waiting/resequencing model | machine matching and movement model | transition model includes transfer zones | PBS machine procedures |
| explicit dynamic resource state | yes, MATLAB PBS dynamic simulation | partially: MIP + greedy construction | yes, position/time matrices | yes, sequence-time joint distribution | partially: matching/GA and Markov state | yes, OD-position state transitions | yes, simulation procedures |
| Q1 priority rules | included in simulation and strategy design | included in greedy/MIP constraints | included | included in the reported Q1 pipeline | included | included | included, though extraction is degraded |
| Q2 removal effect | returns become a more active rearrangement lever | greedy policy changes lane specialization and uses 9 returns | iterative sequence changes with fewer/other return usage | Q2 can drive return use to 0 and reduce completion time | Q2 uses Markov multi-objective ranking | Q2 re-runs the position/transition model with relaxed priority | Q2 reruns MTT/heuristic variants |
| objective calculation | directly computes O1-O4 and weighted total | directly computes weighted total and objective components | directly computes weighted total and objective components | directly reports objective components/weighted score | directly uses weighted objective | directly uses weighted objective | directly reports Q1/Q2 weighted scores |
| search | improved GA with heuristic initial population + chaotic crossover/mutation | greedy construction + simulated-annealing local improvement | dynamic-programming state model + iterated sequence change; grey-wolf variant | reverse solution + grouped/stepwise algorithms; SA versus GA | GA for Q1; Markov decision/multi-objective ranking for Q2 | improved GA over location transitions | heuristic variants including MTT/LWT/RRF and metaheuristic comparison |
| initial solution | several heuristic scheduling strategies; choose best initial population | greedy construction | generated/iterated sequence; state evaluation | grouped/stepwise construction | GA population and matching rules | GA population | heuristic initial schedule |
| neighborhood/action | mutation/crossover over route/lane genome; return probability changes | return/no-return and lane-choice adjustments; SA neighborhood | change output sequence via return-related iterative adjustments | grouping, resequencing, step changes | sequence/assignment changes and Markov action choice | genetic changes to location-transition route | policy/move changes across MTT/LWT/RRF |
| staged decomposition | heuristic initialization then GA; Q1 then Q2 | MIP model then greedy then SA; Q1 then Q2 | state model then iterated sequence improvement; Q1 then Q2 | reordering methods then SA/GA comparison; Q1 then Q2 | Q1 GA, Q2 Markov multi-objective ranking | problem/model then GA; Q1 then Q2 | PBS model then MTT/LWT/RRF variants |
| avoids invalid solutions | simulator checks constraints; no independent workbook audit stated | construction guardrails and feasible-space claim | state matrix constraints; not an independent audit | schedule evaluation; no independent workbook audit stated | constraint/matching rules; no independent audit stated | transition constraints; no independent audit stated | PBS procedures; extraction too degraded to verify |
| final validation | reported position matrix and score; no independent hash/constraint audit | reported scores and comparison to original sequence | reported scores/time/return counts | reported scores and SA/GA comparisons | reported scores/time/returns | reported scores/time | reported scores/time |
| reports concrete score | yes, Q1/Q2 totals and components | yes, Q1/Q2 totals and components | yes, Q1/Q2 totals/time/returns | yes, Q1/Q2 totals/time/returns | yes, Q1/Q2 totals/time/returns | yes, Q1/Q2 totals and time | yes, Q1/Q2 totals |

## Cross-Reference Notes

- The references overwhelmingly optimize a **sequence or assignment
  representation** and then use a simulator/decoder, rather than treating
  feasibility as a post-hoc check. This is a legitimate alternate
  representation, not a regression of the stateful-scheduling contract.
- Several references explicitly use **a constructive initial solution plus
  a neighborhood/improvement phase**: R-02 uses greedy + simulated
  annealing; R-04 uses grouped/stepwise resequencing and compares SA/GA;
  R-01 uses heuristic initialization + genetic changes; R-05 uses GA for Q1
  and Markov/ranking for Q2.
- Return-lane use is not universally beneficial: references report both
  active use and strategies that reduce it to zero. The common lesson is
  not "always use the return lane"; it is "model the return decision and
  its effect on sequence quality as a searchable action".
