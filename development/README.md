# Development And Verification

这里保存 Skill 的开发、benchmark、历史证据、测试、评估器和平台适配内容。它们不进入可安装的 `skill/` 目录。

## 目录

- `benchmarks/`：题目原始输入、trajectory、transcript、冻结运行、run attempts、evaluation 和 postmortem。
- `harness/`：routing、trigger、behavior、trajectory、历史完整性、隔离和结构回归。
- `tests/`：Python 单元测试及 tiny fixtures。
- `tooling/`：clean-room、runtime binding、portable bundle 和 repository packaging 工具。
- `docs/`：平台限制、clean-room 和开发架构说明。
- `artifacts/`：被忽略的生成包和临时导出物。

## Current Development Status

`HISTORICAL_PROBLEM_DEVELOPMENT_COMPLETE`。当前维护模式为 **FINAL RELEASE / READINESS HARDENING**；no new benchmark scheduled，不启动 problem 11，不扩展建模能力。最终历史结论及单一 capability inventory 见[历史验证闭环](docs/historical-validation-closure.md)，本次交付检查见[release readiness](docs/release-readiness.md)。

## Historical Platform Incident / Archived Status

2024C Run-001、Run-002、Run-003 与其原始判定保持冻结。`run-004-attempt-001` 在 Turn 1 前因平台 transport 和 workspace binding 失败中止，其历史状态为 `BLOCKED_BY_PLATFORM`；它属于 archived behavioral-platform track，不是当前 release blocker，也不要求补跑 Run-004。2023E future-information leakage 初版证据的 invalidated 判定同样保留。

## 回归命令

要求 Python >= 3.10。先用 `python -m venv .tmp/release-venv` 创建干净环境；激活后执行 `python -m pip install -r requirements-dev.txt`。Windows 可直接用 `.tmp/release-venv/Scripts/python.exe` 替代下列 `python`，POSIX 使用 `.tmp/release-venv/bin/python`。完整回归前执行 `git lfs pull`。

从仓库根目录运行以下全部 21 个 active harness entry points，再运行 pytest 和编译检查。设置 `PYTHONDONTWRITEBYTECODE=1`；compileall 可用 `python -X pycache_prefix=.tmp/release-pycache -m compileall ...` 将缓存留在临时目录。

```text
python development/harness/smoke_test.py
python development/harness/routing_test.py
python development/harness/trigger_test.py
python development/harness/adversarial_trigger_test.py
python development/harness/behavior_contract_test.py
python development/harness/trajectory_test.py
python development/harness/trajectory_safety_test.py
python development/harness/historical_artifact_test.py
python development/harness/postmortem_regression_test.py
python development/harness/problem_facts_test.py
python development/harness/run001_integrity_test.py
python development/harness/run002_integrity_test.py
python development/harness/run003_integrity_test.py
python development/harness/run_attempt_integrity_test.py
python development/harness/clean_room_regression_test.py
python development/harness/temporal_availability_regression_test.py
python development/harness/runtime_binding_regression_test.py
python development/harness/portable_runtime_regression_test.py
python development/harness/repository_packaging_regression_test.py
python development/harness/protocol_order_regression_test.py
python development/harness/phase5_regression_test.py
python -m pytest -q
python -m compileall -q development/harness development/tooling development/tests skill/scripts
```

`harness/*.py` 中其余三个文件 `router.py`、`regression_contracts.py`、`model_behavior_evaluator.py` 是支持模块或 evaluator，不是遗漏的 release test。历史目录中的临时 tests 不加入 active list。上述检查不产生新的真实 LLM 行为结论。

Live smoke 不检查 `benchmarks/runs/**` 与 `benchmarks/run-attempts/**` 内生成 Markdown 的内容质量；它仍检查活跃文档指向历史文件的链接。历史 source、manifest、hash 和 evaluator 合同由 `historical_artifact_test.py`、各 run integrity tests 及闭环报告的冻结哈希检查单独保护。不得改写历史 REPORT、validation、占位词或链接来消除告警。

Skill-only 分发包可用 `python development/tooling/package_repository.py --skill-only --developer-repo . --output <temporary-path>/huawei-cup-2026-skill.zip` 生成；它只包含一个 `skill/` 顶层目录。
