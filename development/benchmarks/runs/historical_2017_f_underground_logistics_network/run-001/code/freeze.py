"""Record and verify the frozen skill and pre-existing historical assets."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[4]
PROTECTED = ("2005", "2011", "2020", "2022", "2023", "2024")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO).decode("utf-8")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def selected(path):
    return path.startswith("skill/") or (
        path.startswith("development/") and any(year in path for year in PROTECTED)
    )


def snapshot():
    names = git("ls-files", "-z", "--cached", "--others", "--exclude-standard").split("\0")
    paths = sorted(set(p for p in names if p and selected(p)))
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "head": git("rev-parse", "HEAD").strip(),
        "skill_tree_hash": git("rev-parse", "HEAD:skill").strip(),
        "branch": git("branch", "--show-current").strip(),
        "status": git("status", "--short", "--untracked-files=all"),
        "protection_rule": "All tracked and nonignored untracked skill files; development paths containing 2005/2011/2020/2022/2023/2024. No historical content is opened for modeling.",
        "files": {p: digest(REPO / p) for p in paths},
    }


if __name__ == "__main__":
    root = RUN / "integrity"
    root.mkdir(exist_ok=True)
    initial = root / "before.json"
    current = snapshot()
    if sys.argv[1] == "before":
        if initial.exists():
            raise SystemExit("Refusing to overwrite initial freeze")
        initial.write_text(json.dumps(current, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in current.items() if k not in ("files", "status")}, indent=2))
        print("protected_files", len(current["files"]))
    else:
        before = json.loads(initial.read_text(encoding="utf-8"))
        changed = [p for p, h in before["files"].items() if current["files"].get(p) != h]
        added = sorted(set(current["files"]) - set(before["files"]))
        result = {"before_head": before["head"], "after_head": current["head"],
                  "skill_tree_before": before["skill_tree_hash"],
                  "skill_tree_after": current["skill_tree_hash"],
                  "protected_files": len(before["files"]), "changed": changed, "added": added,
                  "status": "PASS" if not changed and not added and before["skill_tree_hash"] == current["skill_tree_hash"] else "FAIL"}
        if "--check-only" not in sys.argv:
            (root / "after.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        if result["status"] != "PASS":
            raise SystemExit(1)
