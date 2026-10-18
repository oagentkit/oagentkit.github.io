# llm

模型客户端——多模型降级链/任务级预算/成本记账/分阶段模型路由/主备切换

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 2 · 集成层（依赖 tier 0/1 + 重第三方地板） |
| oekit 对应 | `httpx` |
| 仓内依赖 | `textx`、`obs`、`runtime` |
| 被依赖 | `agent` |
| 第三方地板 | `github.com/cloudwego/eino`、`github.com/meguminnnnnnnnn/go-openai`、`github.com/cloudwego/eino-ext`、`golang.org/x/time` |
| 包数 | 3 |

## 安装

```bash
go get github.com/oagentkit/llm@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/llm](https://github.com/oagentkit/llm)

## 包

| 包 | 说明 |
| --- | --- |
| `llm` | 模型客户端：多模型降级链、任务级预算、成本记账、分阶段路由、主备切换 |
| `llm/wrap` | 调用包装与限流适配 |
| `llm/llmtest` | 模型层契约测试套件 |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

- **降级链的每一跳都必须记录原因**（成本/限流/超时/内容策略），不得静默换模型。
- **预算判定必须在调用前**，不能事后扣减 —— 事后扣减等于没有预算。
- **panic 不能只转成 error。** `RunSafe*` 系列会把 panic 收进全局 `PanicHandler`
  （库不接 `SetPanicHandler`，默认 `log.Printf`）且返回的 `panic: X` 无哨兵类型，
  无法挂回领域上下文。用 `RunSafeErr` 前先确认丢掉的结构化上下文可接受。

## 日志约定

- 日志走 `oekit/logx`，组件 logger 用 `logx.Delegating("oagentkit-llm")`，
  禁止 `Default()`/`WithService` 声明包级 logger。
- 模型请求/响应落日志前必须脱敏（凭据与用户数据都可能出现在 prompt 里）。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [AI Agent 编排](/guide/ai-agent.html)
- [模型调用与路由](/guide/llm-routing.html)
- [可观测](/guide/observability.html)
