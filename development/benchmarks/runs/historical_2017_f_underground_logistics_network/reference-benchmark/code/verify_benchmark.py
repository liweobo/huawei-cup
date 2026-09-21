"""Check this post-hoc archive without running a network model or changing history."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[4]
PREFIX = ROOT.relative_to(REPO).as_posix() + "/"
IDS = {"F10256001", "F10294003", "F10486024", "F10703002", "F10710008", "F90005027", "FK0263"}
REQUIRED = [
    "source-ledger.md", "current-skill-solution.md", "problem-interpretation-comparison.md",
    "q1-facility-comparison.md", "q2-network-comparison.md", "capacity-operation-comparison.md",
    "q3-robustness-comparison.md", "q4-phasing-comparison.md", "cost-comparison.md",
    "network-validation-comparison.md", "numerical-comparability.md", "reference-consensus.md",
    "reference-weaknesses.md", "generalizable-gaps.md", "REPORT.md", "completion.json",
    "paper-reviews.md", "review-audit.json", "verification.md", "test-record.json",
]


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO)


def check_pdf_bytes(data, entry):
    assert data.startswith(b"%PDF-"), entry["reference_id"]
    assert len(data) == entry["bytes"], entry["reference_id"]
    assert digest(data) == entry["sha256"], entry["reference_id"]
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    assert blob == entry["git_blob_sha"], entry["reference_id"]


def check_review(audit, extraction):
    rows = audit["files"]
    assert len(rows) == 7 and {x["reference_id"] for x in rows} == IDS
    pages = {x["reference_id"]: x["page_count"] for x in extraction}
    for item in rows:
        n = pages[item["reference_id"]]
        assert item["page_count"] == n
        assert item["text_pages_read"] == [1, n]
        assert item["all_sections_and_appendices_reviewed"] is True
        visual = item["visually_verified_pdf_pages"]
        assert visual and len(set(visual)) == len(visual)
        assert all(1 <= p <= n for p in visual)
    assert sum(x["page_count"] for x in rows) == 354
    assert sum(len(x["visually_verified_pdf_pages"]) for x in rows) == audit["visual_page_total"] == 33
    assert Counter(x["operation_class"] for x in rows) == {"STATIC_ONLY": 5, "PARTIAL_OPERATION_MODEL": 2}


def arithmetic():
    d = Decimal
    components = [d(s) for s in ["1997272.066880", "47318.678926", "90370340.288598", "808219.178082"]]
    assert sum(components) == d("93223150.212486")
    ground = {"817": d("1782.565") + d("2363.989"),
              "870": d("2156.898") + d("4156.393"),
              "832": d("1569.787") + d("2569.633"),
              "853": d("2710.378") + d("2051.691")}
    assert all(v > 4000 for v in ground.values())
    wrong_sum = d("1708.511") + d("3201.405")
    assert wrong_sum != d("4099.405")
    assert d("3576.821117") > 3000 and d("3200") > 3000
    secondary = [d(x) for x in ["3040.832", "3064.49", "3354.1796", "3212.684"]]
    assert all(x > 3000 for x in secondary)
    assert d("1.003") > 1 and d("1.176") > 1
    fk_parts = [d(x) for x in ["7.95", "45.90", "27.81", "47.12", "63.62", "32.77", "22.96"]]
    assert sum(fk_parts) == d("248.13")
    assert d("1.05") ** 3 < d("1.2") < d("1.05") ** 4
    return {
        "scope": "Printed-number arithmetic only; no network, routing, dispatch or expansion solve.",
        "frozen_cost_sum_yuan_per_day": str(sum(components)),
        "F10256001_pp23_24_primary_ground_t": {k: str(v) for k, v in ground.items()},
        "F10256001_p24_row894_898_sum": str(wrong_sum),
        "F10256001_p24_printed_sum": "4099.405",
        "F10294003_p16_secondary_ground_t": "3576.821117",
        "F10703002_p14_secondary834_ground_t": "3200",
        "F90005027_p16_secondary_ground_t": [str(x) for x in secondary],
        "F90005027_p50_tolerance_relative_to_annual_mean": str(d("0.1") / (d(1) / 8)),
        "F10710008_p31_probability_bound_violations": ["1.003", "1.087", "1.045", "1.176"],
        "FK0263_p32_rounded_cost_sum_wan_yuan_per_day": str(sum(fk_parts)),
        "FK0263_reported_physical_length_sum_km": str(d("35.29") + d("55.15") + 29),
        "FK0263_p22_park2_single_trip_departures": int((d(1080) - d("14.35576356")) // 12) + 1,
        "nominal_train_payload_10t_8vehicles_t": 80,
        "nominal_train_payload_5t_8vehicles_t": 40,
        "nominal_node_departures_5_per_hour_18hours": 90,
        "line_headway_only_2min_18hours_not_station_capacity": 540,
        "twenty_percent_reserve_first_exceeded_growth_step": 4,
        "F10703002_growth_29step_rounded_t": str((d("76240.97346") * d("1.05") ** 29).quantize(d("0.0001"))),
        "status": "PASS",
        "note": "PASS validates these reviewer arithmetic checks, not the reference solutions.",
    }


def snapshot_check():
    before = read("pre-reference-freeze.json")
    failures = [name for name, expected in before["files"].items()
                if not (REPO / name).is_file() or file_sha(REPO / name) != expected]
    assert not failures, failures
    for name, expected in before["trees"].items():
        assert git("rev-parse", "HEAD:" + name).decode().strip() == expected, name
    assert file_sha(ROOT / "current-skill-solution.md") == before["frozen_summary_sha256"]
    changed = git("diff", before["head"], "--name-only", "-z").decode().split("\0")
    assert all(not n or n.startswith(PREFIX) for n in changed), changed
    names = git("ls-files", "--cached", "--others", "--exclude-standard", "-z").decode().split("\0")
    added_outside = [n for n in names if n and not n.startswith(PREFIX) and n not in before["files"]]
    assert not added_outside, added_outside
    return before


def archive_files():
    return sorted(p for p in ROOT.rglob("*") if p.is_file()
                  and "work" not in p.relative_to(ROOT).parts
                  and "__pycache__" not in p.parts
                  and p.suffix != ".pyc"
                  and p.name != "artifact-manifest.json")


def check_archive_manifest(target=None):
    records = read("artifact-manifest.json")["files"]
    assert {x["path"] for x in records} == {p.relative_to(ROOT).as_posix() for p in archive_files()}
    for item in records:
        path = ROOT / item["path"]
        assert file_sha(path) == item["sha256"], item["path"]
        assert path.stat().st_size == item["bytes"], item["path"]
        if target:
            spec = (":" if target == "index" else "HEAD:") + PREFIX + item["path"]
            assert digest(git("show", spec)) == item["sha256"], spec
    if target:
        spec = (":" if target == "index" else "HEAD:") + PREFIX + "artifact-manifest.json"
        assert digest(git("show", spec)) == file_sha(ROOT / "artifact-manifest.json")
        entries = git("ls-files", "-z", "--", PREFIX).decode().split("\0")
        expected = {PREFIX + x["path"] for x in records} | {PREFIX + "artifact-manifest.json"}
        assert {x for x in entries if x} == expected
        if target == "index":
            staged = git("diff", "--cached", "--name-only", "-z").decode().split("\0")
            assert all(not n or n.startswith(PREFIX) for n in staged)


def dump(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--target", choices=["index", "head"])
    args = parser.parse_args()
    assert not (args.write and args.target), "Do not change the archive during index/commit verification"
    for name in REQUIRED:
        assert (ROOT / name).is_file(), name
    before = snapshot_check()
    manifest = read("reference-manifest.json")
    assert len(manifest["files"]) == 7 and {x["reference_id"] for x in manifest["files"]} == IDS
    for item in manifest["files"]:
        check_pdf_bytes((ROOT / item["path"]).read_bytes(), item)
        assert item["award_level"] == "UNKNOWN" and item["award_verified"] is False
    audit = read("review-audit.json")
    check_review(audit, read("extraction-audit.json"))
    completion = read("completion.json")
    assert completion["papers_fully_reviewed"] == 7
    assert completion["top_generalizable_gap"] == "NONE"
    assert completion["final_decision"] == "NO_MAJOR_GENERALIZABLE_GAP"
    assert completion["frozen_run_002_status"] == "BLIND_RUN_PARTIAL"
    for flag in ["skill_modified", "run_001_modified", "source_recovery_modified", "run_002_modified",
                 "earlier_historical_assets_modified", "problem_resolved_again"]:
        assert completion[flag] is False, flag
    formula = arithmetic()
    if args.write:
        dump("formula-checks.json", formula)
        dump("integrity-verification.json", {
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "baseline_head": before["head"],
            "head_at_archive_check": git("rev-parse", "HEAD").decode().strip(),
            "protected_file_count": len(before["files"]),
            "protected_file_sha256_mismatches": [],
            "protected_tree_hashes": before["trees"],
            "frozen_summary_sha256": before["frozen_summary_sha256"],
            "nonignored_new_files_outside_scope": [],
            "tracked_diff_outside_reference_benchmark": [],
            "reference_pdf_hashes_verified": 7,
            "reference_page_count": 354,
            "visual_review_pages": 33,
            "original_sources": "Original bytes included in pre-reference snapshot; no re-extraction or revision",
            "historical_tests": "test-record.json",
            "status": "PASS",
        })
        dump("artifact-manifest.json", {
            "scope": "All non-cache files in this directory except this manifest itself",
            "excludes": ["work/", "__pycache__/", "*.pyc", "artifact-manifest.json"],
            "files": [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
                       "sha256": file_sha(p)} for p in archive_files()],
        })
    else:
        assert read("formula-checks.json") == formula
    check_archive_manifest(args.target)
    print(json.dumps({"status": "PASS", "protected_files": len(before["files"]),
                      "references": 7, "pages": 354, "visual_pages": 33,
                      "archive_target": args.target or "working-tree"}))


if __name__ == "__main__":
    main()
