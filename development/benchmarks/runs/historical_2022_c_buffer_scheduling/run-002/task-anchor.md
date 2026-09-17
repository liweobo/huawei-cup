# Task Anchor

- **Goal**: Execute a strict third historical blind run on the 2022 C
  painting-to-assembly PBS resequencing problem using the frozen current
  Skill. Produce a source-provenanced, data-audited, explicit mathematical
  model, feasible baseline and real solver results for every tractable
  subproblem, with independent hard-constraint and output audits.
- **Benchmark ID**: `historical_2022_c_buffer_scheduling`
- **Run ID**: `historical_2022_c_buffer_scheduling/run-002`
- **Boundaries**:
  - Do not modify `skill/`.
  - Do not access excellent-solution papers, answers, solution writeups, or
    third-party 2022 C code.
  - Preserve all frozen historical runs and the 2023 E reference benchmark.
  - Treat `run-001` as a prior acquisition attempt; do not overwrite it.
  - Use only the original statement, its attachments, the frozen Skill,
    general solver/library documentation, and general mathematical knowledge.
- **Inputs**:
  - `run-001/raw/` original DOCX and four XLSX attachments
  - `run-001/extracted/problem.txt`
  - frozen `skill/` at repository HEAD
- **Done When**:
  - source URLs and SHA256 values are verified against the retained raw files;
  - `problem-facts.md` covers all rules, timings, objectives and subproblems;
  - all four workbooks are audited against the statement;
  - the optimization models have explicit parameters, variables, objectives,
    constraints, domains and sources;
  - feasible baselines and at least one real solution per tractable subproblem
    are produced;
  - the required `result11`, `result12`, `result21` and `result22` workbooks
    exist in the prescribed code format;
  - every final solution has an independent zero-hard-violation feasibility
    audit;
  - solver provenance, completion status and solution-quality limits are clear;
  - repository regression tests pass, `skill/` is unchanged, and the benchmark
    artifacts are committed and pushed if all checks pass.
- **Risks**:
  - The statement's operational interpretation may be under-specified.
  - A second-by-second discrete-event schedule for up to 450 vehicles is large.
  - The rule "when a downstream bay becomes empty, movement must begin
    immediately" couples queue movement and scheduler actions.
  - Objective 2's block rule has edge-case ambiguity.
  - Optimality is unlikely to be provable at full scale; results must be
    labelled as feasible baselines or best-found heuristic solutions.
