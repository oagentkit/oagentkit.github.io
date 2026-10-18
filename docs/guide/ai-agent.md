---
title: AI Agent 编排
---

# AI Agent 编排

`oagentkit/agent` 是矩阵的 **tier 3 编排层**。它不发明算法，它提供**可复用的编排骨架 +
防失控守卫**——循环必须有上限、派发必须有白名单，这两件事每个 Agent 项目都要重写一遍。

```bash
go get github.com/oagentkit/agent@latest
```

## 六个包

| 包 | 职责 |
| --- | --- |
| `agentrun` | ReAct 运行样板与计划先行（PlanAndExecute）编排 |
| `reflection` | 反思循环 |
| `router` | 显式意图路由 |
| `blackboard` | 无中心多专家协作黑板 |
| `dispatch` | 通用派发守卫：allow 矩阵 + 深度上限 + 自派发拒绝 |
| `clarify` | 澄清与标准化词表内核 |

## 最硬的一条规则

> **编排层不得直连底层实现。** 所有能力经 `llm` / `mcpkit` / `toolgate` 等门面进入，
> 不得绕过门面直接调 provider 或 MCP client。

这条不是风格偏好。直连 provider 的后果很具体：降级链失效（挂了就没有第二个模型）、
预算失效（没人拦得住烧钱）、审计门失效（敏感工具调用绕过判定）。

代码上这条规则长这样——`router.New` 收 eino 的 `model.BaseChatModel`，
但内部持有的客户端是 `*llm.Client`，**门面是在构造时接上的**，你绕不过去：

```go
r, err := router.New(&router.Config{
    Model:        chatModel,      // eino 模型，作为配置面传进来
    ModelName:    "router-cls",   // 记账标识，走 llm 的成本台账
    Routes:       routes,
    Fallback:     fallback,
})
```

## 1. ReAct 样板：`agentrun`

`Run` 是一个带事件回调和重试的 ReAct 循环。

```go
answer, err := agentrun.Run(ctx, cfg, userQuery,
    agentrun.WithOnEvent(func(e agentrun.Event) {
        switch e.Type {
        case agentrun.EventReasoning:
            logger.Info("思考中", "text", e.Text)
        case agentrun.EventText:
            logger.Info("正文", "text", e.Text)     // 同轮收束后的权威快照
        case agentrun.EventTextDelta:
            render(e.Text)                            // 生成中逐分片，实况渲染用
        case agentrun.EventToolCall:
            logger.Info("调用工具", "name", e.Tool, "args", e.Args, "call_id", e.CallID)
        case agentrun.EventToolResult:
            logger.Info("工具返回", "name", e.Tool, "call_id", e.CallID)
        case agentrun.EventAttemptRetry:
            logger.Warn("整程重跑", "reason", e.Text)
        }
    }),
    agentrun.WithRetry("上一个回答没解决问题，请换个思路"),
)
```

`Event.CallID` 是**观测面精确配对的依据**——把 `tool_call` 和 `tool_result` 串起来
不要靠时间邻近猜。同轮 `text_delta` 只服务实况渲染，**回放/对账以同轮的 `text` 快照为准**。
中间调用轮没有 `text` 快照（只有终稿窗口有）。

选项命名是 `RunOption` / `WithXxx` 而不是裸 `Option`——**矩阵统一禁止裸 `Option`**，
多包 co-import 会撞名。

配置面在 `agentrun.Config`：`Model` / `Tools` / `MaxIterations` / `OnUsage` /
`RetryAfterMutation` / `NonMutatingTools` / `DisableStreaming` / `ModelOptions`。
其中 `RetryAfterMutation` + `NonMutatingTools` 解决的是「只读工具可以重试、
有副作用的工具不能」这个真实问题。

想拿用量，先 `cfg.Validate()`；单轮用量从 `OnUsage(ctx, Usage)` 拿，
字段与 eino `TokenUsage` 同义（`PromptTokens` / `CachedTokens` / `CompletionTokens` /
`ReasoningTokens` / `TotalTokens` / `FinishReason`）。
ReAct 没收敛出最终答案时会返回 `*agentrun.FinalMissingError`，
`errors.As` 接住它比裸比字符串稳。

## 2. 意图路由：`router`

选路和槽位提取**共用一次 LLM 调用**，零额外延迟和费用：

```go
r, err := router.New(&router.Config{
    Model:         chatModel,     // 用快模型即可
    ModelName:     "router-cls",
    MinConfidence: 0.6,           // 低于则走 Fallback

    Routes: []router.Route{
        {
            Name:        "bug-fix",
            Description: "定位并修复具体代码缺陷的问题",
            Handle:      handleBugFix,
        },
        {
            Name:        "code-review",
            Description: "对已有代码做评审、找问题的请求",
            Handle:      handleReview,
        },
    },

    // 槽位是正交维度：「要不要方案」不改变走哪条链，只改变链内行为
    Slots: []router.SlotSpec{
        {Name: "plan", Description: "是否要方案，取值 \"true\" / \"false\""},
    },

    Fallback: func(ctx context.Context, input, reason string) (string, error) {
        logger.Warn("路由兜底", "reason", reason)
        return "我没听懂，你可以……", nil
    },
})

dec, err := r.Classify(ctx, input)   // 只分类，不执行
out, err := r.Run(ctx, input)        // 分类并执行命中的链
```

