"""Static Behavior Contract checks for all V2.2 Skill routes.

This is not an LLM behavior test.  It verifies that important routes are
connected to a real workflow, required reads and observable workflow checks.
Real model behavior still requires pressure-testing with historical problems.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from router import load_routing


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skill"


CONTRACTS: dict[str, dict[str, tuple[str, ...]]] = {
    "select_problem": {
        "terms": ("Baseline", "风险", "换题"),
    },
    "analyze_problem": {
        "terms": ("输入", "输出", "约束", "依赖"),
    },
    "audit_data": {
        "terms": ("缺失", "重复", "异常", "时间", "泄漏"),
    },
    "design_model": {
        "terms": ("Baseline", "候选", "比较"),
    },
    "build_baseline": {
        "terms": ("Baseline", "真实运行", "比较"),
    },
    "run_experiment": {
        "terms": ("Baseline", "指标", "运行", "复现"),
    },
    "validate_model": {
        "terms": ("leakage", "灵敏度", "鲁棒性"),
    },
    "write_paper": {
        "terms": ("摘要", "数字", "创新"),
    },
    "reviewer": {
        "terms": ("P0", "P1", "P2", "P3", "泄漏", "一致", "验证"),
    },
    "final_check": {
        "terms": ("READY", "NOT READY", "P0", "一致"),
    },
}


def _workflow_reads(workflow: Path) -> set[Path]:
    """Resolve Markdown links listed in a workflow's Required Reads section."""
    text = workflow.read_text(encoding="utf-8")
    section = re.search(r"## Required Reads\s*(.*?)(?=\n## |\Z)", text, re.IGNORECASE | re.DOTALL)
    if not section:
        return set()
    resolved: set[Path] = set()
    for target in re.findall(r"\]\(([^)#]+)", section.group(1)):
        resolved.add((workflow.parent / target).resolve())
    return resolved


def _section_has_content(text: str, heading: str) -> bool:
    """Check that a required workflow section exists and is non-empty."""
    match = re.search(rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return bool(match and match.group(1).strip())


def main() -> int:
    """Run static route-to-workflow contracts and return a process status."""
    routing = load_routing()
    failures: list[str] = []
    required_sections = ("Outputs", "Stop Conditions", "Handoff")
    for route, contract in CONTRACTS.items():
        config: dict[str, Any] | None = routing["routes"].get(route)
        if not config:
            failures.append(f"{route}: route missing")
            continue
        workflow = (SKILL / config["workflow"]).resolve()
        if not workflow.exists():
            failures.append(f"{route}: workflow missing: {workflow.relative_to(ROOT)}")
            continue
        workflow_text = workflow.read_text(encoding="utf-8")
        declared_reads = _workflow_reads(workflow)
        configured_reads = {(SKILL / path).resolve() for path in config.get("required_reads", [])}
        for path in configured_reads:
            if not path.exists():
                failures.append(f"{route}: required reference missing: {path.relative_to(ROOT)}")
        if declared_reads != configured_reads:
            missing = sorted(str(path.relative_to(ROOT)) for path in configured_reads - declared_reads)
            extra = sorted(str(path.relative_to(ROOT)) for path in declared_reads - configured_reads)
            failures.append(f"{route}: Required Reads mismatch: missing={missing}, extra={extra}")
        for section in required_sections:
            if not _section_has_content(workflow_text, section):
                failures.append(f"{route}: workflow lacks non-empty {section} section")
        for term in contract["terms"]:
            if term.lower() not in workflow_text.lower():
                failures.append(f"{route}: workflow lacks check term {term!r}")
        status = "PASS" if not any(item.startswith(f"{route}:") for item in failures) else "FAIL"
        print(f"{status} | {route}")
    if failures:
        print("\nStatic Behavior Contract: FAIL")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print(f"\nStatic Behavior Contract: PASS ({len(CONTRACTS)} contracts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
