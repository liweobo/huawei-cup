# Attachment comparison

| Frozen GitHub mirror archive | Bytes | Git blob SHA1, recomputed | SHA256, recomputed | Equivalence to official package |
|---|---:|---|---|---|
| 机场AMOS观测.zip | 641,088 | `ecb627cb3b3e99b25f4e04c31dfe0d911f478c4f` | `06e9983053a059db4f92c3d0257d3063332586ccde00bb3d098f4f582e720002` | UNVERIFIED |
| 高速公路视频截图.zip | 12,352,504 | `80b3c261a5c0b0fcec6923111ad578f1f3500651` | `80fe0717d9389050ecae381b72d7a994eb7795ced907e30d0409e94b7104cbf8` | UNVERIFIED |

All six source files in the frozen mirror manifest retain their recorded SHA256, size and blob SHA1. The official RAR was not downloaded or enumerated. Consequently neither `BYTE_IDENTICAL`, `SEMANTICALLY_EQUIVALENT`, `DIFFERENT_VERSION` nor `MISSING_IN_ONE_SOURCE` can be established across the two sources. Both requested cross-source comparisons remain `UNVERIFIED`.

Read-only ZIP validation found 10 entries / 7 files in AMOS and 101 entries / 100 files in the highway archive. No absolute paths, parent traversal, drive-qualified paths or symlink members were found; all CRCs passed. No files were extracted. Details: [mirror-archive-verification.json](mirror-archive-verification.json).

The airport video is only a remotely listed candidate. A filename, declared size or provider metadata cannot prove its identity with a member of the unavailable official RAR.