`Decision` 带 `Route` / `Confidence` / `Reason` / `Slots`，**是可观测的**——
分类错了要能从日志里定位，不用猜。未配置的槽位模型多给的会被直接丢弃。

## 3. 派发守卫：`dispatch`

多 Agent 协作最容易出的事是**无限派发**。`Guard` 是构造期物化 allow 矩阵、运行期只读的守卫：

```go
type registry struct{ allow map[string][]string }

func (r registry) Slugs() []string             { /* 全部 slug */ }
func (r registry) DispatchAllow(s string) []string { /* s 允许派发给谁 */ }

guard := dispatch.NewGuard(registry, maxDepth=3)

err := guard.Assert(caller, callee, depth)  // 三个维度一起判
```

拒绝时返回 `*dispatch.DenyError`，`Reason` 三选一：

| 常量 | 含义 |
| --- | --- |
| `ReasonNotAllowed` | caller→callee 不在 allow 矩阵 |
| `ReasonDepthExceeded` | 派发深度超限 |
| `ReasonSelfDispatch` | 自派发（a 派发给 a） |

allow 矩阵是**白名单，默认拒绝**。另有 `AssertDepth` 单独判深度、`Allowed` 供查询。

::: danger allow 矩阵含环会 panic
`NewGuard` 在**构造期**对矩阵跑 DFS 环检测，有环直接 `panic`：

```
dispatch: allow 矩阵含环（a→b→a 乒乓/自环形态）——派发守卫无法收敛，请修正矩阵或拆环
```

这是故意的。`a→b→a` 乒乓环此前全靠宿主自觉递增深度计数拦截，
**漏递增就是无限派发**。fail-fast 远好过线上打转。自环同样拒绝——a 允许派发给 a 就是无限递归面。
:::

## 4. 反思循环：`reflection`

`Refine(ctx, cfg)` 内部持有 `*llm.Client`——又一次把「经门面」写进了类型。

它至少要配两个东西：**最大轮数**和**终止判据**。这是矩阵的硬规则，不是建议：

> 反思循环与黑板协作必须有**深度上限与终止条件**，防止无限循环。

## 5. 多专家黑板：`blackboard`

无中心协作——没有 leader，共享的是一块板子：

```go
b := blackboard.NewBoard()
b.Seed("task", "把登录接口加上限流")

e := b.Write("expert-a", "analysis", "当前没有限流中间件…")

b.Entries()               // 全部
b.EntriesAfter(e.Seq)    // 增量拉取——多专家循环的标准读法
b.Latest("analysis")      // 某类最新一条
```

读法用 `EntriesAfter` 配 `Entry` 上的序号做游标：**每轮只处理新增的**。
全量 `Entries()` 每轮重扫，专家一多就是 O(n²)。

::: warning 循环必须有上限
黑板协作天然容易发散——专家 A 看到专家 B 的结论又产生新任务。
**必须**在宿主侧自己数轮次并设上限，`blackboard` 本身不替你收口。
:::

## 6. 澄清内核：`clarify`

```go
entries, err := clarify.LoadVocab(fsys, "vocab.yaml")
err = clarify.Validate(entries)

idx, ok := clarify.OrdinalIndex(lower)                       // "第三项" → 2
picked, isFallback, ok := clarify.ResolveAnswer(opts, fb, answer)
```

意图不清时先澄清，比瞎猜一轮便宜。`OrdinalIndex` 处理序数词归一，
`ResolveAnswer` 把自由文本落到候选项上。

## 拼装一个 Agent

典型分层——**每层只做一件事，越权的事交给下一层**：

```
用户输入
   ↓
clarify      澄清 / 归一           ← 不清楚先问，别猜
   ↓
router       选路 + 抽槽位          ← 一次 LLM 调用
   ↓  命中链路
agentrun     ReAct / PlanAndExecute ← 循环，WithOnEvent 挂观测
   ↓  调用工具
toolgate     优先级 / 并发 / 审计门  ← 敏感操作在这里被拦
   ↓
mcpkit       MCP 工具池             ← 建连单飞
   ↓
obs          token / trace 打标
```

多专家协作时，把 `dispatch.Guard` 挂在 `blackboard` 的写入口，
把 `guard.Assert(from, to, depth)` 放在每次专家调用之前。

## 本仓硬规则速查

- **编排层不得直连底层实现** —— 经 `llm` / `mcpkit` / `toolgate` 门面
- **反思与黑板必须有深度上限与终止条件**
- **allow 矩阵白名单默认拒绝**，且有自派发拒绝
- error 一律 `oekit/pkg/errors`；禁止 `_` 忽略
- 禁裸 `go func`，用 `oekit/concurrency/async` 的 `GoSafe`
- logger 用 `logx.Delegating("oagentkit-agent")`
- 面向用户的最终输出落日志前过 `guardx/fence` 中和

完整规范以 [`agent/AGENTS.md`](https://github.com/oagentkit/agent/blob/main/AGENTS.md) 为准，本页是摘要。

## 相关

- [`agent` 模块页](/modules/agent) —— 依赖地板与包清单
- [模型调用与路由](/guide/llm-routing) —— 门面那一侧怎么做
- [工具接入与治理](/guide/tools-and-mcp) —— `toolgate` / `mcpkit`
