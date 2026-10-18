---
title: 快速开始
---

# 快速开始

## 安装

按需装单个模块，不要整包引入。矩阵的价值就在**只为你真正用的能力付依赖代价**。

```bash
go get github.com/oagentkit/llm@latest        # 模型客户端（tier 2）
go get github.com/oagentkit/agent@latest      # Agent 编排（tier 3）
go get github.com/oagentkit/mcpkit@latest    # MCP 工具池（tier 1）
```

装 `agent`（tier 3）会自动拉上 `llm` + `textx`，链路到此为止——**不会**把 eino 之外的
无关地板带进来。tier 分层就是干这个的。

::: danger 不要引门面仓
```go
import "git.enjoye.top/enjoydream/agentkit/agentrun"  // ❌ 原单仓路径
import "github.com/oagentkit/agent/agentrun"          // ✅ 拆分后
```

门面仓 [`oagentkit/agentkit`](https://github.com/oagentkit/agentkit) 只是 re-export 兼容层，
45 包零逻辑转发，按 README 写死的期限在 **v1.x 后退役**。新代码一律用上表的模块路径。

::: danger import 路径不是纯前缀映射
从旧单仓迁移时，**中间层目录会被丢掉**：

```
新路径 = github.com/oagentkit/{仓名}/{包名末段}

agentkit/knowledge/rag   →  oagentkit/rag/rag       ❌ 不是 rag/knowledge/rag
agentkit/worker/pglease  →  oagentkit/queue/pglease  ❌ 不是 queue/worker/pglease
agentkit/llm             →  oagentkit/llm/llm       ❌ 不能省掉末尾一段
```

完整 45 条对照跑 `rewrite_imports.py --print-rules`，机器可读映射见
[`versions.json`](https://oagentkit.github.io/versions.json) 的 `fromLegacy` 字段。
:::
:::

## 按需求选模块

| 你要做的事 | 装这个 | 层 |
| --- | --- | --- |
| 调模型、降级、控预算、算成本 | [`llm`](/modules/llm) | tier 2 |
| ReAct / 反思 / 路由 / 多专家协作 | [`agent`](/modules/agent) | tier 3 |
| 接 MCP server、拿工具目录 | [`mcpkit`](/modules/mcpkit) | tier 1 |
| 治理工具优先级、并发调度、敏感操作审计 | [`toolgate`](/modules/toolgate) | tier 2 |
| 组装 system prompt、运行中转向 | [`promptx`](/modules/promptx) | tier 1 |
| token 用量、trace、分阶段打标 | [`obs`](/modules/obs) | tier 1 |
| 脱敏、SSRF 防护、Shell 沙箱解析 | [`guardx`](/modules/guardx) | tier 0 |
| 会话压缩、diff 解析、代码符号索引 | [`textx`](/modules/textx) | tier 0 |
| 事件总线、流控、子进程、热插拔、钩子 | [`runtime`](/modules/runtime) | tier 0 |
| 任务队列、主备选主 | [`queue`](/modules/queue) | tier 0 |

完整 13 个模块见[模块总览](/modules/)。

## 矩阵通用规约

这几条在**每个仓的 `AGENTS.md` 里都写着**，先记住能少踩一半坑：

**错误处理** —— 一律用 `github.com/oekit/pkg/errors`，业务错误用 `BizError`：

```go
import "github.com/oekit/pkg/errors"

if err := doIt(); err != nil {
    return errors.WrapBiz(err, "解析用户输入失败")
}
```

所有 error 禁止 `_` 忽略。

**并发** —— 禁止裸 `go func`，用 `oekit/concurrency/async` 的 `GoSafe` 系列（panic 会被 recover）：

```go
import "github.com/oekit/concurrency/async"

async.GoSafe(func() { /* ... */ })   // ✅ panic 被兜住
// go func() { /* ... */ }()          // ❌ 一个 panic 带走整个进程
```

共享状态用 mutex / atomic 保护；包级全局可变状态用 `atomic.Pointer[T]`。

**API 命名** —— 函数选项模式命名 `XxxOption`，禁止裸 `Option`（多包 co-import 会冲突）：

```go
type ModelOption func(*modelConfig)   // ✅ 带仓/包前缀
// type Option func(*cfg)             // ❌ 冲突
```

导出符号 PascalCase + godoc 注释，包文档放 `doc.go`。

**日志** —— 走 `oekit/logx`，组件 logger 用 `logx.Delegating`：

```go
logger := logx.Delegating("oagentkit-agent")
```

面向用户的最终输出落日志前要过 `guardx/fence` 的不可信文本中和。

## 查 API

不确定就以源码为准。各仓都带测试，`go doc` 可查：

```bash
go doc github.com/oagentkit/llm
go doc github.com/oagentkit/agent/dispatch
```

每个仓的 `AGENTS.md` 是该仓的**权威规范**——本站的模块页只是摘要，不替代它。

## 下一步

- [架构总览](/guide/architecture) —— 分层不变量、依赖方向、跨矩阵撞名
- [AI Agent 编排](/guide/ai-agent) —— 从零搭一个带守卫的 Agent
