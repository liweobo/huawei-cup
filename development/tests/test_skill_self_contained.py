from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


PROJECT = Path(__file__).resolve().parents[2]
SKILL_SOURCE = PROJECT / "skill"


def _markdown_targets(path: Path) -> list[Path]:
    text = path.read_text(encoding="utf-8")
    targets: list[Path] = []
    for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
        value = match.group(1).split("#", 1)[0]
        if value and not value.startswith(("http://", "https://")):
            targets.append((path.parent / value).resolve())
    return targets


def test_skill_self_contained(tmp_path: Path) -> None:
    isolated = tmp_path / "skill"
    shutil.copytree(SKILL_SOURCE, isolated)

    assert (isolated / "SKILL.md").is_file()
    assert (isolated / "routing.yaml").is_file()
    routing = yaml.safe_load((isolated / "routing.yaml").read_text(encoding="utf-8"))
    assert isinstance(routing, dict)

    for config in routing.get("routes", {}).values():
        workflow = isolated / config["workflow"]
        assert workflow.is_file()
        for reference in config.get("required_reads", []):
            assert (isolated / reference).is_file(), reference
        workflow_text = workflow.read_text(encoding="utf-8")
        for link in _markdown_targets(workflow):
            assert link.is_file(), link

    all_markdown = list(isolated.rglob("*.md"))
    for path in all_markdown:
        for target in _markdown_targets(path):
            assert target.is_file(), f"broken Skill link: {path} -> {target}"
        # Parent-relative links are valid when they resolve inside the copied
        # Skill (for example, workflows linking to sibling rules/templates).
        # The invariant is no link or resource that escapes this root.
        for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            target = match.group(1).split("#", 1)[0]
            if target and not target.startswith(("http://", "https://")):
                assert (path.parent / target).resolve().is_relative_to(isolated.resolve())

    scripts = isolated / "scripts"
    assert scripts.is_dir()
    compile_result = subprocess.run(
        [sys.executable, "-B", "-m", "compileall", "-q", str(scripts)],
        cwd=isolated,
        env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
    )
    assert compile_result.returncode == 0, compile_result.stderr
    import_result = subprocess.run(
        [sys.executable, "-B", "-c", "import scripts.data_audit, scripts.metrics, scripts.temporal_availability, scripts.runtime_provenance, scripts.group_validation, scripts.stateful_scheduling, scripts.structured_improvement, scripts.mechanism_closure, scripts.spectral_conventions, scripts.evaluation_semantics"],
        cwd=isolated,
        env={**__import__("os").environ, "PYTHONPATH": str(isolated), "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
    )
    assert import_result.returncode == 0, import_result.stderr

    # The ordered-protocol fix must survive isolation: sequences stay order
    # sensitive and mapping keys stay canonical, without the development tree.
    behavior_result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            (
                "from scripts.runtime_provenance import protocols_differ; "
                "assert protocols_differ(['a','b','c'], ['b','a','c']) is True; "
                "assert protocols_differ({'x':1,'y':2}, {'y':2,'x':1}) is False; "
                "assert protocols_differ(('p','q'), ('q','p')) is True; "
                "assert protocols_differ(['a','b'], ['a','b']) is False; "
                "print('ok')"
            ),
        ],
        cwd=isolated,
        env={**__import__("os").environ, "PYTHONPATH": str(isolated), "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
    )
    assert behavior_result.returncode == 0, behavior_result.stderr

    evaluation_result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            (
                "from scripts.evaluation_semantics import should_activate, reviewer_codes; "
                "assert should_activate('TOPSIS multi-criteria decision'); "
                "assert not should_activate('ordinary regression prediction'); "
                "c={'evaluation_object':'city','decision_question':'relative order',"
                "'output_semantics':'RELATIVE_SCORE','output_method':'TOPSIS closeness',"
                "'absolute_or_relative':'RELATIVE','output_unit':'score',"
                "'output_scope':{'object':'city','population':'N/A','geography':'six cities','time':'2026','category':'city'},"
                "'comparator':{'used':False},'hard_gate':'NONE',"
                "'allowed_claim':'relative ranking','allowed_claim_semantics':['RELATIVE_SCORE','PROBABILITY'],"
                "'status':'EVALUATION_SEMANTICS_VERIFIED'}; "
                "assert 'RELATIVE_OUTPUT_AS_PROBABILITY' in reviewer_codes(c, 'PROBABILITY'); "
                "print('ok')"
            ),
        ],
        cwd=isolated,
        env={**__import__("os").environ, "PYTHONPATH": str(isolated), "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
    )
    assert evaluation_result.returncode == 0, evaluation_result.stderr
