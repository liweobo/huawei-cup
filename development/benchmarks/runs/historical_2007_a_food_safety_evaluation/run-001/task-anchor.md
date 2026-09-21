# Task Anchor

## Goal

Complete a strict blind, reproducible evaluation of the 2007A food-safety evaluation problem using the frozen Skill, including source extraction, a genuinely run baseline and primary model, stability checks, reviewer audit, and one permitted final decision.

## Boundaries

- Do not modify `skill/`.
- Do not access 2007A excellent papers, solutions, code, abstracts, blogs, or problem-specific retrospectives.
- Do not modify any frozen historical run, including all 2017F artifacts.
- Do not silently invent source facts, indicators, weights, thresholds, experts, probability semantics, or external data.
- Do not start a ninth historical problem or perform post-hoc reference comparison.

## Inputs

- User-designated 2007 problem directory and exact 2007A legacy DOC blob `42ab94a3cd6fd90ed59bc13aaa2c0678c4304d44`.
- Frozen repository `HEAD=bd28c3fe87b4f1fb8cc45217f5c79572d7989a84`.
- Frozen `skill/` tree `2b29e8ffa7c15d33bf81e675e8f1dcb240c226a6`.

## Done When

The source is hash-verified and extraction-audited; all requested artifacts exist; baseline/model/sensitivity/synthetic tests are actually run under a structured record; required repository tests and integrity checks are recorded; only run-001 artifacts are committed and pushed; remote SHA equals the local commit.

## Risks

- Legacy DOC parsing may lose equations, table structure, or images unless independently checked.
- The statement may ask for theory rather than provide an alternatives-by-indicators dataset, limiting empirical ranking claims.
- A compensatory composite score can conceal non-negotiable food-safety failures.
- Relative scores can be misread as absolute safety probabilities.
