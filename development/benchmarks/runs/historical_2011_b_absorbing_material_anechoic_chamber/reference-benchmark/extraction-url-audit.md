# Extraction URL audit

The ignored local file `.tmp/extraction-metadata.json` was generated before the post-hoc ledger was completed and contains a malformed percent-encoding fragment in its automatically generated `github_url` values (`%E8%论文`). The downloaded PDF bytes and SHA256 values are unaffected.

The authoritative URLs recorded for this benchmark are:

- human-readable directory: `https://github.com/zhanwen/MathModel/tree/master/国赛论文/2011年优秀论文/B`
- encoded file template: `https://github.com/zhanwen/MathModel/blob/master/%E5%9B%BD%E8%B5%9B%E8%AE%BA%E6%96%87/2011%E5%B9%B4%E4%BC%98%E7%A7%80%E8%AE%BA%E6%96%87/B/<filename>`

The corrected template is used in `source-ledger.md`. The temporary extraction cache is intentionally not committed.
