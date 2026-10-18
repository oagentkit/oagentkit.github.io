# obs

LLM 可观测——eino callbacks 埋点/token 用量采集/分阶段打标/Langfuse 追踪客户端

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 1 · 能力层（依赖 tier 0） |
| oekit 对应 | `metrics` |
| 仓内依赖 | `textx` |
| 被依赖 | `llm` |
| 第三方地板 | `github.com/cloudwego/eino` |
| 包数 | 2 |

## 安装

```bash
go get github.com/oagentkit/obs@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/obs](https://github.com/oagentkit/obs)

## 包

| 包 | 说明 |
| --- | --- |
| `obsx` | eino callbacks 体系的 LLM 调用追踪 + token 用量采集 + 分阶段打标 |
| `langfuse` | Langfuse Public API 只读客户端（v3 self-hosted 契约面） |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

### trace 复用约束（不可自建）

**必须复用 `oekit/tracing` 的 Provider 和 `oekit/logx` 的 trace 提取器
（`logx.ExtractTrace`/`SetTraceExtractor`），不自建一套 trace。**
否则 agentkit 日志里的 trace_id 会与 OTel 的对不上，跨服务链路断裂。

### 与 oekit 的边界

本仓是**矩阵里唯一直接做 eino callbacks 适配**的仓 —— oekit 作为微服务工具链不会做 LLM 场景。
`oekit/tracing`（3 个导出）提供 Provider，本仓提供「把 LLM 调用挂上去」的适配层。两者互补，不重叠。

## 日志约定

- 日志走 `oekit/logx`，组件 logger 用 `logx.Delegating("oagentkit-obs")`。
- **观测数据不得携带凭据原文**，落盘前过 `guardx/logredact`。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [模型调用与路由](/guide/llm-routing.html)
- [可观测](/guide/observability.html)
