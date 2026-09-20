# 2017F Original Source Recovery

**Final decision: ORIGINAL_SOURCE_RECOVERED**

The missing original attachments were recovered from an original-problem-package page at the University of Shanghai for Science and Technology. The package contains the byte-identical known F.doc, an original XLS with all required tabular inputs, and the numbered region map. This is accepted as a trusted institutional mirror, not labeled organizer-official.

## 1. Frozen Blind Run

`run-001/` remains a permanently frozen SOURCE-INCOMPLETE BLIND RUN with decision `BLIND_RUN_PARTIAL`. Starting commit: `5a80876ca8289debfe810ad96e1217b3b4f42341`. Skill tree: `2b29e8ffa7c15d33bf81e675e8f1dcb240c226a6`. Run-001 tree: `fc2d5b6f7ba6da3dfe2826e72a60aadd89a12d73`. No new attachment is inserted there.

## 2. Missing Inputs

The frozen facts required the freight-region map/IDs, directed OD, centre coordinates, areas, congestion coefficients, four park locations/IDs and park-to-OD correspondence. All are now covered by the recovered XLS and JPG, read together with the original DOC. See verification.md for cell-level locators and limits.

## 3. Search Scope

Bounded official/institutional source discovery only. Four recorded HTTP search queries, a browser institutional query, one current organizer platform and two university pages were inspected. Search stopped after the university package passed completeness checks. No exhaustive-crawl claim; GitHub/Gitee and web archives were not additionally crawled after recovery.

## 4. Official Sources Checked

[Current organizer platform](https://cpipc.acge.org.cn/cw/hp/4) checked. Its excellent-works link was not followed. No organizer-hosted original attachment package was recovered, so `official_source_found: NO` under that precise definition.

## 5. Institutional Mirrors Checked

[USST 2017年赛题](https://lxy.usst.edu.cn/2017/0916/c6729a38056/page.htm), reached through the university historical listing, displays publication date 2017-09-16 and A-F problem package links. Only its F.rar was downloaded. `trusted_mirror_found: YES`.

## 6. Repository Mirrors Checked

The frozen run-001 DOC and its existing zhanwen/MathModel provenance record were used as local comparators. No new repository-wide search and no visit to any solution directory. Prior observations of missing attachments in repository mirrors are historical context, not repeated experiments.

## 7. Candidate Files

C01 F.rar: 2,897,538 bytes, SHA256 `8f8dc68c9049b4c565009dd3af3f959b7ae00f9579c0936baa344794b259f022`. It contains `F/2017年中国研究生数学建模竞赛F题.zip` and `F/地图.jpg`. The ZIP contains only the F.doc and `现状OD数据及其他数据.xls`. Source/member hashes, paths, dates and internal metadata are frozen in attachment-manifest.json.

## 8. Provenance Evaluation

Classification: `MIRRORED_ORIGINAL_CANDIDATE`, accepted with high confidence as an institutional mirror after verification. Supporting evidence: university domain and dated original-problem page, coherent member names/dates, exact DOC Git blob match, and complete attachment content corresponding to that DOC. Limitation: no organizer signature or archived 2017-byte proof. HTTP Last-Modified in 2018 and displayed publication in 2017 are distinguished, not concealed.

The recovered DOC Git blob is `c2dd56c208cf3c7f80f2e52ff1f58ee0a758166f`; SHA256 `7cd51bdf0c6a0392eef93fc84efaf16090262fe94e7bae97d385fee67be28719`. It is byte-identical to the frozen original.

## 9. Attachment Completeness

`essential_attachment_set: COMPLETE` for the source-level instance. The XLS has two sheets: a 114 x 114 directed full-day OD table and attributes for IDs 1-4 plus 791-900. All 114 coordinate pairs, 110 region areas and 110 congestion indices are present. The raster map supplies numbered region boundaries and four separate blue points.

OD uses tonnes and column-origin to row-destination, not the common opposite storage convention. The two independent XLS readers agree on all 14,145 compared cell positions. Park identity is a documented cross-reference inference from the four-park statement and matching blue labels/table keys, not an invented map legend. Unknown CRS/origin/projection and absent park area/index values remain explicit. Original diagonal OD and indices above 10 are preserved. No pixel-derived geometry is used.

## 10. Conflicting Copies

Institutional DOC versus frozen DOC: `IDENTICAL_COPY`. Only one original XLS/map candidate was obtained; independent cross-mirror equivalence is not claimed. No conflict observed in the inspected material. Independent parser agreement verifies extraction, not provenance across two sources.

## 11. Blind-Integrity Protection

No excellent papers, solutions, participant code, paper appendices or answer snippets used. No Skill modification, run-001 modification, modeling, solving or run-002 creation. Protected 2005D, 2020A, 2011B, 2022C, 2023E, 2024C and 2017F history are checked against the 893-file starting snapshot. Checks are confined to historical integrity, source hashes, metadata/index consistency and Git scope, not expensive model regression.

The run-001 synthetic audits remain code-validation evidence only. Their numerical results were not used as modeling hints. Skill conclusion stays `NETWORK_CAPABILITY_NOT_FULLY_TESTED_DUE_TO_SOURCE_INCOMPLETENESS` for the frozen blind run. Finding its missing source does not establish `NETWORK_MODELING_READY` or a generalizable network gap. Gap candidate remains `NONE`.

## 12. Final Decision

`ORIGINAL_SOURCE_RECOVERED`.

This commit delivers source-recovery metadata/reports only. Original bytes remain locally under ignored work/ with exact paths and hashes in the manifest; no raw archive, browser/extraction cache, helper dependencies or solution material is committed. This follows the explicit stage delivery scope and the repository's traceable-source-metadata option. Future retrieval must reproduce the frozen hashes. Historical before/after checks and the existing historical-artifact test are recorded separately; no existing environment issue is repaired.

## 13. Recommended Next Action

`run a new source-complete blind run without excellent papers`

Wait for human review first. Only a separately authorized future `run-002-source-complete` may use the recovered originals and the current unchanged Skill to independently complete Q1-Q4. It must not use run-001 synthetic results as answers. That directory has not been created. Source recovery stops here; no Skill update, post-hoc paper reading or eighth problem.
