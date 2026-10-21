# guardx

安全围栏——凭据脱敏/URL 出口 SSRF 防护/工具许可判定链/提示注入卫生（tier0 零外部依赖底座）

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 0 · 基础层（零仓内依赖或仅依赖同仓包） |
| oekit 对应 | `core` |
| 仓内依赖 | —（零仓内依赖） |
| 被依赖 | `obs`、`skillkit`、`toolgate`、`tools` |
| 第三方地板 | 零 |
| 包数 | 9 |

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
| `injectband` | 系统带外注入的防伪包裹通道：给系统提示打来源标记，并转义 body 内伪造的同形标签（含大小写/空白变体），防身份伪造。与 fence 互补——fence 封数据侧越权，injectband 封系统侧伪造 |
| `invoke` | 工具调用统一契约 + 不可绕过的调用链（构造即保证）；框架无关，不携带 eino / policy 类型 |
| `toolfail` | 工具调用失败的分类与处置契约：类别 → 可重试性/退避/需人工/重发安全/面向模型的处置指引。不可分类即不可重试；重发安全与重试价值是两个正交维度 |
| `sandbox` | 执行沙箱的档位语义与后端协议：Level（none/process/os/machine，序即强弱）+ Provider + Registry。要求档位是下限，选不到满足者即拒绝、绝不降级 |
| `wire` | 跨进程调用协议：帧格式（4B 大端长度 + JSON 负载，不用行分隔——工具输出可能含换行）+ 两条通道（启动通道 Starter/Runner 一次执行、调用通道 Server/Client N 次工具调用）；失败分类跨进程同源（取 toolfail 的分类）、预算权威在父侧、在途调用有硬上限、取消传播靠管道关闭 |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

### 安全语义不可弱化（本仓的全部价值所在）

- **`egress`** —— 任何由 LLM 决定的 URL 出站前必须过判定。**不得新增「信任 LLM 给出的 URL」这类豁免分支** —— 那是提示词注入的直接落点。
- **`permgate`** —— 判定默认值必须是**拒绝**，白名单显式开。不得用「未配置即放行」。
- **`bashguard`** —— 静态解析不执行。**不得改成 exec 执行后再判断**。
- **`fence`** —— 任何把 LLM 产出或用户输入拼进 prompt 的路径都必须过 `EscapeUntrusted`，不得为可读性绕过。
- **`toolfail`** —— **不可分类 = 不可重试**（保守缺省）：判据缺失时两种误判成本不对称，误判可重试会把一次失败放大成 N 次，还可能重复施加副作用。**重发安全与重试价值是两个正交维度**：超时值得重试但服务端可能已执行，原样重发即重复施加副作用——只看「可重试」的调用方必然在这两种误判里选一个。
- **`sandbox`** —— **选不到满足档位的后端即拒绝，绝不降级**：降级会让「宿主声明的强度」与「实际执行的强度」之间没有信号，档位整套机制就成了装饰。**档位序即强弱**，要求档位是下限，满足下限者取最弱（够用且最省）。
- 安全相关路径**禁止吞 error** —— 判定失败必须阻断而非放行。
- **本仓必须保持零外部依赖**（go.mod 的 require 段为空）。Go 的依赖面按 **module** 结算：只 import logredact 的下游，模块图里也会多出本仓的整条 require。带重依赖的能力属于重仓——`audit` 已迁至 `obs/audit`（依赖 oekit/logx），`bashguard` 已迁至 `tools/bashguard`（依赖 mvdan.cc/sh）。
- **`audit` / `bashguard` 已迁出**（v0.7.0）：`github.com/oagentkit/guardx/audit` → `github.com/oagentkit/obs/audit`，`github.com/oagentkit/guardx/bashguard` → `github.com/oagentkit/tools/bashguard`。旧路径的嵌套 module tag 仍在但**已冻结**，不再有后续版本。
- **`invoke` 自 `toolgate/invoke` 迁入**（v0.8.0）：它自身只 import `oekit/pkg/errors`，却在 eino 重仓里让消费方白吃 34 个第三方模块。框架无关的原语属于零依赖底座。
- **`wire`** —— 跨进程调用协议。**两条通道必须是两条连接**（共用一条则「这帧是 Start 还是 Response」只能靠猜，两者 JSON 形状不同，猜错就是「字段读成了另一个意思」）。**失败分类不得退化成自由字符串**（父侧要靠它分「可重试」与「永久拒绝」）。**取消传播靠管道关闭**——管道关闭本身就是最强的取消信号，不需要单独的取消帧。

## 日志约定

- 本仓**不引日志依赖**（tier 0 零外部依赖底座）。审计留痕在 `github.com/oagentkit/obs/audit`（那里引 logx）。
- 日志必须经 `logredact` 打码后再落，**不得直接打印原始载荷**。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [工具接入与治理](/guide/tools-and-mcp.html)
