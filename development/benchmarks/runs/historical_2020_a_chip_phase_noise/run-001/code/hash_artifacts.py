from __future__ import annotations

import hashlib
import json
from pathlib import Path

run = Path(__file__).resolve().parents[1]
manifest = {}
for path in sorted(run.rglob("*")):
    if not path.is_file() or path.name == "artifact-hashes.json" or "__pycache__" in path.parts or path.suffix == ".pyc":
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest[str(path.relative_to(run)).replace("\\", "/")] = {"sha256": digest, "bytes": path.stat().st_size}
(run / "artifact-hashes.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"artifact_count": len(manifest), "manifest": str(run / "artifact-hashes.json")}, indent=2))
