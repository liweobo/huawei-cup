# Trigger Boundary

## Trigger

触发需要满足以下任一条件：

- 用户明确建立数学建模竞赛或数学建模项目上下文，并提出 Skill 能力范围内的当前任务；
- 当前对话已经建立该上下文，并且本轮请求属于 Skill 工作流；
- 用户提供高特异性的竞赛产物，例如 MCM/ICM Problem、数模赛题、数模附件或数模论文。

Harness 使用可选的 `state.domain_context` 模拟对话上下文延续；Competition State 中对应字段为 `Domain Context`。实际运行时应结合完整对话判断，不为此建立独立的复杂状态系统。

## Do Not Trigger

普通机器学习、数据分析、编程、论文写作、附件分析、优化问题或单道数学问题不应单独触发。`模型选择`、`模型验证`、`敏感性分析`、`CSV` 和 `附件` 等是 task signals，只用于已确认数模上下文后的任务识别与路由。

## Decision Order

先调用 `should_trigger` 判断请求是否属于本 Skill。只有结果为 true 时，才使用 `classify` 选择 route。Route 命中只说明“如果这是数模任务，应进入哪个工作流”，不能反向证明数模 domain 已成立。

## Negation

`不要建模`、`先不建模型` 通常表示暂缓模型设计，是 workflow 阶段约束，不表示退出 Skill。只有 `我不是在做数学建模`、`与数学建模无关` 等明确否定 domain 的表达才关闭触发。
