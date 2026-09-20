# Source Provenance And Extraction Verification

Authorized directory: https://github.com/zhanwen/MathModel/tree/master/国赛试题/2017年研究生数学建模竞赛试题

Original filename: `2017年中国研究生数学建模竞赛F题.doc`. Exact download URL is recorded in `source.json`. Retained unchanged as `source/2017F_地下物流系统网络.doc`.

Git blob SHA: `c2dd56c208cf3c7f80f2e52ff1f58ee0a758166f`.
SHA256: `7cd51bdf0c6a0392eef93fc84efaf16090262fe94e7bae97d385fee67be28719`.
Size: 2,579,456 bytes. Fresh network download matches the pre-existing source byte for byte. Git identity was recomputed as SHA1(`blob <length>\0` + file bytes), not merely copied from metadata.

The authorized directory listing contains C docx, E rar, F doc, B docx, A zip and a D directory. Only F content was fetched. No F attachment archive is listed. Other problem contents and all excellent-solution paths were not opened. No answer search occurred. Initial TLS failures affected urllib, curl, git and the in-app browser; the stale local proxy was unavailable. Normal verified HTTPS subsequently worked. No certificate validation was disabled, network settings changed or alternate solution source used.

## Legacy Verification

1. Parse the OLE WordDocument and selected 1Table stream, respecting the CLX piece table. All 3 pieces contain UTF-16LE; 4,509 source characters reconstructed. Text SHA256 matches the earlier extraction `b50d172e8d6147d79437b92e8c01b28f7b5a02039685ea5d3e66df6bda7ff6dc`.
2. Independently load the original .doc with Aspose.Words 26.9.0. Compare all 57 nonempty visible source paragraphs to the engine text; all match. Full-stream strings are intentionally not identical: evaluation boilerplate, header/footer pagination and floating-text-box order differ. No mismatch is silently described as equality.
3. Render six pages and inspect every page, plus the original evolution image. Page 1 background; page 2 figures 1,2 and the two figure-3 images; page 3 hierarchy/vehicle parameters; page 4 Q1 and beginning Q2; page 5 Q2/Q3/Q4; page 6 final Q4 note, figure 5 and attachment description. All numbered subquestions and printed constraints are legible. Native Word tables: 0. ObjectPool embedded data files: 0.
4. Inventory five source PNG payloads, all matched bytewise inside the original OLE Data stream, plus two original figure-5 text boxes. Aspose adds a sixth raster logo; it is renderer-generated and excluded from source evidence. Circled-number formula fields are numbering, not missing scientific equations. Transfer ratio is given verbally with phi and can be faithfully expressed as a quotient.

The field referring to a local INCLUDEPICTURE path is source metadata, not an instruction to access that path. Its cached figure is present. The source has no numbered figure 4; no missing figure is invented.

TEXT_AND_PARAMETER_EXTRACTION: PASS.
SOURCE_OBJECT_INVENTORY: PASS.
SCHEMATIC_NODE_IDS / LEGEND / COORDINATES / ENGINEERING_LENGTH: EXTRACTION_UNVERIFIED.
REQUIRED_REAL_DATA_ATTACHMENTS: MISSING_FROM_AUTHORIZED_SOURCE.

Figure 5 is a conceptual evolution example, with no recoverable authoritative node IDs, coordinates or calibration. Its pixels cannot define the actual graph. The spatial map, OD matrix, area/coordinate table and congestion coefficients referenced by the text are absent, not zero-valued. Exact attachment filenames and checksums are unknown.

Full text dumps, page PNGs, PDF and extracted image bytes remain local under `work/`; they are extraction caches and are not committed. The retained .doc plus extraction code and compact audit manifest support reproducibility. Renderer evaluation watermarks are not original content and are not delivered as a clean edition of the problem.

## External Knowledge Ledger

| source | claim | why_needed | confidence |
|---|---|---|---|
| SciPy 1.18.1 installed `scipy.sparse.csgraph.dijkstra.__doc__`; API reference https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.dijkstra.html | Nonnegative path weights; directed flag matters; absent paths yield infinity and predecessor sentinel | Select valid route algorithm and reject disconnected routes | HIGH; installed documentation read and manual oracle passed; linked web page not separately fetched |
| SciPy installed `connected_components.__doc__` | Weak/strong directed connectivity differ | Separate physical connectivity from operating reachability | HIGH; documentation read and directed oracle checked |
| https://pypi.org/project/olefile/ ; installed 0.47 | OLE streams can be enumerated and read | Check old .doc compound container and embedded-data inventory | HIGH for enumerated streams; binary/text relationships additionally validated |
| https://pypi.org/project/aspose-words/ ; installed 26.9.0 | Independent legacy Word reading/rendering and shape extraction | Validate piece-table text and visual mapping | HIGH for matching paragraphs/source image bytes; limited for engineering semantics; evaluation additions explicitly excluded |
| https://pypi.org/project/PyMuPDF/ ; installed 1.28.2 | PDF rasterization for page inspection | Inspect all six rendered pages | HIGH for displayed rendering; not proof of source GIS correctness |
| `model.md`, shortest-route lower-bound argument and exhaustive 8-subset calculation | If independently shortest routes satisfy all static capacities, their unconstrained minimum is attained in that fixed design | Justify oracle decomposition, not a general network-design shortcut | HIGH within the explicitly fixed synthetic static model |

All package downloads used the public PyPI registry. No 2017F-specific external solution, paper, code, summary or domain parameter was accessed. General source statements quoted by the problem's background are not independently verified research facts in this benchmark.
