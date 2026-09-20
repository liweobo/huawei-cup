# Source Recovery Verification

This verifies source availability and correspondence, not network feasibility or modeling capability. Machine-readable evidence: [input-inspection.json](input-inspection.json), [attachment-manifest.json](attachment-manifest.json), [provenance-evidence.json](provenance-evidence.json).

## Original Document

The institutional package DOC equals the frozen original byte-for-byte. SHA256 `7cd51bdf0c6a0392eef93fc84efaf16090262fe94e7bae97d385fee67be28719`; Git blob `c2dd56c208cf3c7f80f2e52ff1f58ee0a758166f`. The previously verified legacy-DOC extraction remains applicable to these identical bytes. Its attachment paragraph and four-park statement were read again, without running any run-001 script or modifying its artifacts.

The final attachment paragraph calls for the Xianlin freight-region division map, OD matrix, region areas and centre coordinates, and congestion coefficients. It states tonnes for OD and `横轴对纵轴的发货量`. All those attachment classes are now present. The invitation to collect other useful data is open-ended, not a reference to another missing named official file.

## Completeness And Correspondence

| Essential input | Original evidence | Result |
|---|---|---|
| Freight-region map | C01-MAP, original numbered boundaries and points | PRESENT |
| Region IDs | Map labels and XLS IDs 791-900 | PRESENT, 110 |
| Directed OD | 现状全天OD!B2:DK115 | PRESENT, 114 x 114 |
| Region centres | 各区域中心点及面积!D6:E115 | PRESENT, 110 X/Y pairs, metres |
| Areas | Same sheet B6:C115 | PRESENT, 110 km^2/m^2 pairs |
| Congestion | Same sheet F6:F115 | PRESENT, 110 indices |
| Four parks | Four-park DOC statement; blue map IDs 1-4; XLS D2:E5 | PRESENT by source cross-reference |
| Park/OD correspondence | IDs 1-4 in map, attribute rows 2-5, OD rows 2-5 and columns B-E | PRESENT |
| Other named required attachments | Original attachment description versus two recovered attachment files | No remaining missing named class |

The map does not print a semantic legend saying blue equals park. Interpreting the four separate blue points as the four parks is a high-confidence cross-reference inference from the original four-park statement, exact labels 1-4, coordinate rows, and the distinction from the 110 area-bearing regions. It is not misquoted as an explicit legend. Park geographic names are not needed because original numeric IDs suffice.

## Reader Verification

`xlrd 2.0.2` and `python-calamine 0.6.1` independently decoded both sheets. All 13,225 OD-sheet cell positions and 920 attribute-sheet positions agree, including headers and original blank values. Calamine trims the two entirely empty formatted columns G:H; padding these with empty strings yields zero discrepancies. The file was not converted, recalculated or re-saved. A BIFF record scan found zero FORMULA records; values do not rely on recalculating external formulas.

OD row IDs, column IDs and attribute IDs match exactly in order, are unique, and cover `1-4` plus `791-900`. All 12,996 OD entries are numeric, finite and nonnegative; 11,956 are positive and 1,040 are zero. There are 5,607 asymmetric unordered pairs. Example source-orientation witness: F2 is 791 -> 1, 487.798 tonnes; B6 is 1 -> 791, 504 tonnes. No symmetrization was performed. This counts data entries, not graph edges or routes.

Two original diagonal entries are nonzero: region 895 = 2.92 tonnes and 896 = 0.52 tonnes. They are preserved, and intra-region treatment must be explicit in a future run. All 114 coordinate pairs are finite numeric values. All 110 region area pairs and congestion indices are present. The m^2 column equals 1,000,000 times the km^2 column with zero observed floating-point difference in this check. Congestion ranges from 1.33 to 11.54; the original DOC permits values above 10 in its proportional simplification.

## Geometry Limits

The full JPEG and three native-resolution crops were visually inspected, including crowded labels 844-853 and 887-889. Region labels 791-900 and separate blue labels 1-4 are readable. Raster boundaries were recovered, not vector GIS polygons. Coordinates come from the original XLS, never from OCR or image pixels. There is no printed scale bar, north arrow, CRS, projection or coordinate origin identified. JPEG DPI is not ground resolution. No road network, existing tunnel network, engineering corridor or geographic obstruction is inferred from the boundary lines.

No missing essential attachment is concealed by these limits. Local metre-coordinate computations may be considered by a future run only with an explicit planar/geometry interpretation. Recovery does not establish surveyed road distance, tunnel length or physical constructability.

Park areas and congestion are blank in B2:C5 and F2:F5. These 12 cells were neither imputed nor converted to zero. They do not remove any of the 110 region attributes specified by the source. A later model must not treat the four separate parks as ordinary regions with invented area/index values.

## Integrity And Checks

- Source hashes: all five retained archive/member files must match the committed manifest; nested ZIP CRCs pass.
- Historical protection: the before snapshot covers 893 tracked/nonignored pre-existing files outside source-recovery, including protected history and existing untracked artifacts. The after check must report zero modified/missing files and no new out-of-scope files.
- Skill and run-001: empty tracked diff and unchanged Git tree hashes required; run-001 remains permanently `BLIND_RUN_PARTIAL`.
- Repository historical artifact test: executed read-only against original fixtures, with temporary files redirected into ignored source-recovery/work. See checks.json for actual output/status.
- No expensive model regression, optimization or blind-run workflow was rerun. `DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING` remains an inherited issue, not retested or repaired. `.tmp/github-publish-checkout`, frozen 2020A smoke duplicates and existing untracked history are untouched.
- Precommit index verification checks JSON parsing, source hashes and staged-byte equality. Postcommit checks verify committed manifest bytes and current branch remote SHA. Git delivery is separate from source authenticity.

## Acceptance

`ORIGINAL_SOURCE_RECOVERED` through a trusted institutional mirror. No claim of organizer-hosted official attachment discovery. No excellent solutions accessed. No Skill change. No Q1-Q4 solution, graph design, routing, flow or objective computation in this stage. Wait for human review before any run-002.
