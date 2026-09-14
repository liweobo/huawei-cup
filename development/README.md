# Development And Verification

这里保存 Skill 的开发、benchmark、历史证据、测试、评估器和平台适配内容。它们不进入可安装的 `skill/` 目录。

## 目录

- `benchmarks/`：题目原始输入、trajectory、transcript、冻结运行、run attempts、evaluation 和 postmortem。
- `harness/`：routing、trigger、behavior、trajectory、历史完整性、隔离和结构回归。
- `tests/`：Python 单元测试及 tiny fixtures。
- `tooling/`：clean-room、runtime binding、portable bundle 和 repository packaging 工具。
- `docs/`：平台限制、clean-room 和开发架构说明。
- `artifacts/`：被忽略的生成包和临时导出物。

## 当前状态

Run-001、Run-002、Run-003 保持冻结；Run-004 behavioral run 尚未执行，`run-004-attempt-001` 在 Turn 1 前因平台 transport 和 workspace binding 失败而中止。Temporal Availability / Outcome Horizon Gate 与有序等级目标建模协议已就绪，2023E 的 future-information leakage 初版证据仍保留并标为 invalidated。当前平台状态仍为 `BLOCKED_BY_PLATFORM`；这些能力更新不改变历史事实。

## 回归命令

从仓库根目录运行：

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
python development/harness/phase5_regression_test.py
pytest -q
python -m compileall -q development/harness development/tooling development/tests skill/scripts
```

这些测试是静态结构、路由和工具回归，不等价于真实 LLM 行为通过；不得在本阶段启动任何历史题或 Run-004。

Skill-only 分发包可用 `python development/tooling/package_repository.py --skill-only --developer-repo . --output <temporary-path>/huawei-cup-2026-skill.zip` 生成；它只包含一个 `skill/` 顶层目录。
