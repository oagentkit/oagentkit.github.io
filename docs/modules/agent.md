# agent

Agent 编排——ReAct 运行样板/计划先行/反思循环/意图路由/多专家黑板/派发守卫

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 3 · 编排层（依赖 llm 等 tier 2 门面） |
| oekit 对应 | `workflow` |
| 仓内依赖 | `llm`、`textx` |
| 被依赖 | —（矩阵叶子） |
| 第三方地板 | `github.com/cloudwego/eino` |
| 包数 | 6 |

## 安装

```bash
go get github.com/oagentkit/agent@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/agent](https://github.com/oagentkit/agent)

## 包

| 包 | 说明 |
| --- | --- |
| `agentrun` | ReAct 运行样板与计划先行（PlanAndExecute）编排 |
| `reflection` | 反思循环 |
| `router` | 显式意图路由 |
| `blackboard` | 无中心多专家协作黑板 |
| `dispatch` | 通用派发守卫：allow 矩阵 + 深度上限 + 自派发拒绝 |
| `clarify` | 澄清与标准化词表内核 |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

- **编排层不得直连底层实现。** 所有能力经 `llm`/`mcpkit`/`toolgate` 等门面进入，
  不得绕过门面直接调 provider/MCP client。
- 反思循环与黑板协作必须有**深度上限与终止条件**，防止无限循环。
- 派发守卫的 allow 矩阵是白名单，默认拒绝；并有**自派发拒绝**（防止无限递归）。

## 日志约定

- 日志走 `oekit/logx`，组件 logger 用 `logx.Delegating("oagentkit-agent")`。
- 面向用户的最终输出落日志前过 `guardx/fence` 的不可信文本中和。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [AI Agent 编排](/guide/ai-agent.html)
