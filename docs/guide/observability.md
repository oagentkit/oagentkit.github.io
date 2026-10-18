---
title: 可观测
---

# 可观测

`oagentkit/obs` 是矩阵的 **tier 1 能力层**，也是**唯一**直接做 eino callbacks 适配的仓。
它和 [`llm`](/modules/llm) 的成本台账配合，回答两个问题：

- **钱花在哪个环节**（按 stage 归集）
- **这次调用到底走了哪个模型、报了什么错**（trace）

```bash
go get github.com/oagentkit/obs@latest
```

## 两个包

| 包 | 职责 |
| --- | --- |
| `obsx` | eino callbacks 体系的 LLM 调用追踪 + token 用量采集 + 分阶段打标 |
| `langfuse` | Langfuse Public API 只读客户端（v3 self-hosted 契约面） |

## 1. 分阶段打标

```go
ctx = obsx.WithStage(ctx, "R3")
stage := obsx.StageFromContext(ctx)
```

stage 词表和 [`llm` 的 `CostTracker`](/guide/llm-routing) 对齐：
`R1`/`R2`/`R3`/`R4`/`R5`/`plugin:xxx`。

**两处都要标**——`llm.Client.Generate(ctx, stage, ...)` 的参数位传一个，
`obsx.WithStage` 走 context 传一个。用 context 的好处是**不用改函数签名**，
新建的调用点也能自动带上阶段名。

## 2. TracingHandler

```go
h := obsx.NewTracingHandler(logger, obsx.Options{ /* ... */ })
h := obsx.NewTracingHandler(logger, opts)
```

返回 eino 的 `callbacks.Handler`，直接挂到 eino 的 callback 链上：

```go
callbacks.AppendGlobalHandlers(h)
```

它接管四类回调：

| 回调 | 记录 |
| --- | --- |
| `onStart` | 调用开始（模型、stage、入参摘要） |
| `onEnd` | 正常结束 + usage |
| `onError` | 出错 |
| `onStreamEnd` | 流式收束 + usage 补记 |

## 3. token 用量

```go
usage := obsx.TokenUsageOf(output)          // 从 CallbackOutput 取
u, name := obsx.DrainStreamUsage(streamReader)
```

::: warning 流式和非流式的用量位置不同
非流式：用量在 `onEnd` 的 `CallbackOutput` 里。
流式：增量片段里的 usage 可能是空的，**要 drain 完整条流**才有——
`DrainStreamUsage` 存在的理由就是这个。用 `TokenUsageOf` 直接读最后一片
大概率拿到零值。
:::

## 4. 用量标签

配合 [`llm.WithUsageLabels`](/guide/llm-routing)：

```go
ctx = llm.WithUsageLabels(ctx, map[string]string{"tenant": "acme"})
ctx = llm.WithCallCounter(ctx)
```

标签走 context 下传，最终聚到 `UsageRecord` 上，可以按租户/功能维度拆成本。

## trace 复用约束（不可自建）

> **必须复用 `oekit/tracing` 的 Provider 和 `oekit/logx` 的 trace 提取器
> （`logx.ExtractTrace` / `SetTraceExtractor`），不自建一套 trace。**
> 否则日志里的 trace_id 会与 OTel 的对不上，**跨服务链路断裂**。

这条是本仓最硬的规则。症状是：单服务看日志都正常，
一跳到下游就查不到上游——因为两套 trace_id 命名规则不一致。

## 与 oekit 的边界

| | 职责 |
| --- | --- |
| `oekit/tracing`（3 个导出） | 提供 Provider |
| `oagentkit/obs` | 把 LLM 调用挂上去的适配层 |

oekit 作为微服务工具链不做 LLM 场景适配，所以这块不会重复。
**两者互补，不重叠。**

## 5. Langfuse

`langfuse` 是 **Public API 只读客户端**，契约面为 v3 self-hosted。

只读——它把 Langfuse 里的 trace 拉回来看，不写入。
写入侧仍走你既有的埋点链路。

## 排查顺序

线上「答得慢 / 答得贵 / 答得不对」，按这个顺序看：

1. **`llm.Resilient.LastModel()`** —— 实际用了哪个模型？
   如果不是你配的主模型，降级已经触发了，去看 `FailoverModel.OnFailover` 记的原因。
2. **stage 分布** —— `CostTracker.Summary()` 按 stage 看成本，
   某一阶段占比异常高就是它的问题，不是模型的问题。
3. **trace** —— 用 `logx.ExtractTrace` 的 trace_id 串起全链路，
   跨服务跳不动就检查 trace 提取器配没配。
4. **usage 是否为零** —— 流式场景先确认 `DrainStreamUsage` 调了没有。

## 本仓硬规则速查

- **不自建 trace**，复用 `oekit/tracing` + `logx` 的 trace 提取器
- 流式用量必须 drain，别只读最后一片
- stage 命名要能回答「这次调用为什么花这笔钱」
- logger 用 `logx.Delegating("oagentkit-obs")`

## 相关

- [`obs` 模块页](/modules/obs) —— 依赖地板与包清单
- [模型调用与路由](/guide/llm-routing) —— 成本台账那一侧
