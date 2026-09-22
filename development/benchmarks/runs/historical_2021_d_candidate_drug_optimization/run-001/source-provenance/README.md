# Source Provenance

Only the five allowlisted immutable blobs were acquired. Direct GitHub TLS was unavailable, so the canonical raw URLs were transported through `gh-proxy.com`; the downloaded bytes were accepted only when their computed Git blob IDs exactly matched the supplied IDs. No repository clone, directory crawl, excellent-paper path, solution repository, solution code, blog, or public prediction file was accessed.

| File | Git blob | SHA256 | Bytes | Status |
| --- | --- | --- | --- | --- |
| 抗胰腺癌候选药物的优化建模.docx | b970fb60d85c0dd650d1152463cabbabf3cfe619 | 0659b4322a79a24e1a9c6df2010f38112959c808b7fd37bd5511fff5179a298e | 25749 | PASS |
| ERα_activity.xlsx | a8cbbe3620d7794d475cf85b2351f6dba2a931e3 | 16141c97ee795c0c2706df180ebabf28182286f6ebdb0ef2ad0e30b8193e6956 | 93695 | PASS |
| ADMET.xlsx | 08cee79e5e3beffe574e327b877c6028add92dc6 | 269339467b982e295ae3e93a62ae689db1c5595cae60378aada4450ed1a4dcd4 | 87227 | PASS |
| Molecular_Descriptor.xlsx | 21ee480d930e3befc65e55bdb283a01294a48bde | 714e26121180052c50b82cb99ef16185b0e111b23bcd54f464a0cb6f5ea2585d | 8804984 | PASS |
| 分子描述符含义解释.xlsx | 29e813b8da02985a8043e1cee03120e65378cbd8 | 9617582cc34f44d064a74edfdfb0e9482c7b85e4e9acdea976a29f900b397305 | 49477 | PASS |

All workbook and document reads were local after acquisition. `source-manifest.json` retains canonical and transport URLs.
