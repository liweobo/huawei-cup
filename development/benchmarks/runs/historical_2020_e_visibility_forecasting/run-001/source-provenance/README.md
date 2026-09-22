# Source provenance

Acquisition scope was restricted to the designated source directory: `https://github.com/zhanwen/MathModel/tree/master/国赛试题/2020年研究生数学建模竞赛试题/2020年E题`. Each retained byte stream was checked against the user-supplied Git blob SHA-1 and then hashed locally with SHA-256. The six originals are retained under `original/`; extracted archives, rendered pages, and browser/extraction caches are excluded from version control.

| File | Git blob SHA-1 | SHA-256 | Bytes |
|---|---|---|---:|
| `2020年E题--能见度估计与预测.doc` | `20bf8163a93285aec0ea6638219c905ae9490511` | `9687dd1be18e2caf52abd936e083635216edd264bd7bf7e9791ca1966f50b151` | 111104 |
| `能见度估计与预测.doc` | `df00f145a1b3347c1f4157183f097148cb9675f6` | `84885b986702a05f72af007faaf9c24969d46c7e37d34f2b0c3a1af862405fd9` | 139776 |
| `能见度估计与预测.pdf` | `a70a173ff0165902f1f51814cc7f7137eedf5005` | `e274df55b56ac1d648a72309e9a8a3161b0789f3b5302cc379f19b73e3514923` | 661546 |
| `机场AMOS观测.zip` | `ecb627cb3b3e99b25f4e04c31dfe0d911f478c4f` | `06e9983053a059db4f92c3d0257d3063332586ccde00bb3d098f4f582e720002` | 641088 |
| `高速公路视频截图.zip` | `80b3c261a5c0b0fcec6923111ad578f1f3500651` | `80fe0717d9389050ecae381b72d7a994eb7795ced907e30d0409e94b7104cbf8` | 12352504 |
| `机场视频参见百度云网盘.md` | `87804adeedc51c1abf53b7142655deb286c12c73` | `fddad5e72ddf21723c394a3d22f53828858dad7753c673b1594f1ae4f0607418` | 210 |

The acquisition URL for each byte stream was the Git blob endpoint `https://api.github.com/repos/zhanwen/MathModel/git/blobs/<blob-sha>`, corresponding to the designated source directory. `integrity-before.json` freezes the starting repository state.

## Extraction verification

- Both legacy DOC files were opened read-only through Microsoft Word, converted to PDF, and every rendered page was visually checked. This is not an unverified plain-text-only extraction.
- The supplied PDF was inspected with Poppler text extraction and page rendering; all five pages were visually checked. The equations are image objects, so their symbols were transcribed only after visual verification.
- No problem-document tables exist. The older DOC has 10 inline shapes; the corrected DOC has 13. The PDF contains seven visible image objects plus seven soft masks on page 4, corresponding to the rendered equation fragments.
- Verified equations include contrast `K`, atmospheric attenuation `F=F0 exp(-sigma z)`, and `MOR=log(F/F0)/(-sigma)=log(0.05)/(-sigma)`.

## Blindness disclosure

No excellent-solution PDF or excellent-solution directory was opened. During source-link troubleshooting, an unintended web search-result snippet from a 2020E-specific blog was displayed. It repeated problem-subquestion text and only the generic phrase that question 1 could use formula/fitting; no page, code, numerical result, model specification, or solution artifact was opened or used. This is recorded as `UNINTENDED_NON_SUBSTANTIVE_SEARCH_SNIPPET_EXPOSURE`, not hidden, and contributes to the conservative `PARTIAL` status.
