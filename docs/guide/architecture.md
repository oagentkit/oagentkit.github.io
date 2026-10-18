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

<DependencyGraph />

图的数据由 `data/modules.json` 生成，与下面的矩阵表共用同一份依赖声明——
不会出现「图说 A 依赖 B、表说 A 不依赖 B」。

::: tip 无环即切仓可行
依赖图**无环**、最深 3 跳。这不是巧合，是当初按自底向上切仓可行性的硬证据：
无环意味着切仓不会产生循环 module 依赖。

`tier 3 · agent` 只有 1 个模块、零仓内被依赖——它是矩阵的顶点；
`tier 0` 四个模块全部零仓内依赖，是整张图的地基。
:::

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

→ 两套矩阵的定位对比、oekit 的 24 个模块分层、入口清单：**[姊妹项目 oekit](/guide/oekit)**

## 易踩的坑

### import 路径不是纯前缀映射

新路径 = `github.com/oagentkit/{仓名}/{包名末段}`。旧单仓路径的**中间层目录会被丢掉**，
因为新矩阵里那层组织职责由**仓**承担：

| 旧单仓 | 新路径 | 直觉会写成（错） |
| --- | --- | --- |
| `agentkit/knowledge/rag` | `oagentkit/rag/rag` | `oagentkit/rag/knowledge/rag` |
| `agentkit/worker/pglease` | `oagentkit/queue/pglease` | `oagentkit/queue/worker/pglease` |
| `agentkit/llm` | `oagentkit/llm/llm` | `oagentkit/llm` |

最后一条最坑：仓名与包名末段相同时**不能省掉一段**。
机器可读映射见 [`versions.json`](https://oagentkit.github.io/versions.json) 的 `fromLegacy` 字段。

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

### `runtime/breaker` 已退役

`runtime` 的 `breaker` 包**已删除**。原三态熔断器迁到
[`oekit/concurrency/breaker`](https://github.com/oekit/concurrency/breaker)，
由 `llm/breaker.go` 的准入适配层消费。

**退役是分阶段完成的**，顺序不能颠倒：

1. **上游先补能力** —— 上游 breaker 缺代绑定、探测时限、独立冷却、计数型触发，
   库形态消费方只能并行维护第二套熔断器。需求链 `#17 → #19 → #20 → #25` 全部关闭后，
   上游才有等价能力。
2. **消费方改依赖** —— `llm` 从 `oagentkit/runtime` 摘出来，改依赖
   `oekit/concurrency/breaker`（v0.9.0 → v0.12.0）。
3. **最后才删包** —— `runtime` 在 2026-10-18 02:07 用 `refactor!` 移除实现。

任何一步提前做都是构建断裂：消费方还 import 时删包会直接挂；上游能力没补齐就切会丢语义。

遗留：`llm` 侧还留着一段计数型准入否决作为兜底，等上游 `#25` 完全收敛后可去掉。

完整 issue 链见[模块总览](/modules/index.html)。

## 相关

- [模块总览](/modules/) —— 13 个模块的完整矩阵
- [CI 门禁与模块规则](/guide/contributing) —— 规则改动走哪条路
