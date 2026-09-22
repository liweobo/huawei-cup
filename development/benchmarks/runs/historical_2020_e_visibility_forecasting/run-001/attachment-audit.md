# Attachment audit

| Attachment | Integrity and contents | Dependent question | Status |
|---|---|---|---|
| Airport AMOS ZIP | Safe archive paths; two 24-hour events; each contains PTU, VIS, WIND `.his`; format-description DOCX verified | Q1; supports protocol-only forecast diagnostics | AVAILABLE |
| Highway screenshots ZIP | Safe archive paths; 100 BMP frames, each 1280×720; frame timestamps span about 06:30:26–07:39:11 | Q3 and Q4 | AVAILABLE |
| Airport video link | Markdown gives Baidu share link and password, but the remote object could not be obtained in this environment | Q2 | `SOURCE_ATTACHMENT_UNAVAILABLE` |

The AMOS format note defines `LOCALDATE (BEIJING)` and UTC `CREATEDATE`; `MOR_1A`/`RVR_1A` are one-minute averages, while VIS/WIND raw records are at approximately 15-second cadence. Extracted archive contents and rendered format-note pages are transient audit material and are not committed.

Impact boundary:

- Q1 can be attempted from AMOS.
- Q2 cannot be trained or evaluated because its indispensable image stream is unavailable. No reference paper was used to reconstruct it.
- Q3 can produce a scene-relative video contrast curve from the supplied frames. With no highway MOR labels or geometrically calibrated landmark distances, absolute MOR in metres remains unverified.
- Q4 can assess the direction and short-horizon behavior of that relative proxy, but a 150 m crossing/dispersal time is not identifiable without a defensible proxy-to-MOR calibration.

Overall essential-attachment status: `PARTIAL`.
