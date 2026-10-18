---
title: 工具接入与治理
---

# 工具接入与治理

工具能力在矩阵里分三个仓，各管一段：

| 仓 | 层 | 管什么 |
| --- | --- | --- |
| [`mcpkit`](/modules/mcpkit) | tier 1 | MCP 客户端 / 工具池 / 建连单飞 / 自愈与租约 |
| [`toolgate`](/modules/toolgate) | tier 2 | 优先级三层约束 / 并发调度 / 操作审计门 |
| [`guardx`](/modules/guardx) | tier 0 | 凭据脱敏 / 出口 SSRF 防护 / 工具许可判定 / Shell 沙箱解析 / 审计 |

```bash
go get github.com/oagentkit/mcpkit@latest
go get github.com/oagentkit/toolgate@latest
go get github.com/oagentkit/guardx@latest
```

## 一、MCP 工具池：`mcpkit`

### 建连必须单飞

```go
pool := mcp.NewPool(
    mcp.ServerConfig{Name: "github", /* ... */},
    mcp.ServerConfig{Name: "fs",    /* ... */},
)

res, err := pool.Tools(ctx, []mcp.ToolSpec{
    {Server: "github", Allow: []string{"create_issue", "list_issues"}},
})
```

> **建连必须单飞。** 同一 server 的并发建连要合并为一次，
> 不得每次 `Allow` 都新建连接。

这条是本仓硬规则。并发场景下每次调用都新建连接，MCP server 会被打成筛子。
**等待方的 ctx 取消要各自生效**，不能干等 leader——否则先到的请求超时了，
后来的一批还挂在 leader 上一起卡死。

### 租约与自愈

```go
pool.PingServer(ctx, "github")
n := pool.ReapIdle(30 * time.Minute)      // 回收空闲连接，返回回收数
pool.StartIdleReaper(time.Minute, 30*time.Minute)
```

池内还有**传输层自愈**（`selfHealRedial`）：连接被判死时自动重连并重新装配工具，
工具调用侧感知不到。

### 工具注解归一

```go
hints := mcp.ToolHints{}
hints.ConcurrentSafe()   // == ReadOnly && Idempotent
hints.RiskLevel()
```

> 工具注解（`mcp.ToolAnnotation`）归一时，**`nil` 视为规范缺省，不得当成「无限制」**。

这个判断方向很关键：`nil` 的自然写法是「没标注 → 放开」，但 MCP 规范里缺省是保守值。
**放开要显式标，缺省按保守处理。**

### 错误即观测

```go
tools = mcp.WrapErrorAsObservation(tools)
```

MCP server 返回的错误里常带可供模型读的观测信息（"file not found: x"、
"rate limited, retry in 30s"）。`WrapErrorAsObservation` 把这类错误转成工具输出
而不是直接抛——模型看到能自己纠正，直接抛异常它只会重试同样的错。

## 二、优先级与并发：`toolgate`

### 三层约束是收紧语义

```go
tbl := toolprior.NewTable()
tbl.Add(toolprior.Entry{ /* ... */ })    // 可链式

ordered := tbl.Ordered(ctx)
prompt := tbl.StrategyPrompt(ctx)        // 给模型看的策略说明
```

> 优先级三层约束是**收紧**语义：上层只能进一步限制，**不得放宽**下层已设的限制。

这是白名单式设计——每加一层只会更严。想放宽，去掉那一层，不是把它改成宽松值。

单工具调用次数上限：

```go
limited := toolprior.LimitCalls(t, maxCalls)
```

### 注解驱动的并发调度

```go
sched, err := scheduler.Schedule([]toolsched.Call{ /* ... */ })
```

调度器按 `Hints` 决定能否并行，并且**做拓扑排序**——有依赖的调用按序，
无依赖的按 `maxConcurrency` 分组并行。

> 并发调度的**去重键必须包含全部影响结果的参数**，否则会错误合并不等价调用。

两个只有 `name` 相同但参数不同的调用，如果去重键漏了参数，会被错误合并成一个——
模型以为自己发起了两次，实际只执行了一次。

### 操作审计门：`policy`

三值裁决 + 两个过程值：

| Verdict | 含义 |
| --- | --- |
| `VerdictAuto` (`auto_proceed`) | 直接放行 |
| `VerdictNeedHuman` (`need_human`) | 要人工确认 |
| `VerdictDeny` (`deny`) | 拒绝 |
| `VerdictPlanOnly` (`plan_only`) | 计划模式：只审不执行 |
| `unknown` | 灰区待仲裁，**仅例外规则可产出** |

四种执行模式：

| Mode | 含义 |
| --- | --- |
| `ModeConfirm` | 变更前确认（**缺省**） |
| `ModeAuto` | 低风险（≤ `auto_max_risk`）系统代批 |
| `ModePlan` | 计划模式：方案只审不执行 |
| `ModeFull` | 完全访问：≤ `full_max_risk` 代批，**最高危恒人工双确认** |

模式归一 `Normalize` 的兜底很值得学：

> 空 / 非法一律回落 `confirm`。非法值在 API 入口已被 400 拦截（`ValidMode`），
> 这里是纵深兜底——**审计门不允许因模式脏值放大权限**。

## 三、安全围栏：`guardx`

```bash
go get github.com/oagentkit/guardx@latest
```

tier 0，零仓内依赖。六个包：

| 包 | 职责 |
| --- | --- |
| `fence` | 凭据脱敏、日志文本中和 |
| `logredact` | 日志脱敏 |
| `egress` | URL 出口 SSRF 防护 |
| `permgate` | 工具许可判定链 |
| `bashguard` | Shell 沙箱解析 |
| `audit` | 审计日志 |

两件事放前面做：

1. **用户可见内容进日志前过 `fence`** —— 面向用户的最终输出落日志前要过不可信文本中和，
   否则模型输出里的 ANSI 转义、控制字符、伪造日志行会污染你的日志系统。
2. **出网 URL 过 `egress`** —— SSRF 防护在解析和拨号两处都要管，
   只查 URL 字符串挡不住 DNS 重绑定和重定向。

## 拼起来

```
模型想调工具
   ↓
permgate     许可判定链          ← 这个工具有没有权限
   ↓
policy       操作审计门           ← 高危操作要不要人工确认
   ↓
toolprior    优先级 + 次数上限     ← 收紧，不放宽
   ↓
toolsched    并发调度 + 去重      ← 去重键含全部影响参数
   ↓
mcpkit       连接租约 + 自愈
   ↓
guardx       出网 SSRF / Shell 沙箱解析 / 输出脱敏
```

每层都有理由被插在这里——顺序不是随意的：
**便宜的判定放前面**（`permgate` 查表比拨号便宜几个数量级），
**有副作用的判定必须在执行前**（`policy` 必须在 `toolsched` 之前，
一旦并发跑起来再问人要确认就晚了）。

## 本仓硬规则速查

- `mcpkit`：建连单飞；等待方 ctx 各自取消；注解 `nil` 按保守缺省
- `toolgate`：三层约束只收紧；去重键含全部影响参数
- `guardx`：SSRF 防护在解析 + 拨号两处
- 三仓通用：error 走 `oekit/pkg/errors`；禁裸 `go func`，用 `async.GoSafe`

## 相关

- [`mcpkit`](/modules/mcpkit) · [`toolgate`](/modules/toolgate) · [`guardx`](/modules/guardx) 模块页
- [AI Agent 编排](/guide/ai-agent) —— 工具从哪来、谁来调
