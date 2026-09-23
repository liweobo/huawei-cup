# Reference Benchmark Validation

## Source-byte verification

All five temporary review copies matched both the supplied Git blob and the recorded SHA256 before cleanup.

| reference | Git blob | SHA256 | pages | result |
|---|---|---|---:|---|
| D21101080006 | `578f9f8a3b3f030bd0b4e7b8456627d0eadbd045` | `f9ac7ba22b06ee6d84a6f10b32a8b973c99feb57d789069b9018cf6835fbbf76` | 65 | PASS |
| D21102700119 | `731850f70e41f036e2edfe53f206c2dfc8873779` | `0355de2dacb187522ace7c5d858d6db08427d693f9a42319a794ab8f5757f391` | 49 | PASS |
| D21102980066 | `7f000f3664b534cde53be98fbcbf3f842683693d` | `030d464446526c366370b53b90058dd6d69cd43f9e9250e8f4bf8f1a6e9a1bcc` | 53 | PASS |
| D21104860088 | `c33f967f2510a8202e400fb3f630d9f06936a61e` | `6adc2185fdcee00276ce0b4e61bbe4bb5c97cb1cec579d9cc33c199d1715a8b0` | 69 | PASS |
| D21116460003 | `aece8efce5d3e7ab22d74c851b3ecc754b017fe9` | `322ec9baf97abad7f1db721b48bc2bc9eb2aacb85d87718a6b8550f893f9c246` | 55 | PASS |

Total reviewed pages: `291`.

## Artifact checks

| check | result | evidence |
|---|---|---|
| required artifact presence | PASS | all 20 required files present; `validation.md` and the separate freeze hash file are additional audit artifacts |
| JSON validity | PASS | `completion.json` parsed successfully |
| internal Markdown links | PASS | every relative link resolves within the benchmark directory |
| source-ledger consistency | PASS | all five IDs, blob IDs, SHA256 values, page counts, and `UNKNOWN` award policy agree |
| frozen summary hash | PASS | SHA256 `2b4e65b5a73fe7465e1e34891da91270f2d4f3ffb17b741faa608e8989c95bea` |
| forbidden artifact scan | PASS | no PDF, extraction cache, page render, solution code, `__pycache__`, or `.tmp` content in the benchmark directory |
| Git scope | PASS | all worktree changes are under this `reference-benchmark/` directory |

## Historical integrity

Each listed path had an empty worktree diff and no untracked content. Recorded baseline Git tree IDs:

| protected asset | tree ID | result |
|---|---|---|
| `skill/` | `8deb5278e19862738d8f04f21d8a7b6d3f5eb45e` | PASS |
| 2021D `run-001/` | `2bfd6738fe4428be8f7dfa286b43b5c22448ebdd` | PASS |
| 2020E | `101065189e56c1e9b9dc70c955045c44276aa54d` | PASS |
| 2007A | `8b04b32b5966d5bae2085cb28d492246de78ecc9` | PASS |
| 2017F | `e2cc3eda04f300698edd078996a17be6584f1fcc` | PASS |
| 2005D | `1cb175c3339d2db9627945c25ecc27d02e894ebc` | PASS |
| 2020A | `6e7bd05c50aa614b1e741c08117765a17dd0a6ff` | PASS |
| 2011B | `e04effd94bce8c3dca97c72155853aafc65df037` | PASS |
| 2022C | `92bd2ef04f834c8011d179e9dd4691f08209685d` | PASS |
| 2023E problem assets | `1d86b7ece9f07b6c9d67d9f82d7553758a13fade` | PASS |
| 2024C | `56dece647c5ab8ef7fff8a1713e1a8a4a1b6ac1a` | PASS |

The benchmark makes no executable change, so the expensive modeling suite was not repeated. Existing repository findings remain recorded as `DEFAULT_PYTEST_ENVIRONMENT_ISSUE_EXISTING` and `EXISTING_SMOKE_FAILURES_PRESERVED`; they were not modified.
