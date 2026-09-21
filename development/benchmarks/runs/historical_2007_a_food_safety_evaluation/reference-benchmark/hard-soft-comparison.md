# Hard / Soft and Compensation Comparison

| reference | safety decision structure | hard-gate class | compensatory behavior | audit |
|---|---|---|---|---|
| `REF-01` | exposure/exceedance compared with a safety threshold; high PI prompts follow-up | `HARD_GATE_IMPLICIT` in design, but numerical gate is invalidly matched | ordinary indicators do not compensate for the stated threshold; error is semantic/unit, not compensation | gate concept present, implementation invalid |
| `REF-02` | warn when intake quantile exceeds national daily-intake standard | `HARD_GATE_EXPLICIT` | fuzzy matching combines candidate data sources before exposure calculation; it does not offset a safety exceedance | noncompensatory final decision |
| `REF-03` | safe when `Q_0.99999` is below authority standard | `HARD_GATE_EXPLICIT` | no compensatory score | noncompensatory, but no uncertainty margin |
| `REF-04` | compare age/body-weight-scoped q with converted tolerance | `HARD_GATE_EXPLICIT` | no compensatory score | noncompensatory point decision |
| `REF-05` | compare selected q with GB limit and declare safety | `HARD_GATE_IMPLICIT` in form, invalid in scope/unit | no compensatory score | gate concept present, comparator invalid |
| `REF-06` | same as `REF-02` | `HARD_GATE_EXPLICIT` | same | duplicate |

No reference is a fully compensatory MCDM system in which population, monitoring coverage, economic value, or ordinary quality indicators can offset a severe safety violation. This means the post-hoc evidence does **not** identify a new hard-versus-soft gap: the frozen Skill already says a hard constraint must not be reduced to a compensatory total score.

The missing piece is earlier: identify what mathematical output is being gated and whether the threshold actually applies. The minimal new contract should link to the existing hard-constraint rule rather than recreate it.

The frozen blind run is stronger than all references on uncertainty-aware gating: it uses `VIOLATION`, `UNCERTAIN`, and `COMPLIANT_UNDER_MODEL`, applies the gate before optional triage, and prevents coverage/population indicators from offsetting the gate.
