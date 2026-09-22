# Source ledger

This stage checks original-source availability. All timestamps and evidence levels are in [source-observations.json](source-observations.json). Remote metadata is not a downloaded original attachment.

| ID | Source | Classification | Verified claim | Limitation |
|---|---|---|---|---|
| O1 | [Official competition notice](https://cpipc.acge.org.cn/cw/contestNews/detail/4/2c9088a674924b7f01749981b29502e9) | `OFFICIAL_COMPETITION_PLATFORM_SOURCE` | Published 2020-09-17; names E as 能见度估计与预测 and supplies O2, share code 2020 and archive password 2020HDligong16520. HTTP 200 on continuation. | Does not prove package contents. |
| O2 | [Official full-package share](https://pan.baidu.com/s/1C_AGvMxrojaU-rCvl5w9Iw) | Official-platform-linked original package candidate | Correct share code opens a RAR listing; earlier page metadata declares 1,129,044,568 bytes. | No package downloaded, hashed, enumerated or extracted. |
| M1 | [Frozen airport-video link](../run-001/source-provenance/original/机场视频参见百度云网盘.md) → [Baidu video share](https://pan.baidu.com/s/15XKUMDUG-mlF3OZ9iRTrYg) | Verifiable original-problem mirror link; not independently authenticated as an O2 member | Code kxst opens Fog20200313000026.mp4. Earlier page metadata declares 1,042,173,258 bytes, duration 41,609 s and 1280×720. | No full media file, SHA256 or local decode verification; 90-second web preview and verification-code prompt. |
| M2 | [Frozen mirror manifest](../run-001/source-provenance/source-files.json) | Existing original-problem GitHub mirror | Recomputed all six listed files' SHA256, Git blob SHA1 and size; both ZIP archives pass read-only safety and CRC checks. | Equivalence to O2 is unverified. |
| U1 | [Shanghai University of Engineering Science notice](https://ge.sues.edu.cn/03/da/c19717a197594/page.htm) | University official republication of competition notice | HTML reachable; four administrative/template attachment links enumerated. | No independent problem archive found on this page; attachments not opened. |
| A1 | Internet Archive CDX lookup for O2 | Archived-original-source candidate | Attempt recorded; current TLS handshake failure; earlier tool also could not access the lookup. | Archive availability remains unverified. |
| X1 | Exact filename searches in the original task | Bounded discovery only | Domain-limited GitHub/Gitee/university/archive queries returned no candidate; generic aggregator snippets were excluded. | Search is not proof of global absence. |

No excellent paper, submitted paper, solution repository, reconstructed MOR label, or solution-derived attachment was used. Incidental generic video-extraction snippets are disclosed in the search log. Raw browser state, cookies, transient request data, HTML caches and preview artifacts stay in ignored `.tmp/` and are not evidence of recovered media.
