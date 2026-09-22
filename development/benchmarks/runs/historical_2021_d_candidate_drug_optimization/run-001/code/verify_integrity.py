"""Verify blind-run, Skill, and historical-asset integrity before commit."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


RUN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = RUN_ROOT.parents[4]
RUN_REL = RUN_ROOT.relative_to(REPO_ROOT).as_posix()
PROTECTED = {
    "historical_2020_e_visibility_forecasting": "101065189e56c1e9b9dc70c955045c44276aa54d",
    "historical_2007_a_food_safety_evaluation": "8b04b32b5966d5bae2085cb28d492246de78ecc9",
    "historical_2017_f_underground_logistics_network": "e2cc3eda04f300698edd078996a17be6584f1fcc",
    "historical_2005_d_stochastic_inventory": "1cb175c3339d2db9627945c25ecc27d02e894ebc",
    "historical_2020_a_chip_phase_noise": "6e7bd05c50aa614b1e741c08117765a17dd0a6ff",
    "historical_2011_b_absorbing_material_anechoic_chamber": "e04effd94bce8c3dca97c72155853aafc65df037",
    "historical_2022_c_buffer_scheduling": "92bd2ef04f834c8011d179e9dd4691f08209685d",
    "historical_2024_c_core_loss": "56dece647c5ab8ef7fff8a1713e1a8a4a1b6ac1a",
}


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=check
    )


def main() -> None:
    head = git("rev-parse", "HEAD").stdout.strip()
    skill_tree = git("rev-parse", "HEAD:skill").stdout.strip()
    status_lines = [
        line
        for line in git("-c", "core.quotepath=false", "status", "--porcelain=v1", "-uall").stdout.splitlines()
        if line
    ]
    changed_paths = [line[3:].replace("\\", "/") for line in status_lines]
    outside = [path for path in changed_paths if not path.startswith(RUN_REL + "/")]
    protected_records = {}
    for name, expected in PROTECTED.items():
        path = f"development/benchmarks/runs/{name}"
        actual = git("rev-parse", f"HEAD:{path}").stdout.strip()
        diff = git("diff", "--quiet", "HEAD", "--", path, check=False).returncode
        protected_records[name] = {
            "expected_tree": expected,
            "actual_head_tree": actual,
            "worktree_diff_empty": diff == 0,
            "status": "PASS" if actual == expected and diff == 0 else "FAIL",
        }
    protected_2023 = [
        "development/artifacts/2023e-reference-benchmark",
        "development/benchmarks/problems/2023/E",
        "development/benchmarks/runtime/historical_2023_e_hemorrhagic_stroke",
    ]
    protected_2023_records = {
        path: git("diff", "--quiet", "HEAD", "--", path, check=False).returncode == 0
        for path in protected_2023
    }
    forbidden_names = [
        path.relative_to(RUN_ROOT).as_posix()
        for path in RUN_ROOT.rglob("*")
        if path.is_file()
        and (
            path.suffix.lower() == ".pdf"
            or any(token in path.name for token in ["D21101080006", "D21102700119", "D21102980066", "D21104860088", "D21116460003"])
            or "优秀论文" in path.as_posix()
        )
    ]
    result = {
        "pre_commit_head": head,
        "expected_pre_commit_head": "4ff6213a729567ab916932bb0ce5a65bebd246b6",
        "skill_tree": skill_tree,
        "expected_skill_tree": "8deb5278e19862738d8f04f21d8a7b6d3f5eb45e",
        "skill_worktree_diff_empty": git("diff", "--quiet", "HEAD", "--", "skill", check=False).returncode == 0,
        "changed_path_count_before_integrity_record": len(changed_paths),
        "changed_paths_only_in_new_run": not outside,
        "outside_new_run_paths": outside,
        "protected_historical_trees": protected_records,
        "protected_2023_worktree_diffs_empty": protected_2023_records,
        "forbidden_reference_files_in_run": forbidden_names,
        "excellent_solutions_accessed": False,
    }
    result["status"] = (
        "PASS"
        if head == result["expected_pre_commit_head"]
        and skill_tree == result["expected_skill_tree"]
        and result["skill_worktree_diff_empty"]
        and result["changed_paths_only_in_new_run"]
        and all(item["status"] == "PASS" for item in protected_records.values())
        and all(protected_2023_records.values())
        and not forbidden_names
        else "FAIL"
    )
    (RUN_ROOT / "source-provenance" / "integrity-after.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": result["status"], "outside": outside, "skill_tree": skill_tree}, indent=2))


if __name__ == "__main__":
    main()
