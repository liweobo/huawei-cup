# Source Ledger

Decision: `ORIGINAL_SOURCE_RECOVERED`. Acceptance is based on a trusted institutional mirror, not a claim of organizer-hosted or cryptographically authenticated official bytes.

## Primary Candidate C01

| Field | Observed value |
|---|---|
| source_url | https://lxy.usst.edu.cn/_upload/article/files/e2/01/9e3482374298a63f4622c0c1e50f/bca064b7-2489-4dba-88b9-f2d5fcdbd0d1.rar |
| host | lxy.usst.edu.cn |
| source_type | INSTITUTIONAL_ORIGINAL_PROBLEM_MIRROR |
| provenance_class | MIRRORED_ORIGINAL_CANDIDATE |
| filename | F.rar |
| download_date | 2026-09-20T12:16:11.131219+00:00 |
| claimed_origin | University of Shanghai for Science and Technology, College of Science, page titled `2017年赛题`, dated 2017-09-16 |
| sha256 | 8f8dc68c9049b4c565009dd3af3f959b7ae00f9579c0936baa344794b259f022 |
| file_type | RAR 4 archive, HTTP application/x-rar-compressed |
| file_size | 2,897,538 bytes |
| why_considered_original | University-hosted A-F problem-package listing; original-problem member names; exact known F.doc blob match; workbook and map cover the original attachment description |
| confidence | HIGH for trusted institutional original-file mirror; organizer origin not independently authenticated |
| disposition | ACCEPTED_FOR_FUTURE_SOURCE_COMPLETE_BLIND_RUN |

Discovery chain: [institutional historical listing](https://lxy.usst.edu.cn/xsycxjs1/list36.psp) -> [2017年赛题](https://lxy.usst.edu.cn/2017/0916/c6729a38056/page.htm) -> `F.rar`.

The article displays publisher `姜珍珍`, publication date `2017-09-16`, and links `A.zip`, `B.rar`, `C.rar`, `D.rar`, `E.rar`, `F.rar`. Only F was downloaded. The server reports Last-Modified `2018-07-26T11:23:26Z`; this is not silently substituted for the page publication date or archive member dates. No dated web-archive snapshot or organizer signature was obtained.

## Package Members

All members inherit C01's source URL, host, source type, download date, claimed origin, provenance rationale and confidence. Each has those fields repeated explicitly in [attachment-manifest.json](attachment-manifest.json). Member extraction did not re-save the document, spreadsheet or image.

| ID | Member | Type | Bytes | SHA256 |
|---|---|---|---:|---|
| C01-ZIP | F/2017年中国研究生数学建模竞赛F题.zip | ZIP | 2603620 | 34beef8fad48cc340c437d6c110e4f5326946d130282a22953ddad0666ad352d |
| C01-DOC | ZIP: 2017年中国研究生数学建模竞赛F题.doc | OLE Word DOC | 2579456 | 7cd51bdf0c6a0392eef93fc84efaf16090262fe94e7bae97d385fee67be28719 |
| C01-XLS | ZIP: 现状OD数据及其他数据.xls | OLE Excel BIFF8 | 259072 | 15f306257b78632d74576bcc3ccda03e69c8affc098a92dba183ae8f94a207ab |
| C01-MAP | F/地图.jpg | JPEG | 404751 | 30ee09fb69ae9e79506280a8e32e108bda35b6ddc53f1892e52dc28c6cf23d96 |

C01-DOC Git blob: `c2dd56c208cf3c7f80f2e52ff1f58ee0a758166f`. It is an `IDENTICAL_COPY` of the frozen run-001 document, not merely similar extracted text.

## Comparator And Excluded Sources

The frozen original came from [zhanwen/MathModel original questions](https://github.com/zhanwen/MathModel/tree/master/国赛试题/2017年研究生数学建模竞赛试题). Its existing source-provenance record was read locally; no repository solution directory was visited. The `.doc` was compared locally, byte-for-byte. No second independent XLS or map copy was found or needed after recovery.

The [current organizer platform](https://cpipc.acge.org.cn/cw/hp/4) was checked as O01, but it did not supply the recovered archive. `official_source_found: NO` means no organizer-hosted original attachment package recovered; it does not mean no official competition website exists.

Solution-oriented search results and the platform's excellent-works link were excluded without opening their targets. See [search-log.md](search-log.md). No numerical source fact comes from a search snippet.

## Retention

Original F.rar, ZIP, DOC, XLS and JPG bytes remain locally under ignored `work/` paths listed in the manifest. This commit retains metadata and reports only, following this stage's explicit delivery scope and the repository's allowance for traceable source metadata. Browser pages, temporary extracted copies, inspection crops, helper scripts and installed reader dependencies are not committed. A future checkout must retrieve C01 from its exact URL, verify its frozen SHA256, and verify every member hash before use. A different download is not an accepted replacement without review.
