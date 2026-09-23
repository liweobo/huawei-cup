# Huawei Cup 2026 Mathematical Modeling Skill

这是一个用于华为杯、研究生数学建模及相近竞赛任务的 Codex Skill。它帮助团队完成选题、赛题拆解、附件审计、模型比较、真实实验、验证、论文组织和提交检查，并要求结论可追溯到输入、实验和证据。

## 使用与分发

只需将完整 [`skill/`](skill/) 复制到你的 Skill 安装目录，命名为 `huawei-cup-2026`。入口是 [`SKILL.md`](skill/SKILL.md)，[`routing.yaml`](skill/routing.yaml) 提供 10 条路由；rules、workflows、references、templates、scripts 随该目录一起分发并按需加载。

在对话中明确数学建模项目背景，例如：“使用 huawei-cup-2026，先分析赛题与附件，列出输入、输出、约束和验证计划。”随后可继续提出“建立基线”“验证模型”“审查论文”等任务。Python helpers 要求 **Python >= 3.10**，并按使用的脚本安装科学计算依赖；已验证的开发环境为 Python 3.13.1。

## 开发与验证

Benchmark、历史运行、评估器、测试和平台工具位于 [`development/`](development/)，不属于 Skill 分发内容。历史题开发已完成，当前只做 release/readiness 维护，不安排新 benchmark。参见[历史闭环与能力清单](development/docs/historical-validation-closure.md)、[发布就绪报告](development/docs/release-readiness.md)及[完整回归命令](development/README.md)。开发约束见 [`AGENTS.md`](AGENTS.md)。

**Git LFS 仅完整 developer repository 的历史数据与完整回归需要**；使用 Skill-only 目录或 ZIP 不需要 Git LFS。开发者克隆后先执行 `git lfs pull`，获取原始附件及冻结审计输出。所有历史 evidence 保持原始字节，不转换换行。

从仓库根目录安装声明的开发依赖并做最小验证（建议先创建虚拟环境）：

```text
python -m pip install -r requirements-dev.txt
python development/harness/smoke_test.py
python -m pytest -q development/tests/test_skill_self_contained.py
```

结构 smoke 检查 live docs；冻结历史由独立 integrity tests 验证。根目录的 `pytest.ini`、`requirements-dev.txt` 仅服务开发测试，Skill 运行不读取它们。

## 生成 Skill-only ZIP

```text
python development/tooling/package_repository.py --skill-only --developer-repo . --output development/artifacts/huawei-cup-2026-skill.zip
```

输出文件须尚不存在。ZIP 只有 `skill/` 顶层目录，不含 development、历史 benchmarks、Git 数据或缓存。解压后复制整个 `skill/` 即可使用；验证过程见发布就绪报告。
