# Airport video verification

Candidate source: [original-problem mirror share](https://pan.baidu.com/s/15XKUMDUG-mlF3OZ9iRTrYg), linked by the frozen original markdown (blob `87804adeedc51c1abf53b7142655deb286c12c73`), share code `kxst`.

| Check | Result | Evidence level |
|---|---|---|
| Remote object found | YES: `Fog20200313000026.mp4` | Share listing reopened on continuation |
| Declared size | 1,042,173,258 bytes | Earlier page metadata, 2026-09-22T08:49:29.704Z |
| Declared duration | 41,609 seconds | Provider metadata; not measured from original media |
| Declared resolution | 1280×720 | Provider metadata; not locally decoded |
| Complete local file / SHA256 | NO / unavailable | Download directory empty |
| Readability and decode | UNVERIFIED | No complete original file |
| Frame count / frame rate | UNVERIFIED / UNVERIFIED | Neither inferred from duration nor taken from snippets |
| Embedded timestamps / time base | UNVERIFIED | Filename is not a verified capture timestamp |
| Match to problem and AMOS event times | UNVERIFIED | Requires full source/time-base inspection |
| Membership in official full package | UNVERIFIED | Official archive unavailable |
| Download outcome | NOT_RECOVERED | Visible download reached verification-code prompt; web player offers a 90-second preview |

`airport_video_found: YES` means a live remote listing was found. `airport_video_verified: NO` and `SOURCE_RECOVERED` is not established. Preview playback or preview images do not establish full duration, full decode, provenance, complete frame coverage or usable training/evaluation data. No preview is used as a substitute for the original video; no frames or labels are reconstructed from solutions.
