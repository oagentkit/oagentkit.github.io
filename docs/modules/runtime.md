# runtime

Agent 进程运行时——LLM token 流式节控/泛型事件总线/子进程最小环境/运行时热插拔/生命周期钩子

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 0 · 基础层（零仓内依赖或仅依赖同仓包） |
| oekit 对应 | `无直接对应；并发主体已上移到 oekit/concurrency` |
| 仓内依赖 | —（零仓内依赖） |
| 被依赖 | `promptx`、`llm`、`mcpkit`、`tools` |
| 第三方地板 | 零 |
| 包数 | 5 |

## 安装

```bash
go get github.com/oagentkit/runtime@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/runtime](https://github.com/oagentkit/runtime)

## 包

| 包 | 说明 |
| --- | --- |
| `pacer` | 流式增量节流器：LLM token 分片攒够窗口再发，避免逐条发布洪泛事件通道 |
| `progress` | 泛型事件总线 `Bus[T]`（发布订阅 + 慢消费者丢弃计数） |
| `procx` | 子进程最小环境构造 `ChildEnv` + 执行封装，供 spawn 外部进程的包共用 |
| `hotplug` | 运行时插拔与原子热替换：`Plugboard` 启停视图 + `Holder[T]` 快照持有点 |
| `hookx` | 外部 hook 拦截协议：在关键拦截点派生子进程，stdin 喂 JSON |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

### `progress` 撞名但语义相反（最容易踩）

- `oekit/concurrency/progress` = 长任务**阶段进度追踪器**（`NewTracker`/`PhaseConfig`/`PhaseStatus`）
- 本仓 `progress` = 泛型**事件总线**（`NewBus[T]`，发布订阅 + 慢消费者丢弃计数）

**任何按包名对齐的迁移/退役判断都会做错。对齐必须按语义。**

### `pacer` ≠ `ratelimit`

`oekit/concurrency/ratelimit` 是**准入控制**（允许发/不允许发），本仓 `pacer` 是**聚合缓冲**
（攒够窗口再发）。不是同一语义，不要互相替代。

### `procx` 的分层硬约束

`procx` 被 tier1 的 `mcpkit`、`promptx` 使用，**必须留在 tier0**。
把它并入 tier2 的 `tools` 会造成 tier1→tier2 分层倒挂，违反矩阵不变量。

### `breaker` 已退役（完整退役纪律）

本仓不再有熔断实现。`breaker` 已迁往 `oekit/concurrency/breaker`，
由 `llm` 仓按模型名分桶后转发调用。

**退役是有前置条件的，不能跳步**——`oekit/concurrency` 的 breaker 缺代绑定、
探测时限、独立冷却、计数型触发时，库形态消费方只能并行维护第二套熔断器。
需求链 `#17 → #19 → #20 → #25` 全部落地后才有等价能力。

四步顺序，颠倒任何一步都是构建断裂或语义丢失：

1. **上游先补能力** —— `#17` v0.9.0 → `#19`/`#20` v0.12.0 → `#25` v0.13.0
2. **消费方改依赖** —— `llm` 从 `oagentkit/runtime` 摘出，改依赖上游
   （2026-10-18 02:08）
3. **删本包实现** —— 本仓 `refactor!` 移除 breaker（2026-10-18 02:07）
4. **删本地兜底** —— 上游 `#25` 修好后，`llm/breaker.go` 里的计数型准入否决段
   已删除（2026-10-18 06:01），熔断语义全部委托上游

**不要在本仓重新实现熔断。** 需要熔断能力就用 `oekit/concurrency/breaker`。

## 日志约定

- **本仓不引入日志依赖。** tier0 加日志等于给所有下游抬地板；需要观测输出时返回 error 或交给调用方。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [AI Agent 编排](/guide/ai-agent.html)
- [模型调用与路由](/guide/llm-routing.html)
