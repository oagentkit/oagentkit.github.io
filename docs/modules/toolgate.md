# toolgate

工具治理——优先级三层约束/注解驱动并发调度/操作审计门/构造期不可绕过的工具调用链

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 2 · 集成层（依赖 tier 0/1 + 重第三方地板） |
| oekit 对应 | `middleware` |
| 仓内依赖 | `mcpkit` |
| 被依赖 | —（矩阵叶子） |
| 第三方地板 | `github.com/cloudwego/eino`、`gopkg.in/yaml.v3` |
| 包数 | 4 |

## 安装

```bash
go get github.com/oagentkit/toolgate@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/toolgate](https://github.com/oagentkit/toolgate)

## 包

| 包 | 说明 |
| --- | --- |
| `toolprior` | 工具优先级三层约束（收紧语义，下层已设的限制不得放宽） |
| `toolsched` | 注解驱动的工具并发调度与去重 |
| `policy` | 操作审计门：敏感工具调用的策略判定 |
| `invoke` | 不可绕过的工具调用链：门禁由**构造**保证而非调用点自觉——Handler 按值收进私有字段，绕过链的代码在类型层面就写不出来 |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

- 优先级三层约束是**收紧**语义：上层只能进一步限制，**不得放宽**下层已设的限制。
- 并发调度的去重键必须包含全部影响结果的参数，否则会错误合并不等价调用。

## 日志约定

- 日志走 `oekit/logx`，组件 logger 用 `logx.Delegating("oagentkit-toolgate")`。
- 被拒的工具调用属审计事件，字段需带工具名、调用者、拒绝原因。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [AI Agent 编排](/guide/ai-agent.html)
- [工具接入与治理](/guide/tools-and-mcp.html)
