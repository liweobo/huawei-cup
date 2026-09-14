# Clean-Room Runtime

真实 Layer B 或可复现实验必须在开发仓库之外的临时 clean room 中启动。开发仓库是 Developer Repository；clean room 是 Model Runtime Workspace。两者不能通过把 working directory 改到子目录来代替隔离。

## Build

使用 [`../tooling/prepare_clean_room.py`](../tooling/prepare_clean_room.py) 的通用 `prepare_clean_room()` 或 CLI，传入 `developer_repo`、`benchmark_id`、`run_id` 和 `source.yaml`。默认输出到系统临时目录下的 `huawei-cup-benchmark/<run-id>/`；目标目录必须是新目录且位于开发仓库之外。

Builder 只复制：

- 当前 `skill/**` runtime 文件；
- `skill/` 内由工作流实际引用的 runtime 模板和脚本；
- `data_audit.py`、`metrics.py`、`plotting.py`、`robustness.py`、`runtime_provenance.py`、`sensitivity.py` 等正式运行工具；
- source manifest 声明的用户原始输入到 `input/`。

Runtime lifecycle 工具包括 builder、launch adapter、bundle validator 和薄 backend contract；这些脚本不携带 evaluator 数据。比赛规则位于 `skill/references/competition/2026-rules.md`，随 Skill 自包含复制。

输入优先使用 hard link，失败时使用普通复制；两种方式都必须重新计算 runtime SHA256 并与 canonical source 一致。禁止 symbolic link。`skill_hash`、输入清单和 `clean-room-manifest.yaml` 是启动前的 provenance。

## Visibility Gate

启动模型前运行 `scan_visibility()`。它递归扫描整个 clean room，并写出 `visibility-report.yaml`。以下内容默认禁止：历史 run、`benchmarks/`、`harness/`、`tests/`、`evaluation.yaml`、`postmortem.md`、`expected.yaml`、`ground-truth.yaml`、`problem-facts.yaml`、`transcript.yaml`、`result.txt`、rubric 和 known-failure 文件，以及 evaluator-only 结构化标记（如 `expected_route:`、`known_failure:` 和 `evaluator_notes:`）。发现任一匹配时状态为 `CLEAN_ROOM_FAIL`，不得开始 run。

`workspace/` 是唯一生成目录；使用 `writable_path_errors()` 或 `validate_generated_path()` 检查生成路径。Active Evidence Set 仍必须绑定当前 `run_id`；文件系统隔离不能替代证据选择隔离。

## Platform Launch Gate

`prepare_clean_room.py` 只证明准备出的 bundle 是干净的；它不能证明平台实际交给模型的 root 相同。启动真实模型前，host-side [`../tooling/runtime_launch_adapter.py`](../tooling/runtime_launch_adapter.py) 必须检查实际 root：绝对路径相同的运行是 `DIRECT`，路径不同但所有 model-visible regular files 的相对路径、类型和 SHA256 完全一致的运行是 `MANAGED_MIRROR`。缺少 `skill/`, `input/`, `workspace/`、出现 evaluator/prior-run 文件、hash 不一致或 workspace 写入失败时，binding 为 `UNBOUND`，不得发送 Turn 1。

Transport preflight 与模型对话分离。若使用 Responses function events，`function_call_output` 必须带有此前真实 `function_call` 的相同 `call_id`；缺失、孤立或错误配对必须在平台请求前 fail fast。provider、continuation mode 和 WebSocket 能力未知时记录 `UNKNOWN`，不猜测兼容性。adapter 的 binding/transport 结果写入 host-side report；它不修改 Skill 语义、不执行 benchmark turns，也不声称提供操作系统级 sandbox。平台无法选择或挂载实际 model-visible root 时，状态为 `BLOCKED_BY_PLATFORM`。

## Canonicalization

运行结束后只用 `canonicalize_clean_room()` 转移明确选中的 manifest、transcript、experiment records、evidence、paper 和关键 outputs/code。该函数为归档写入 hash 清单，并在校验完成后删除临时 clean room。不要把整个开发仓库或整个 clean room 无条件复制进 frozen archive。

平台级限制仍需单独说明：本工具提供项目级目录可见性和路径约束，不声称替代操作系统或 LLM agent 平台的 sandbox。若底层平台可读取 clean-room root 之外的全局文件，必须在运行报告中标记该残余风险。

## Portable Runtime

开发侧 `export_runtime_bundle.py` 调用现有 builder，再从生成的 `runtime_allowlist` 导出 Skill、正式工具、模板、运行参考文件与原始输入。`runtime-manifest.yaml` 使用相对路径记录每个 immutable file 的 SHA256、size、role、Skill identity 和 frozen user-script hash；脚本正文不进入运行包。原始附件在 portable bundle 中是普通副本，可独立搬迁。`workspace/` 初始只有当前 run 的 workspace manifest 和空 Active Evidence Set，其他子目录没有生成物。

外部 runner 安装 `runtime-requirements.yaml` 的 Python 依赖；把包作为唯一 project/mount，允许模型写入的路径只有 `workspace/`。设置 `PYTHONDONTWRITEBYTECODE=1`，将绘图配置目录等运行缓存放在 workspace 内。包内校验命令从 bundle root 执行：

```bash
python -B scripts/validate_runtime_bundle.py . --manifest-sha256 <trusted-manifest-sha256>
```

Manifest digest 与运行前 immutable snapshot 由 host 保管在模型可见目录之外；validator 的 `--snapshot` 和 `--verify-snapshot` 支持运行前后校验。Snapshot 检查同时覆盖 manifest 自身，防止改动文件后再改 manifest 掩盖 mutation。只读挂载优先；不具备只读能力时，pre/post hash 是检测手段，不等于阻止写入。任一 immutable 区域变化时为 `RUNTIME_INTEGRITY_FAIL`。

`runtime_backend.py` 只定义 `LOCAL_CONTROLLED`、`CONTAINER`、`MANAGED_WORKSPACE` 的接口与要求。Backend 名称不能证明隔离，实际 `filesystem_isolation_level` 在缺少平台证据时为 `UNKNOWN`。外部 runner 必须提供 actual root、可见范围、写入边界与 transport capability/probe evidence；`runtime_launch_adapter.py` 对 portable manifest 复用 V2.7 的 direct/mirror、hash、visibility、write probe 和 function pairing gate。只有 `READY_FOR_MODEL_TURN_1` 才允许在 fresh conversation 中提交首轮；export metadata 始终保留 `turn1_allowed: false`，新的 host preflight report 不写回 immutable metadata。

运行结束后先停止模型会话，再调用 `runtime_backend.export_workspace_outputs()`，传入可信 snapshot、停止状态和 host execution metadata。它在 immutable 校验后仅复制 workspace 与执行记录到新目录，并再次核对转移 hash。之后 evaluator 才能读取这些文件，模型会话不能共享 evaluator 的 live filesystem。临时包完成必要证据转移后可以删除；长期只保存必要 outputs、manifest digest、bundle digest 和 exporter version。
