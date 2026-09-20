"""Fetch only the user-authorized problem directory and exact F problem blob."""
import hashlib
import json
import subprocess
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
PROVENANCE = RUN / "source-provenance"
PROVENANCE.mkdir(exist_ok=True)
DIRECTORY = "国赛试题/2017年研究生数学建模竞赛试题"
API = "https://api.github.com/repos/zhanwen/MathModel/contents/" + urllib.parse.quote(DIRECTORY)
EXPECTED = "c2dd56c208cf3c7f80f2e52ff1f58ee0a758166f"


def fetch(url):
    url = urllib.parse.quote(url, safe=":/?=&%")
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "2017F-blind-source-audit"})
            with urllib.request.urlopen(req, timeout=15) as response:
                return response.read()
        except Exception:
            if attempt == 1:
                return subprocess.check_output(["curl.exe", "--fail", "--silent", "--show-error", "--retry", "2", "--retry-all-errors", "--max-time", "60", url])
            time.sleep(1)


listing_error = None
try:
    listing = json.loads(fetch(API))
    assert isinstance(listing, list), type(listing)
except Exception as error:
    listing = []
    listing_error = str(error)
metadata = [{key: entry.get(key) for key in ("name", "type", "sha", "size", "download_url")} for entry in listing]
(PROVENANCE / "directory-listing.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
matches = [entry for entry in listing if entry["sha"] == EXPECTED]
assert len(matches) <= 1, metadata
entry = matches[0] if matches else {
    "name": "2017年中国研究生数学建模竞赛F题.doc",
    "download_url": "https://raw.githubusercontent.com/zhanwen/MathModel/master/" + urllib.parse.quote(DIRECTORY + "/2017年中国研究生数学建模竞赛F题.doc"),
}
raw = fetch(entry["download_url"])
git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
assert git_blob == EXPECTED
source = next((RUN / "source").glob("*.doc"))
assert source.read_bytes() == raw, "Existing source differs; refusing to overwrite"
record = {"accessed_at": datetime.now(timezone.utc).isoformat(), "source_directory": API,
          "original_name": entry["name"], "download_url": entry["download_url"],
          "git_blob_sha": git_blob, "sha256": hashlib.sha256(raw).hexdigest(),
          "bytes": len(raw), "retained_source": str(source.relative_to(RUN)),
          "fresh_download_matches_preexisting_source": True,
          "directory_listing_error": listing_error,
          "scope": "Only authorized problem directory metadata and exact problem .doc downloaded; no solutions accessed"}
(PROVENANCE / "source.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(metadata, ensure_ascii=False, indent=2))
print(json.dumps(record, ensure_ascii=False, indent=2))
