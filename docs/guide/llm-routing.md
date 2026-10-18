---
title: 模型调用与路由
---

# 模型调用与路由

`oagentkit/llm` 是矩阵的 **tier 2 集成层**，也是编排层唯一该走的模型门面。
它把降级、预算、成本、重试、错误分类收在一处——所以
[「编排层不得直连底层实现」](/guide/ai-agent) 那条规则在类型上就成立。

```bash
go get github.com/oagentkit/llm@latest
```

## 1. 客户端：`Client`

```go
budget := llm.NewBudget(200_000)          // 任务级 token 预算
c := llm.NewClient(chatModel, "gpt-4o-mini", budget)

msg, err := c.Generate(ctx, "R1", msgs)          // 普通生成
err = c.GenerateJSON(ctx, "R1", msgs, &out)      // 结构化输出

used := c.UsedTokens()
left := budget.Remaining()
```

每个调用都带一个 **`stage` 字符串**（`R1`/`R2`/`R3`/`R4`/`R5`/`plugin:xxx`）。
它不是日志装饰——成本台账按 stage 归集，`obs` 的分阶段打标也靠它。
**stage 命名要能回答「这次调用为什么花这笔钱」**，别都填 `"default"`。

### 预算必须在调用前判定

> **预算判定必须在调用前，不能事后扣减** —— 事后扣减等于没有预算。

`Client` 接的是 `TokenAccountant` 接口而不只是 `*Budget`，
所以你可以换成自己的账本实现（按租户、按用户、按阶段分账）：

```go
type TokenAccountant interface { /* ... */ }
```

## 2. 降级链：`FailoverModel`

```go
chain := llm.NewFailoverModel(
    llm.ChainLink{Model: primary,   Name: "primary"},
    llm.ChainLink{Model: secondary, Name: "cheap-fallback"},
)
chain.OnFailover = func(from, to, reason string) {
    logger.Warn("模型降级", "from", from, "to", to, "reason", reason)
}
```

> **降级链的每一跳都必须记录原因**（成本 / 限流 / 超时 / 内容策略），**不得静默换模型**。

这条是矩阵硬规则。不记原因的话，线上「答得慢而且变傻」你根本查不出是降级触发的。
`OnFailover` 是**每跳**回调，不是只在最终失败时调一次。

`FailoverModel` 实现 eino 的 `ToolCallingChatModel`，
所以 `WithTools` / `Generate` / `Stream` 都能直接接进 eino 的编排。

## 3. 分阶段路由：`StageRouter`

不同阶段用不同模型——分类用便宜快的，生成用强的：

```go
r := llm.NewStageRouter(defaultGen)
r.Use("router-cls", cheapFastModel)
r.Use("R5",        strongModel)
```

`StageRouter` 实现 `Generator`，接口和 `Client` 对齐
（`Generate` / `GenerateJSON` / `RawModel` / `UsedTokens`），
所以门面可以整体替换，下游编排代码一行不用改。

## 4. 错误分类：`RetryHint`

```go
hint := llm.ClassifyLLMError(err)
// hint.Retryable / hint.IsRateLimit / hint.IsTruncated

llm.IsRateLimitError(err)
llm.IsTruncatedError(err)
llm.RetryableLLMError(err)
```

退避策略区分 429 与普通错误（`backoffDelay(attempt, base, ceil, isRateLimit)`），
另有 `RetryAfter` 提示解析。**截断（truncated）和限流（rate limit）要分开处理**——
截断应该缩短输入重试，限流应该退避等待，混在一起会两头都做不好。

流式场景还有几个专用判定：

```go
llm.IsTransientStreamError(err)
llm.IsContextExceededError(err)       // 上下文超了要压缩，不是重试
llm.IsProviderBusyCode(code)
llm.SuspiciousEmptyResult(finishReason, respLen, toolCallCount, usageTotal)
llm.BusyAdmissionDelay(retry)
```

::: warning 上下文超限不是可重试错误
`IsContextExceededError` 命中说明**输入太长**。重试只会再超一次。
正确处理是压缩上下文（`textx/compact`）或分段，不是加重试。
:::

## 5. 成本记账：`CostTracker`

```go
ct := llm.NewCostTracker()
ct.Record("gpt-4o-mini", "R1", promptTokens, completionTokens, costPer1K)

for _, r := range ct.Records() { /* 逐次明细 */ }
sum := ct.Summary()      // map[model]*ModelSummary，含 TotalTokens() / CallCount
```

`CostRecord` 带 `Stage`（R1/R2/R3/R4/R5/plugin:xxx），所以**能按阶段归集成本**——
这是回答「钱花在哪个环节」的唯一依据。

## 6. 用量标签：`WithUsageLabels`

```go
ctx = llm.WithUsageLabels(ctx, map[string]string{"tenant": "acme", "feature": "chat"})
ctx = llm.WithCallCounter(ctx)
```

标签走 context 下传，`UsageRecord` 按 labels 聚合。
配 `obs` 的 trace 一起用，效果见[可观测](/guide/observability)。

## 7. 韧性：`Resilient`

`NewResilient(chain *FallbackChain, cfg ResilientConfig)` 在降级链外再包一层
单次尝试的超时、重试次数和尝试预算。`LastModel()` 告诉你最后实际用了哪个模型——
**排障时先看它**。`AttemptError` 用 `Unwrap() []error` 保留全部尝试的错误，
比只留最后一个有用得多。

## 关于 panic

::: danger panic 不能只转成 error
`oekit/concurrency/async` 的 `RunSafe*` 系列会把 panic 收进**全局** `PanicHandler`
（库不接 `SetPanicHandler`，默认 `log.Printf`），返回的 `panic: X` **无哨兵类型**，
挂不回领域上下文。用 `RunSafeErr` 前先确认丢掉的结构化上下文可接受。
:::

真要 recover，就自己写并保留类型：

```go
defer func() {
    if r := recover(); r != nil {
        err = errors.WrapBiz(fmt.Errorf("阶段 %s panic: %v", stage, r), "生成失败")
    }
}()
```

## 本仓硬规则速查

- 降级链**每一跳**都记原因，不得静默换模型
- **预算判定必须在调用前**
- panic 不能只转 error（见上）
- error 一律 `oekit/pkg/errors`，禁止 `_` 忽略
- 禁裸 `go func`，用 `async.GoSafe`
- logger 用 `logx.Delegating("oagentkit-llm")`

## 相关

- [`llm` 模块页](/modules/llm) —— 依赖地板与包清单
- [AI Agent 编排](/guide/ai-agent) —— 门面的调用侧
- [可观测](/guide/observability) —— 用量与 trace 怎么串
