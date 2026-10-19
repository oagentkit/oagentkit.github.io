# obs

观测与审计——Langfuse 追踪客户端/敏感操作结构化审计（不引 eino 框架）

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 2 · 集成层（依赖 tier 0/1 + 重第三方地板） |
| oekit 对应 | `metrics` |
| 仓内依赖 | `guardx`、`textx` |
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
| `langfuse` | Langfuse Public API 只读客户端（v3 self-hosted 契约面） |
| `audit` | 敏感操作的结构化审计留痕（自 guardx/audit 迁入）：字段值统一经 logredact 打码 |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

### trace 复用约束（不可自建）

**必须复用 `oekit/tracing` 的 Provider 和 `oekit/logx` 的 trace 提取器
（`logx.ExtractTrace`/`SetTraceExtractor`），不自建一套 trace。**
否则 agentkit 日志里的 trace_id 会与 OTel 的对不上，跨服务链路断裂。

### 与 oekit 的边界

本仓是**矩阵里唯一直接做 eino callbacks 适配**的仓 —— oekit 作为微服务工具链不会做 LLM 场景。
`oekit/tracing`（3 个导出）提供 Provider，本仓提供「把 LLM 调用挂上去」的适配层。两者互补，不重叠。
- **`audit` 自 `guardx/audit` 迁入**（v0.8.0）：它依赖 `oekit/logx`，而 guardx 是 tier 0 零依赖底层，依赖面按 module 结算。包名与职责不变，只是 import 路径变了。
- **层位 t1 → t2**：带 `eino` 地板（obsx 是 eino callbacks 适配层）——属集成层。重定位后 tier0/tier1 = 零重量级第三方地板的层（可被零依赖核心安全依赖）。
- **`obsx` 已迁至 `github.com/oagentkit/llm/obsx`**（v0.9.0）：它是 eino callbacks 适配层，在本仓时把 langfuse / audit 这两个轻包拖进 27 个第三方模块。迁走后本仓的 eino 依赖消失。

## 日志约定

- 日志走 `oekit/logx`，组件 logger 用 `logx.Delegating("oagentkit-obs")`。
- **观测数据不得携带凭据原文**，落盘前过 `guardx/logredact`。
- `audit` 包的 logger 为 nil 时回退 `logx.NewAuditLogger`（级别锁 `Info`、不受 `LOG_LEVEL` 降级、SetLevel 到 WARN/ERROR 被拒）—— 这是刻意设计，别改回普通 logger。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [模型调用与路由](/guide/llm-routing.html)
- [可观测](/guide/observability.html)
