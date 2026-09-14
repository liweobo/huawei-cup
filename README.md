# Huawei Cup 2026 Mathematical Modeling Skill

这是一个用于华为杯、研究生数学建模及相近竞赛任务的 Codex Skill。它帮助团队完成选题、赛题拆解、附件审计、模型比较、真实实验、验证、论文组织和提交检查，并要求结论可追溯到输入、实验和证据。

## 使用

可安装或复制的 Skill 只有 [`skill/`](skill/)。入口是 [`skill/SKILL.md`](skill/SKILL.md)，路由配置在 [`skill/routing.yaml`](skill/routing.yaml)。Skill 内的 rules、workflows、references、templates 和 scripts 按需加载；复制整个 `skill/` 后不需要本仓库其他目录。

## 内容导航

- 任务原则和渐进式路由：[`skill/SKILL.md`](skill/SKILL.md)
- 路由：[`skill/routing.yaml`](skill/routing.yaml)
- 必须遵守的规则：[`skill/rules/`](skill/rules/)
- 分任务工作流：[`skill/workflows/`](skill/workflows/)
- 按需领域参考：[`skill/references/`](skill/references/)
- 比赛运行模板：[`skill/templates/`](skill/templates/)
- 数模运行脚本：[`skill/scripts/`](skill/scripts/)

## 开发与验证

Benchmark、历史运行、评估器、测试和平台工具位于 [`development/`](development/)，不属于 Skill 分发内容。开发约束见 [`AGENTS.md`](AGENTS.md)，开发状态和回归命令见 [`development/README.md`](development/README.md)。

大型原始附件和冻结审计输出使用 [Git LFS](https://git-lfs.com/) 保存。开发或运行回归前请安装 Git LFS，并在克隆后执行 `git lfs pull`，确保获得完整数据。冻结证据保留原始字节，避免换行转换改变 SHA256。

Skill 结构校验：

```text
python C:/Users/aaa/.codex/skills/.system/skill-creator/scripts/quick_validate.py skill
```

根目录的 `pytest.ini` 和 `requirements-dev.txt` 仅服务开发测试，不应复制进 Skill。
