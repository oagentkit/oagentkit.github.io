# guardx

安全围栏——凭据脱敏/URL 出口 SSRF 防护/工具许可判定链/Shell 沙箱解析/审计日志

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 0 · 基础层（零仓内依赖或仅依赖同仓包） |
| oekit 对应 | `core` |
| 仓内依赖 | —（零仓内依赖） |
| 被依赖 | `skillkit`、`tools` |
| 第三方地板 | 零 |
| 包数 | 7 |

## 安装

```bash
go get github.com/oagentkit/guardx@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/guardx](https://github.com/oagentkit/guardx)

## 包

| 包 | 说明 |
| --- | --- |
| `fence` | 中和不可信文本（LLM 产出、用户输入）中的 markdown 结构，防提示词注入 |
| `logredact` | 日志/审计载荷凭据脱敏：连接串/URL/头中的凭据落盘前打码 |
| `egress` | 出口围栏：LLM 可控 URL 的字面量层 SSRF 防护 |
| `permgate` | 工具调用许可判定链：谁在什么模式下对什么输入得到什么许可 |
| `bashguard` | bash 命令静态风险解析：不执行命令，经真 shell AST 判定 |
| `audit` | 审计日志：对敏感操作留结构化审计痕迹，与业务日志分离 |
| `injectband` | 系统带外注入的防伪包裹通道：给系统提示打来源标记，并转义 body 内伪造的同形标签（含大小写/空白变体），防身份伪造。与 fence 互补——fence 封数据侧越权，injectband 封系统侧伪造 |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

### 安全语义不可弱化（本仓的全部价值所在）

- **`egress`** —— 任何由 LLM 决定的 URL 出站前必须过判定。**不得新增「信任 LLM 给出的 URL」这类豁免分支** —— 那是提示词注入的直接落点。
- **`permgate`** —— 判定默认值必须是**拒绝**，白名单显式开。不得用「未配置即放行」。
- **`bashguard`** —— 静态解析不执行。**不得改成 exec 执行后再判断**。
- **`fence`** —— 任何把 LLM 产出或用户输入拼进 prompt 的路径都必须过 `EscapeUntrusted`，不得为可读性绕过。
- 安全相关路径**禁止吞 error** —— 判定失败必须阻断而非放行。
- `audit` 的 `log` 为 nil 时回退 `logx.NewAuditLogger`（级别锁 `Info`、不受 `LOG_LEVEL` 降级）——
  这是刻意设计，别改回普通 logger。
- **本仓含 3 个 Go module**：主模块（fence/injectband/logredact/egress/permgate，**零外部依赖**） + 两个嵌套子模块 `guardx/audit`（依赖 oekit/logx）与 `guardx/bashguard`（依赖 mvdan.cc/sh）。import 路径不变，但**版本线独立**（嵌套模块各自打 `audit/vX.Y.Z` / `bashguard/vX.Y.Z` tag）。 主模块必须保持零外部依赖——import logredact 不该把第三方库拖进下游的模块图。

## 日志约定

- 本仓是矩阵里**允许依赖 `oekit/logx` 的仓**（审计与脱敏需要）。
- 日志必须经 `logredact` 打码后再落，**不得直接打印原始载荷**。
- 审计走 `audit.New(log, service)`；`log` 为 nil 时回退 `logx.NewAuditLogger`
  （级别锁 `Info`、不受 `LOG_LEVEL` 降级 —— 刻意设计）。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [工具接入与治理](/guide/tools-and-mcp.html)
