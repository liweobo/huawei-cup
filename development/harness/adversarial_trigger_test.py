"""Independent trigger-boundary pressure test for V2.2 Phase 1."""

from __future__ import annotations

import sys

from router import should_trigger


CASES = (
    (False, "机器学习里的模型选择怎么做"),
    (False, "How should I tune a random forest?"),
    (False, "帮我分析这个业务 CSV"),
    (False, "请检查附件里的字段"),
    (False, "怎么做 k-fold cross validation?"),
    (False, "写一篇关于 XGBoost 的论文"),
    (False, "这个优化问题有哪些解法"),
    (False, "证明这个积分收敛"),
    (False, "普通数学问题的建模思路"),
    (False, "数学建模是什么"),
    (False, "我不是在做数模，只是学一下数据科学"),
    (False, "This is not a mathematical modeling project; explain PCA"),
    (True, "数模国赛 A 题如何拆解"),
    (True, "美赛 C题怎么做"),
    (True, "美赛 Problem B 的数据怎么审计"),
    (True, "MCM Problem C needs a baseline"),
    (True, "ICM Problem E sensitivity analysis"),
    (True, "我们的数学建模项目正在写摘要"),
    (True, "数学建模比赛先做数据清洗"),
    (True, "这是数模论文的 reviewer 检查"),
    (True, "2026 华为杯赛题附件"),
    (True, "mathematical modeling competition: validate the model"),
    (True, "数模项目怎么做交叉验证"),
    (True, "先分析题意，不要建模", {"domain_context": "数学建模竞赛"}),
    (True, "检查问题三", {"domain_context": "mathematical_modeling_competition"}),
)


def main() -> int:
    false_positive = 0
    false_negative = 0
    failures: list[str] = []
    for expected, text, *state in CASES:
        actual = should_trigger(text, state[0] if state else None)
        if actual != expected:
            failures.append(text)
            if actual:
                false_positive += 1
            else:
                false_negative += 1
    print(f"Adversarial Trigger Test: {len(CASES) - len(failures)}/{len(CASES)} passed")
    print(f"false positives={false_positive}, false negatives={false_negative}")
    if failures:
        print("failures:")
        print("\n".join(f"- {item}" for item in failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
