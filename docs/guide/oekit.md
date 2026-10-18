---
title: oekit（姊妹项目）
---

# oekit（姊妹项目）

::: tip 一句话
oagentkit 依赖 oekit 的三个包，反过来不成立。**两者是两套独立矩阵，不是子品牌。**
:::

| | oagentkit | oekit |
| --- | --- | --- |
| 全称 | Open Agent Kit | Open Easy Kit |
| 面向 | Agent / LLM 编排 | Go 微服务 |
| 模块数 | 13 | 24 |
| 能力层 | 4 层（tier 0–3） | 5 层 |
| 框架地板 | eino | Hertz / Kitex |
| 适合谁 | 写 Agent、接模型与工具 | 写微服务、治理与数据访问 |

两者共享同一套**方法论**，各自独立发版：

- 按**框架耦合度**分层，不是按功能目录
- 依赖严格自底向上，无环
- 每仓独立 SemVer + 独立 CI
- **每个仓库根目录都有 `AGENTS.md`** —— 面向 AI Agent 的权威规范
- CI 门禁都是 reusable workflow，规则本体只在一个仓里

## 入口

| 去哪 | 地址 |
| --- | --- |
| 文档站 | [oekit.github.io](https://oekit.github.io) |
| 架构总览（五能力层架构图） | [oekit.github.io/about/architecture](https://oekit.github.io/about/architecture.html) |
| 模块索引（机器可读） | [oekit.github.io/llms.txt](https://oekit.github.io/llms.txt) |
| 版本矩阵 | [oekit.github.io/versions.json](https://oekit.github.io/versions.json) |
| GitHub 组织 | [github.com/oekit](https://github.com/oekit) |

## oagentkit 依赖它的三个包

只有这三个，其余 oekit 模块与本矩阵无关。

| oekit 包 | oagentkit 用在哪 |
| --- | --- |
| [`pkg`](https://github.com/oekit/pkg) | `errors`（Wrap/BizError）/ `stringx` / `encoding` / `mathx` —— 20 合 1 零第三方依赖微工具集 |
| [`concurrency`](https://github.com/oekit/concurrency) | `GoSafe` goroutine 池 / 单飞 / 重试 / 令牌桶 / 滑动窗口 / 时间轮 / 熔断 |
| [`logx`](https://github.com/oekit/logx) | 全矩阵日志门面，组件 logger 一律 `logx.Delegating("oagentkit-<repo>")` |

### 为什么是这三个

- **`pkg`** —— 纯标准库、零第三方依赖。带进来不会抬地板，这是能进底层依赖的第一条件。
- **`concurrency`** —— 并发原语与业务无关，两个矩阵都会用。
- **`logx`** —— 日志门面是全矩阵的**统一要求**（每个仓的 `AGENTS.md` 都写着日志走 `logx`）。

反过来 oekit **不会**做 LLM 场景适配：`oekit/tracing` 提供 Provider，
「把 LLM 调用挂上去」由本矩阵的 [`obs`](/modules/obs) 完成。
两者互补，不重叠。

## oekit 的 24 个模块

依赖严格自底向上，五个能力层：

| 层 | 模块 |
| --- | --- |
| 基础库 | `pkg` `kitx` `concurrency` `core` |
| 可观测性 | `logx` `tracing` `metrics` |
| 数据访问 | `gormx` `redis` `etcdx` `data` `timertask` |
| 通信 · 服务治理 | `httpx` `nns-endpoint` `network` `nns` `registry` |
| 应用引导 · 框架生态 | `bootstrap` `hertz` `kitex` `middleware` `workflow` `k8s` |

注意 `pkg` / `concurrency` / `logx` 分处**不同层**——oagentkit 挑的是三个不同层里的各一个，
不是因为它们在 oekit 内部挨着。

完整清单见 [oekit llms.txt](https://oekit.github.io/llms.txt)。

## 易混点

两套矩阵里有**同名但语义相反或不同族**的包，按包名对齐会做错：

| 包名 | oekit | oagentkit |
| --- | --- | --- |
| `progress` | 长任务**阶段进度追踪器** | 泛型**事件总线** |
| `breaker` | 自适应三态熔断（`GenBreaker` 代绑定） | 三态熔断器（待退役，阻塞中） |

两个仓都在你的 import 里，**按前缀逐段对**：`oekit/concurrency/progress` ≠
`oagentkit/runtime/progress`。`runtime/breaker` 的退役状态见[架构总览](/guide/architecture)。

## 相关

- [架构总览](/guide/architecture) —— 本矩阵的分层不变量
- [CI 门禁与模块规则](/guide/contributing) —— 两套矩阵共用的方法论
