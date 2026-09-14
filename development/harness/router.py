"""Small semantic route selector used by the Skill harness.

This is intentionally not a general NLP classifier. It combines route signals
from routing.yaml with task-intent and context rules so that generic words such
as "模型" do not decide a route on their own.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RouteDecision:
    """A route prediction with transparent evidence for test/debug output."""

    route: str | None
    score: float
    evidence: tuple[str, ...]


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = REPO_ROOT / "skill"
ROUTING_PATH = SKILL_ROOT / "routing.yaml"


def load_routing(path: Path = ROUTING_PATH) -> dict[str, Any]:
    """Load and validate the routing YAML at a known path."""
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("routes"), dict):
        raise ValueError("routing YAML must contain a routes mapping")
    return data


def _norm(text: str) -> str:
    """Normalize text for phrase matching without stripping Chinese characters."""
    return " ".join(text.lower().strip().split())


def _contains(text: str, phrases: tuple[str, ...]) -> list[str]:
    """Return matched phrases, preferring longer phrases for evidence."""
    return [phrase for phrase in sorted(phrases, key=len, reverse=True) if phrase in text]


# These are deliberately small, high-signal patterns.  They suppress a broad
# intent only when the user explicitly negates it; they are not a general
# Chinese NLP parser.
NEGATED_MODEL_PHRASES = (
    "不要建模",
    "先不要建模",
    "先不建模型",
    "暂时不建模",
    "暂时不建模型",
    "不需要建模",
    "不要选模型",
    "先别选模型",
    "暂时不用模型",
    "暂时不需要模型",
    "不要上复杂模型",
)

# Triggering uses semantic signal groups instead of route matches.  Task words
# such as "附件" or "模型验证" are intentionally not standalone triggers.
EXPLICIT_DOMAIN_SIGNALS = (
    "华为杯",
    "研究生数学建模",
    "数学建模竞赛",
    "数学建模比赛",
    "数学建模项目",
    "数学建模",
    "数模",
    "建模竞赛",
    "国赛",
    "美赛",
    "mathematical modeling competition",
    "mathematical modelling competition",
    "mathematical modeling project",
    "mathematical modelling project",
)

STRONG_COMPETITION_ARTIFACTS = (
    "数模赛题",
    "数模附件",
    "数模论文",
    "数学建模论文",
    "华为杯建模",
)

DOMAIN_NEGATION_SIGNALS = (
    "不是在做数学建模",
    "并不是在做数学建模",
    "不在做数学建模",
    "没有在做数学建模",
    "不是在做数模",
    "并不是在做数模",
    "不在做数模",
    "没有在做数模",
    "不是数学建模",
    "并非数学建模",
    "不参加数学建模",
    "没参加数学建模",
    "与数学建模无关",
    "不是数模",
    "并非数模",
    "not a mathematical modeling",
    "not a mathematical modelling",
)

TASK_SIGNALS = (
    "选题",
    "拆题",
    "拆解",
    "怎么拆",
    "赛题",
    "分析题意",
    "题意分析",
    "输入输出",
    "问题依赖",
    "看看数据",
    "数据检查",
    "数据清洗",
    "数据审计",
    "审计",
    "附件",
    "csv",
    "xlsx",
    "模型设计",
    "模型选择",
    "重新设计模型",
    "模型验证",
    "交叉验证",
    "检查模型",
    "检查时间划分",
    "时间划分",
    "验证泛化",
    "泛化",
    "建模任务",
    "建模方案",
    "建模思路",
    "怎么建模",
    "建立模型",
    "开始建模",
    "帮我建模",
    "baseline",
    "基线",
    "实验",
    "跑实验",
    "模型实验",
    "实验结果",
    "可行性",
    "约束",
    "敏感性分析",
    "敏感性",
    "灵敏度分析",
    "灵敏度",
    "稳健性分析",
    "稳健性",
    "鲁棒性分析",
    "鲁棒性",
    "写论文",
    "论文",
    "整理结果",
    "结果部分",
    "决策建议",
    "写摘要",
    "摘要",
    "reviewer",
    "审稿",
    "找漏洞",
    "最终检查",
    "提交检查",
    "提交前",
    "复核",
    "下一步",
    "接下来",
    "model selection",
    "model validation",
    "validate the model",
    "data audit",
    "sensitivity analysis",
    "robustness analysis",
    "analyze the problem",
    "problem analysis",
    "write the paper",
    "write a paper",
)

NEGATED_FINAL_CHECK_PHRASES = (
    "不要做最终提交检查",
    "不做最终提交检查",
    "不要做提交检查",
    "不做提交检查",
    "不要做final check",
    "不做final check",
    "先别做最终提交检查",
)


def _has_negated_model_intent(query: str) -> bool:
    """Return whether the query explicitly defers or rejects model design."""
    return any(phrase in query for phrase in NEGATED_MODEL_PHRASES)


def _has_negated_final_check_intent(query: str) -> bool:
    """Return whether final submission checking is explicitly deferred."""
    return any(phrase in query for phrase in NEGATED_FINAL_CHECK_PHRASES)


def _risk_route(query: str) -> tuple[str | None, list[str]]:
    """Map high-risk signals to a safety-oriented route with evidence."""
    leakage = _contains(
        query,
        (
            "时间序列 shuffle",
            "shuffle 后划分",
            "随机划分时间序列",
            "过去未来混在一起",
            "训练集测试集按8:2随机",
            "未来数据进入训练集",
            "target leakage",
            "data leakage",
            "数据泄漏",
            "信息泄漏",
            "未来信息",
            "未来数据",
            "leakage",
        ),
    )
    if leakage:
        # A question about a split/validation protocol is already a validation
        # task; a vague suspicion is better handled by data audit first.
        validation_context = (
            "时间序列" in query
            or "shuffle" in query
            or "划分" in query
            or "验证" in query
            or "训练集" in query
            or "测试集" in query
            or "怎么" in query
            or "应该" in query
        )
        return ("validate_model" if validation_context else "audit_data", [f"risk:{p}" for p in leakage])
    if "时间序列" in query and ("shuffle" in query or "随机" in query) and ("划分" in query or "8:2" in query):
        return "validate_model", ["risk:time-series-random-split"]

    imbalance = _contains(
        query,
        ("类别不平衡", "样本不平衡", "少数类", "accuracy 很高", "准确率很高但少数类", "98:2", "99:1"),
    )
    numeric_imbalance = (
        "accuracy" in query
        and "类别" in query
        and bool(re.search(r"(?:98|99)\s*%", query))
        and bool(re.search(r"(?:1|2)\s*%", query))
    )
    if imbalance or numeric_imbalance:
        if numeric_imbalance:
            imbalance.append("high-accuracy-minority-class")
        return "validate_model", [f"risk:{p}" for p in imbalance]

    overfit = _contains(query, ("过拟合", "训练集很好测试集很差", "训练误差低验证误差高"))
    if overfit:
        return "validate_model", [f"risk:{p}" for p in overfit]

    feasibility = _contains(query, ("不可行", "约束冲突", "最优解不满足约束", "优化结果无法实施", "违反约束"))
    if feasibility:
        return "validate_model", [f"risk:{p}" for p in feasibility]

    inconsistency = _contains(
        query,
        (
            "论文结果和代码不一致",
            "论文中的结果和代码对不上",
            "论文中的结果和代码结果对不上",
            "结果和代码对不上",
            "表格和正文不一致",
            "摘要和正文不一致",
            "单位不一致",
        ),
    )
    if inconsistency:
        if any(signal in query for signal in ("提交", "最终", "检查")):
            return "final_check", [f"risk:{p}" for p in inconsistency]
        return "reviewer", [f"risk:{p}" for p in inconsistency]
    if ("结果" in query and "代码" in query and ("对不上" in query or "不一致" in query)):
        return "reviewer", ["risk:code-paper-inconsistency"]
    return None, []


def classify(text: str, state: dict[str, Any] | None = None) -> RouteDecision:
    """Choose a route from task intent, route signals and optional state.

    Explicit deliverable intents outrank broad model/data words. Competition
    context boosts route selection but does not activate the skill by itself.
    """
    if not text or not text.strip():
        return RouteDecision(None, 0.0, ())
    query = _norm(text)
    if any(phrase in query for phrase in ("翻译", "翻译成中文", "翻译这一段")) and not any(
        signal in query for signal in ("华为杯", "数模", "数学建模", "赛题")
    ):
        return RouteDecision(None, 0.0, ("boundary:translation",))
    data = load_routing()
    routes = data["routes"]
    scores: dict[str, float] = {name: 0.0 for name in routes}
    evidence: dict[str, list[str]] = {name: [] for name in routes}
    for name, config in routes.items():
        matches = _contains(query, tuple(config.get("triggers", [])))
        for phrase in matches:
            scores[name] += 1.0 + min(len(phrase) / 20.0, 1.0)
            evidence[name].append(f"signal:{phrase}")

    # Deliverable intent disambiguates broad signals such as 建模/模型/论文.
    intent_groups: dict[str, tuple[str, ...]] = {
        "select_problem": ("选题", "哪道题", "a题还是b题", "a题和b题", "比较a题b题", "选哪个", "多个赛题", "比较题目", "判断选哪道题"),
        "analyze_problem": ("到底让我求什么", "到底要求什么", "到底要做什么", "输入输出", "子问题", "问题三", "拆解题意", "拆题", "怎么拆", "题意分析", "分析题意", "分析题目", "分析这道题", "梳理这道题", "整体梳理", "问题依赖", "看问题依赖", "假设是不是太强"),
        "audit_data": ("附件", "缺失值", "异常值", "字段", "数据审计", "xlsx", "csv", "看看数据", "先看看数据", "字段含义"),
        "build_baseline": ("baseline", "基线", "基准模型", "对照模型", "简单模型", "规则基线"),
        "run_experiment": ("实验结果", "跑模型", "跑实验", "跑完", "重新跑实验", "实际算出来", "参数比较", "比较三个模型", "模型比较"),
        "validate_model": ("验证", "验证泛化", "泛化", "误差", "敏感性", "灵敏度", "参数扰动", "稳健性", "鲁棒性", "回测", "稳定不稳定", "检查可行性", "可行性", "时间划分"),
        "write_paper": ("写论文", "整理成论文", "整理摘要", "摘要", "问题重述", "结果分析", "整理结果", "结果部分", "论文结构", "决策建议"),
        "reviewer": ("审稿", "模拟评委", "找漏洞", "检查论文", "评审", "证据记录", "数字都能对应"),
        "final_check": ("提交检查", "最终检查", "final check", "提交前", "复核", "能否提交"),
        "design_model": ("模型设计", "模型选择", "用什么模型", "预测模型", "预测路线", "评价模型", "优化模型", "候选模型", "候选方案", "修正方程", "比较协议", "重新设计模型"),
    }
    for route, phrases in intent_groups.items():
        matches = _contains(query, phrases)
        for phrase in matches:
            scores[route] += 5.0 + min(len(phrase) / 10.0, 2.0)
            evidence[route].append(f"intent:{phrase}")

    # An explicit baseline shortfall followed by candidate comparison is a
    # model-design decision, not a request to rebuild the same baseline.
    candidate_after_baseline = any(signal in query for signal in ("候选模型", "候选方案", "模型比较")) or bool(
        re.search(r"候选.{0,4}模型", query)
    )
    if any(signal in query for signal in ("baseline", "基线")) and candidate_after_baseline and any(
        signal in query for signal in ("不够", "改进", "比较")
    ):
        scores["design_model"] += 8.0
        evidence["design_model"].append("intent:baseline-to-candidate-design")

    # When paper numbers are explicitly checked against a run/evidence record,
    # consistency review outranks generic writing language.
    if "论文" in query and "数字" in query and any(signal in query for signal in ("运行", "证据", "代码结果")):
        scores["reviewer"] += 8.0
        evidence["reviewer"].append("intent:paper-evidence-consistency")

    risk_route, risk_evidence = _risk_route(query)
    if risk_route:
        # Risks are blocking signals.  Give the route a deterministic boost so
        # that broad words such as “模型” cannot override them.
        scores[risk_route] += 12.0
        evidence[risk_route].extend(risk_evidence)

    # Broad signals are useful only when no stronger deliverable intent exists.
    if "模型" in query or "建模" in query:
        if not _has_negated_model_intent(query):
            scores["design_model"] += 0.5
            evidence["design_model"].append("broad:model")
        else:
            # Remove both the broad signal and any generic design intent that
            # was only activated by the negated phrase.
            scores["design_model"] = min(scores["design_model"], 0.0)
            evidence["design_model"] = [e for e in evidence["design_model"] if "model" not in e.lower()]
    if "论文" in query:
        scores["write_paper"] += 0.5
        evidence["write_paper"].append("broad:paper")
    if _has_negated_final_check_intent(query):
        scores["final_check"] = min(scores["final_check"], 0.0)
        evidence["final_check"] = [e for e in evidence["final_check"] if "final" not in e.lower() and "提交" not in e]

    # A negated model phrase still leaves the explicitly requested route in
    # charge.  These boosts cover terse mixed-intent requests where only a
    # broad word (e.g. “分析”) is otherwise present.
    if _has_negated_model_intent(query):
        if any(signal in query for signal in ("分析", "题意", "问题依赖", "输入输出", "拆题")):
            scores["analyze_problem"] += 8.0
            evidence["analyze_problem"].append("negation:explicit-analysis")
        if any(signal in query for signal in ("附件", "数据", "csv", "xlsx", "字段", "缺失")):
            scores["audit_data"] += 8.0
            evidence["audit_data"].append("negation:explicit-data-audit")
        if "baseline" in query or "基准" in query or "对照" in query:
            scores["build_baseline"] += 8.0
            evidence["build_baseline"].append("negation:explicit-baseline")
    if "数据" in query:
        scores["audit_data"] += 0.5
        evidence["audit_data"].append("broad:data")

    if state:
        phase = _norm(str(state.get("current_phase", "")))
        if phase in {"data", "data audit", "audit_data"}:
            scores["audit_data"] += 1.0
            evidence["audit_data"].append("state:phase")
        if phase in {"experiment", "validation"}:
            scores["run_experiment"] += 0.5
            scores["validate_model"] += 0.5

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_route, best_score = ranked[0]
    if best_score <= 0:
        return RouteDecision(None, 0.0, ())
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    # Ambiguous broad requests should not pretend to have precise routing.
    if best_score < 5.0 and best_score - second_score < 1.0:
        return RouteDecision(None, best_score, tuple(evidence[best_route]))
    return RouteDecision(best_route, best_score, tuple(evidence[best_route]))


def _has_explicit_domain(query: str) -> bool:
    """Return whether the request explicitly establishes modeling context."""
    if _contains(query, EXPLICIT_DOMAIN_SIGNALS):
        return True
    return bool(re.search(r"\b(?:mcm|icm)\b", query))


def _has_strong_competition_artifact(query: str) -> bool:
    """Return whether text names a high-specificity modeling artifact."""
    if _contains(query, STRONG_COMPETITION_ARTIFACTS):
        return True
    return bool(re.search(r"\b(?:mcm|icm)\s+(?:problem|problem\s*)?[a-f]\b", query))


def _has_domain_context(state: dict[str, Any] | None) -> bool:
    """Read the lightweight domain marker available to the harness/runtime."""
    if not state:
        return False
    marker = state.get("domain_context", state.get("Domain Context"))
    if marker is True:
        return True
    normalized = _norm(str(marker or ""))
    return normalized in {
        "mathematical_modeling",
        "mathematical_modeling_competition",
        "mathematical modelling",
        "mathematical modelling competition",
        "数学建模",
        "数学建模竞赛",
        "数模",
    }


def _has_task_signal(query: str) -> bool:
    """Return whether a carried-over request belongs to a Skill workflow."""
    if _contains(query, TASK_SIGNALS):
        return True
    return bool(
        re.search(
            r"(?:问题|第)\s*[一二三四五六七八九十\d]+|(?:[a-f])\s*题|\bproblem\s+[a-f\d]+\b",
            query,
        )
    )


def should_trigger(text: str, state: dict[str, Any] | None = None) -> bool:
    """Decide Skill activation independently from route classification.

    Explicit or carried-over modeling context must accompany a workflow task.
    Generic task words never trigger merely because they map cleanly to a
    route; high-specificity competition artifacts are the narrow exception.
    """
    query = _norm(text)
    if not query or _contains(query, DOMAIN_NEGATION_SIGNALS):
        return False
    if _has_strong_competition_artifact(query):
        return True
    return (_has_explicit_domain(query) or _has_domain_context(state)) and _has_task_signal(query)
