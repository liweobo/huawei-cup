# Task Anchor — FOURTH HISTORICAL PROBLEM BLIND RUN

- Goal: use the frozen current Skill to model the original 2011B problem, execute real numerical work, and observe the first meaningful failure without repairing the Skill.
- Boundaries: no edits anywhere in `skill/`; no 2011B solution/paper/blog/code access; no development on 2022C; protect every pre-existing benchmark file, including untracked assets.
- Input: only the user-designated zhanwen/MathModel 2011 problem directory and original target DOC; general scientific sources only with claim-level provenance.
- Done when: source/facts freeze, quantity/assumption/model ledgers, baseline and mechanism calculations, numerical/physical validation, critical review, existing regressions, scoped commit/push/remote verification, then STOP.
- Output root: this run directory. Conversion/cache artifacts go in its ignored `.tmp/` directory. Final artifact manifest excludes caches.
- Benchmark isolation: source-blind in the development repository, not a falsely claimed platform clean room; historical content inspected only for hashes/regression.
- Routes: analyze_problem → audit_data → design_model → build_baseline → run_experiment → validate_model → reviewer.
- Risks: legacy equation/image extraction; unknown material/geometry values; underidentified phase/material parameters; model error versus numerical error; user-provided safeguards may compensate for gaps and must not be attributed to autonomous Skill capability.
