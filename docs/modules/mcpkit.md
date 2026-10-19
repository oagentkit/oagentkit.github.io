# mcpkit

MCP 工具池——客户端封装/工具目录/建连单飞/自愈与租约管理

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 2 · 集成层（依赖 tier 0/1 + 重第三方地板） |
| oekit 对应 | `registry` |
| 仓内依赖 | `runtime` |
| 被依赖 | `toolgate` |
| 第三方地板 | `github.com/mark3labs/mcp-go`、`github.com/eino-contrib/jsonschema`、`github.com/cloudwego/eino` |
| 包数 | 1 |

## 安装

```bash
go get github.com/oagentkit/mcpkit@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/mcpkit](https://github.com/oagentkit/mcpkit)

## 包

| 包 | 说明 |
| --- | --- |
| `mcp` | MCP 客户端/工具池：工具目录、建连单飞、自愈与租约管理 |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

- **建连必须单飞。** 同一 server 的并发建连要合并为一次，
  不得每次 `Allow` 都新建连接。
- **等待方的 ctx 取消要各自生效**，不能干等 leader。
- 工具注解（`mcp.ToolAnnotation`）归一时，`nil` 视为规范缺省，**不得当成「无限制」**。
- **层位 t1 → t2**：带 `eino` + `mcp-go` 地板（MCP 客户端本身绑框架）——属集成层。重定位后 tier0/tier1 = 零重量级第三方地板的层（可被零依赖核心安全依赖）。

## 日志约定

- **本仓不引入日志依赖。** tier0 加日志等于给所有下游抬地板；需要观测输出时返回 error 或交给调用方。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [工具接入与治理](/guide/tools-and-mcp.html)
