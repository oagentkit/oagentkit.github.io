---
title: 架构总览
---

# 架构总览

## 分层判据

oagentkit 的切分轴是**框架耦合度**，不是功能目录。三条硬判据：

1. **依赖地板不同** —— 重第三方依赖（eino / milvus / mcp-go / lib/pq / mvdan.cc/sh / yaml）
   不同则必拆。地板不同意味着版本升级节奏不同，混在一仓会被 slowest 拖死。
2. **消费方集合不同** —— 谁 import 它决定它该独立发版还是当门面。
3. **变更节奏不同** —— 上游 issue 收口轮只碰一部分包时，不该带着全仓发版。

### eino 是本矩阵的「框架层」

13 个包直接依赖 `github.com/cloudwego/eino`。它在本矩阵的地位，
与 oekit 的 Hertz / Kitex 地位对等——**eino 就是这层地板**，而不是可选增强。

## 依赖方向

**tier N 不得依赖 tier > N。** 这是全矩阵唯一的结构性不变量。

```
tier 3 编排层    agent ─────────────► llm, textx
                                    │
tier 2 集成层    llm ──► obs, runtime, textx      toolgate ──► mcpkit
                  tools ──► guardx, runtime, textx
                                    │
tier 1 能力层    mcpkit ──► runtime     skillkit ──► guardx, textx
                  promptx ──► runtime, textx
                  obs ──► textx          rag ──► textx
                                    │
tier 0 基础层    textx   runtime   guardx   queue      （零仓内依赖）
```

依赖图**无环**、最深 3 跳 —— 这是当初按自底向上切仓可行性的硬证据。
依赖图无环，意味着切仓不会产生循环 module 依赖。

### 门面层

**编排层不得直连底层实现。** 所有能力经 `llm` / `mcpkit` / `toolgate` 等门面进入，
不得绕过门面直接调 provider 或 MCP client。

这条不是风格偏好：直连意味着你的编排代码会被具体 provider 的接口绑死，
降级链、预算、审计门全部失效——它们都挂在门面上。

## 与 oekit 的边界

oagentkit 依赖 oekit 的三个包，这是**单向**的：

| oekit 包 | oagentkit 用在哪 |
| --- | --- |
| `oekit/pkg` | errors / stringx / encoding / mathx |
| `oekit/concurrency` | goroutine 池 / 单飞 / 重试 / 令牌桶 / 滑动窗口 / 时间轮 |
| `oekit/logx` | 全矩阵日志门面，组件 logger 一律 `logx.Delegating` |

反过来不成立：oekit 作为微服务工具链不做 LLM 场景适配。
`obs` 是矩阵里**唯一**直接做 eino callbacks 适配的仓——
`oekit/tracing` 提供 Provider，oagentkit 提供「把 LLM 调用挂上去」的适配层，两者互补不重叠。

## 易踩的坑

### `progress` 撞名但语义相反

| | 语义 |
| --- | --- |
| `oekit/concurrency/progress` | 长任务**阶段进度追踪器** |
| `oagentkit/runtime/progress` | 泛型**事件总线** |

**按包名对齐会做错。** 两个仓都在你的 import 里，按前缀逐段对，别按末段包名猜。

### `pacer` ≠ `ratelimit`

- `pacer` 是**聚合缓冲**——攒够窗口再发，削峰。
- `ratelimit` 是**准入控制**——按速率放行，防超。

要「批量攒着发」用 pacer，要「别超过 N 次/秒」用 ratelimit。

### `runtime/breaker` 待退役

与 `oekit/concurrency/breaker` 重叠但**非同族**：后者是自适应概率丢弃，
前者是三态熔断器。上游需求见 [oekit/concurrency#17](https://github.com/oekit/concurrency/issues/17)。

**落地前不要删除。** 过渡期它仍在本仓可用。

## 相关

- [模块总览](/modules/) —— 13 个模块的完整矩阵
- [CI 门禁与模块规则](/guide/contributing) —— 规则改动走哪条路
