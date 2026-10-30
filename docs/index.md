---
layout: home

hero:
  name: oagentkit
  text: Open Agent Kit
  tagline: Agent / LLM 编排工具链模块矩阵
  image:
    src: /logo.svg
    alt: oagentkit
  actions:
    - theme: brand
      text: 快速开始
      link: /guide/getting-started
    - theme: alt
      text: 模块总览
      link: /modules/
    - theme: alt
      text: llms.txt
      link: /llms.txt

features:
  - title: 13 个独立发版模块
    details: 每仓独立 SemVer + 独立 CI，依赖严格自底向上。不用被最慢的那个依赖拖住升级节奏。
  - title: 每仓都有 AGENTS.md
    details: 面向 AI Agent 的权威规范——分层不变量、错误处理、日志、并发安全、该仓特有的工程红线。
  - title: 机器可读
    details: llms.txt 模块索引、versions.json 版本矩阵，还有 matrix-tools 仓的生成 / 审计 / import 改写脚本。
---

## 模块矩阵

13 个独立发版的 Go 模块，按**框架耦合度**分四层。tier N 不得依赖 tier > N。

<DependencyGraph />

<!--@include: ./parts/matrix-table.md-->

::: warning 别引门面仓
安装一律用上表的模块路径。**不要引门面仓 [`oagentkit/agentkit`](https://github.com/oagentkit/agentkit)** ——
它只是原单仓的 re-export 兼容层（转发包集合已冻结，零逻辑转发），按 README 写死的期限在 v1.x 后退役。
:::

## 基建

| 仓 | 作用 |
| --- | --- |
| [`.github`](https://github.com/oagentkit/.github) | org profile + 全 org 共享 CI 门禁（reusable workflow） |
| [`matrix-tools`](https://github.com/oagentkit/matrix-tools) | 版本矩阵生成 / 依赖方向审计 / import 改写 / 建仓 |
| [`versions.json`](https://oagentkit.github.io/versions.json) | 机器可读版本矩阵（由 `matrix-tools/scripts/gen_versions.py` 生成） |
| [`llms.txt`](https://oagentkit.github.io/llms.txt) | LLM 模块索引，旧→新包路径映射 |

## 与 oekit 的关系

oagentkit 与 [oekit](https://oekit.github.io)（Open Easy Kit，Go 微服务工具链）是**两套独立矩阵**，
不是子品牌。两者只共享 `o` / `kit` 元素。

oagentkit **依赖** oekit 的三个包：

- `github.com/oekit/pkg` — 微工具集（errors / stringx / encoding / mathx）
- `github.com/oekit/concurrency` — goroutine 池 / 单飞 / 重试 / 令牌桶 / 滑动窗口 / 时间轮
- `github.com/oekit/logx` — 日志门面

反过来不成立。要看微服务侧的 24 个模块怎么分层，直接去
[oekit 文档站](https://oekit.github.io)或它的[架构总览](https://oekit.github.io/about/architecture.html)。

**[姊妹项目详解 →](/guide/oekit)** —— 两套矩阵的定位对比、依赖边界、24 模块分层与易混点。

::: tip 撞名提醒
按包名对齐会做错。两边都有 `progress` 和 `breaker`，但语义相反或不同族——
`oekit/concurrency/progress` 是长任务**阶段进度追踪器**，
`oagentkit/runtime/progress` 是泛型**事件总线**。详见[架构总览](/guide/architecture)。
:::
