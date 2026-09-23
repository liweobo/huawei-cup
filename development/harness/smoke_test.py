"""Structural validation for the V2 Skill repository."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

from router import load_routing


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skill"


def live_markdown_files(root: Path) -> list[Path]:
    """Select live docs; immutable evidence is checked by integrity harnesses."""
    frozen_roots = (
        root / "development/benchmarks/runs",
        root / "development/benchmarks/run-attempts",
    )
    return [
        path for path in root.rglob("*.md")
        if not any(path.is_relative_to(frozen) for frozen in frozen_roots)
        and not set(path.relative_to(root).parts) & {"dist", ".tmp", ".pytest_cache", "artifacts"}
    ]


def markdown_targets(path: Path, text: str) -> list[Path]:
    """Resolve local Markdown links from one file."""
    targets: list[Path] = []
    for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
        target = match.group(1).split("#", 1)[0]
        if not target or target.startswith(("http://", "https://")):
            continue
        targets.append((path.parent / target).resolve())
    return targets


def workflow_required_reads(workflow: Path) -> set[Path]:
    """Return local links declared inside a workflow Required Reads section."""
    text = workflow.read_text(encoding="utf-8")
    section = re.search(r"## Required Reads\s*(.*?)(?=\n## |\Z)", text, re.IGNORECASE | re.DOTALL)
    if not section:
        return set()
    return set(markdown_targets(workflow, section.group(1)))


def fail(message: str, errors: list[str]) -> None:
    """Append one structural failure."""
    errors.append(message)


def check_live_markdown(root: Path, errors: list[str]) -> list[Path]:
    """Check live content without rewriting or interpreting frozen evidence."""
    markdown_files = live_markdown_files(root)
    hashes: dict[str, list[str]] = {}
    paragraphs: dict[str, list[str]] = {}
    for path in markdown_files:
        if path.stat().st_size == 0:
            fail(f"empty markdown: {path.relative_to(root)}", errors)
        content = path.read_text(encoding="utf-8")
        if re.search(r"\b(?:TODO|FIXME|PLACEHOLDER)\b", content, re.IGNORECASE):
            fail(f"unfinished placeholder in: {path.relative_to(root)}", errors)
        for resolved in markdown_targets(path, content):
            if not resolved.exists():
                fail(f"broken markdown link {path.relative_to(root)} -> {resolved}", errors)
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        hashes.setdefault(digest, []).append(str(path.relative_to(root)))
        for paragraph in re.split(r"\n\s*\n", content):
            normalized = re.sub(r"\s+", " ", paragraph.strip().lower())
            if len(normalized) >= 120 and not normalized.startswith(("|", "```")):
                paragraphs.setdefault(normalized, []).append(str(path.relative_to(root)))
    for duplicate_paths in hashes.values():
        if len(duplicate_paths) > 1:
            fail(f"duplicate markdown content: {duplicate_paths}", errors)
    for duplicate_paths in paragraphs.values():
        unique_paths = sorted(set(duplicate_paths))
        if len(unique_paths) > 1:
            fail(f"duplicate long paragraph: {unique_paths}", errors)
    return markdown_files


def main() -> int:
    """Run all structural checks and return a process status."""
    errors: list[str] = []
    required = [
        ROOT / "AGENTS.md",
        ROOT / "README.md",
        SKILL / "SKILL.md",
        SKILL / "routing.yaml",
        SKILL / "rules/index.md",
        SKILL / "workflows/index.md",
        SKILL / "references/index.md",
        SKILL / "references/models/index.md",
        SKILL / "templates/task-anchor.md",
        SKILL / "templates/competition-state.md",
        ROOT / "development/harness/smoke_test.py",
        ROOT / "development/harness/routing_test.py",
        ROOT / "development/harness/trigger_test.py",
        ROOT / "development/harness/adversarial_trigger_test.py",
        ROOT / "development/harness/behavior_contract_test.py",
        ROOT / "development/harness/trajectory_test.py",
        ROOT / "development/harness/trajectory_safety_test.py",
        ROOT / "development/harness/historical_artifact_test.py",
        ROOT / "development/harness/model_behavior_evaluator.py",
        ROOT / "development/harness/regression_contracts.py",
        ROOT / "development/harness/postmortem_regression_test.py",
        ROOT / "development/harness/problem_facts_test.py",
        ROOT / "development/harness/run001_integrity_test.py",
        ROOT / "development/harness/run002_integrity_test.py",
        ROOT / "development/harness/phase5_regression_test.py",
        ROOT / "development/harness/temporal_availability_regression_test.py",
        ROOT / "development/benchmarks/README.md",
        ROOT / "development/benchmarks/model-behavior-rubric.md",
        ROOT / "development/benchmarks/trajectories/schema.md",
        ROOT / "development/benchmarks/trajectories/schema.yaml",
        ROOT / "development/benchmarks/problems/README.md",
        ROOT / "development/benchmarks/transcripts/README.md",
        ROOT / "development/benchmarks/transcripts/schema.yaml",
        ROOT / "development/benchmarks/trajectories/historical-2024-c.yaml",
        ROOT / "development/benchmarks/problems/2024/C/source.yaml",
        ROOT / "development/benchmarks/problems/2024/C/user-turns.yaml",
        ROOT / "development/benchmarks/problems/2024/C/expected.yaml",
        ROOT / "development/benchmarks/problems/2024/C/evidence-ledger.yaml",
        ROOT / "development/benchmarks/runs/historical_2024_c_core_loss/run-manifest.yaml",
        ROOT / "development/benchmarks/runs/historical_2024_c_core_loss/run-001/run-manifest.yaml",
        ROOT / "development/benchmarks/runs/historical_2024_c_core_loss/run-002/run-manifest.yaml",
    ]
    for path in required:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}", errors)
    try:
        routing = load_routing()
    except Exception as exc:  # pragma: no cover - failure output is the assertion
        fail(f"routing parse failed: {exc}", errors)
        routing = {"routes": {}}
    for name, config in routing.get("routes", {}).items():
        for key in ("workflow", "required_reads"):
            values = config.get(key, []) if key == "required_reads" else [config.get(key)]
            for value in values:
                if not value:
                    fail(f"route {name} has empty {key}", errors)
                    continue
                target = (SKILL / value).resolve()
                if not target.exists():
                    fail(f"route {name} missing {key}: {value}", errors)
        workflow = (SKILL / config["workflow"]).resolve()
        if workflow.exists() and workflow.stat().st_size == 0:
            fail(f"empty workflow: {workflow.relative_to(ROOT)}", errors)
        if workflow.exists():
            expected_reads = {(SKILL / value).resolve() for value in config.get("required_reads", [])}
            declared_reads = workflow_required_reads(workflow)
            if expected_reads != declared_reads:
                missing = sorted(str(path.relative_to(ROOT)) for path in expected_reads - declared_reads)
                extra = sorted(str(path.relative_to(ROOT)) for path in declared_reads - expected_reads)
                fail(f"route/workflow Required Reads mismatch for {name}: missing={missing}, extra={extra}", errors)

    # Historical source/manifests remain required above. Content integrity is
    # enforced separately by historical_artifact_test and run integrity tests.
    markdown_files = check_live_markdown(ROOT, errors)

    agents = ROOT / "AGENTS.md"
    if agents.exists():
        for target in re.findall(r"`([^`]+(?:\.md|\.yaml|/))`", agents.read_text(encoding="utf-8")):
            resolved = (ROOT / target.rstrip("/")).resolve()
            if not resolved.exists():
                fail(f"AGENTS.md points to missing path: {target}", errors)

    workflow_names = {path.stem for path in (SKILL / "workflows").glob("*.md")}
    gotchas = SKILL / "references/gotchas.md"
    if gotchas.exists():
        gotcha_text = gotchas.read_text(encoding="utf-8")
        for activation in re.findall(r"`([a-z]+(?:-[a-z]+)+)`", gotcha_text):
            if activation in {"design-model", "write-paper", "final-check", "audit-data", "validate-model", "reviewer"} and activation not in workflow_names:
                fail(f"gotcha activation points to missing workflow: {activation}", errors)

    if errors:
        print("FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"PASS: smoke checks ({len(markdown_files)} markdown files, {len(routing['routes'])} routes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
