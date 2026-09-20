# Bounded Search Log

Date: 2026-09-20 (UTC timestamps below). Purpose: recover original attachments only. No 2017F solution, excellent paper, appendix, participant code or answer-derived data was opened or used.

## Search And Access Events

| Event | Time UTC | Scope / URL / query | Outcome |
|---|---|---|---|
| S01 | 12:12:36 | Bing RSS: `"2017" "研究生数学建模" "赛题" "附件" 官方` | Mostly irrelevant year results; not useful negative coverage |
| S02 | 12:12:36 | Google HTTP: `"2017" "研究生数学建模" "F题" "附件" site:edu.cn -论文 -题解` | HTTP result parser yielded no useful results; not evidence of absence |
| S03 | 12:12:36 | Bing RSS: `"2017" "研究生数学建模" "试题" site:cpipc.acge.org.cn` | Mostly irrelevant results; not useful negative coverage |
| Browser discovery | Before U01; exact time not retained | Google browser: `2017 研究生数学建模 F题 附件 site:edu.cn -论文 -题解` | Original-question institutional listing discovered; snippets not used as problem facts |
| S04 | 12:14:38 | Bing RSS: `研究生数学建模竞赛 2017 赛题 下载 官方` | Current organizer platform and other candidates found; only permitted source pages fetched |
| U01 | 12:14:39 | https://lxy.usst.edu.cn/xsycxjs1/list36.psp | Institutional history listing with `2017年赛题` link |
| O01 | 12:15:21 | https://cpipc.acge.org.cn/cw/hp/4 | Official current competition platform inspected; no original F attachment recovered here |
| U02 | 12:15:21 | https://lxy.usst.edu.cn/2017/0916/c6729a38056/page.htm | Dated university page listing original A-F packages |
| C01 | 12:16:11 | F.rar URL in source-ledger | Downloaded successfully, HTTP 200, 2,897,538 bytes |
| Local verification | After download | RAR listing, original-only ZIP members, XLS readers, original map, frozen DOC bytes | Essential attachment coverage established; search stopped |

The priority was official and institutional sources, but calls were interleaved during discovery. This is not an exhaustive audit of all official historical sites. Recovery at the institutional tier made further crawling unnecessary.

## Coverage Boundaries

- Official sources: O01 current platform only. No organizer-hosted 2017 package was obtained; no claim that every official archive is missing it.
- Institutional mirrors: U01/U02 at the University of Shanghai for Science and Technology; C01 accepted after local verification.
- Repository mirrors: frozen run-001 provenance and DOC used as a local comparator. Its missing-attachment result and the user's other-mirror observation are historical context, not fresh search findings. No new GitHub/Gitee corpus crawl.
- Internet Archive and other download mirrors: NOT SEARCHED after successful recovery. No unsupported claim about their availability.
- No alternative city dataset, manual data re-entry or map-pixel coordinate reconstruction.

## Solution Sources Excluded

| URL / category | Reason | Action |
|---|---|---|
| https://www.kdocs.cn/l/cv3j79fp8mZY | Excellent-works collection linked from O01 | SOLUTION_SOURCE_EXCLUDED; target not opened |
| https://zhuanlan.zhihu.com/p/2063550564265472383 | Search-result title offered excellent papers | SOLUTION_SOURCE_EXCLUDED; target not opened |
| zhanwen/MathModel/国赛论文/2017年优秀论文/F | Explicit forbidden solution directory | Never visited |
| Lower-trust blog/download compilation result | Unnecessary after stronger institutional lead | Not opened or used |

Search-result titles were inspected for exclusion; any answer-oriented snippet is not evidence. No recovered value was corroborated through a paper. No theoretical/network algorithm reference was needed in this stage. `xlrd 2.0.2` and `python-calamine 0.6.1` were used solely as file readers, not as problem sources.

Stop rule met: exact known original DOC plus a coherent, complete named-attachment set obtained from a contemporaneously dated university problem-package page. Further search would not be necessary to make this recovery decision.
