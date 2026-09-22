# Q3/Q4 calibration audit

`additional_q3_q4_calibration_material: UNVERIFIED`

The official full package has not been downloaded or enumerated. No conclusion can be made about whether it contains camera calibration, scene geometry, landmark distances, road dimensions, paired highway MOR, another video or additional README material. In particular, this stage does **not** assert `OFFICIAL_PACKAGE_CONTAINS_NO_ADDITIONAL_ABSOLUTE_MOR_CALIBRATION`.

The existing frozen mirror contains the problem documents, airport AMOS ZIP, 100 highway BMP screenshots and the airport-video link. Its source inventory and original archive hashes were rechecked; no new calibration input was recovered. The frozen run-001 identifiability limitation is therefore unchanged, not strengthened by an uninspected official package.

| Essential evidence | Current recovery evidence | Conclusion |
|---|---|---|
| Full airport video and verified alignment | Live share metadata only | Q2 source blocker remains |
| Metric highway landmark distances / camera geometry | No newly recovered input; official contents uninspected | UNVERIFIED |
| Highway image–MOR pairs | No newly recovered input; official contents uninspected | UNVERIFIED |
| Absolute MOR or 150 m crossing identification | No new absolute-scale evidence | `DATA_IDENTIFIABILITY_LIMIT` remains for available inputs |

`absolute_mor_identifiability_after_recovery: NO` applies to the actually available evidence. It is not a claim that every original source lacks calibration, or that the problem is intrinsically impossible. Relative monocular depth does not become metres without scale evidence. No model, relative-contrast series, Ridge/persistence comparison, prediction or crossing time was recomputed.
