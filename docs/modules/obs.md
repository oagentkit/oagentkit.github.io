# obs

敏感操作审计——结构化审计留痕，字段值统一经 logredact 打码（不引 eino 框架）

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 2 · 集成层（依赖 tier 0/1 + 重第三方地板） |
| oekit 对应 | `metrics` |
| 仓内依赖 | `guardx` |
| 被依赖 | —（矩阵叶子） |
| 第三方地板 | 零 |
| 包数 | 1 |

## 安装

```bash
go get github.com/oagentkit/obs@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/obs](https://github.com/oagentkit/obs)

## 包

| 包 | 说明 |
| --- | --- |
| `audit` | 敏感操作的结构化审计留痕（自 guardx/audit 迁入）：字段值统一经 logredact 打码 |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

### 定位（v0.10.0 起）：audit 单包仓

本仓只剩 `audit` 一个包：**执行面的操作留痕**（谁做了什么、参数是什么、结果如何），
字段值统一经 `guardx/logredact` 打码。

- **Langfuse 只读客户端已迁往 `llm/obsx`**（读写同域，oagentkit/obs#129）：
  观测/追踪侧的能力（eino callbacks 适配、OTel generation 发射出口）本就在 llm 仓的
  `obsx`，读端并入后「Langfuse 上有什么、是谁写进去的」一处答全。本仓不再承担观测面。
- **同层依赖禁令**：`obs` 与 `llm` 同为 tier 2 ⇒ `obs` 不得依赖 `llm` ⇒ 本仓**不能**
  留一个转发到 `llm/obsx` 的兼容壳 ⇒ `langfuse` 直接删除，下游改 import 路径。
- `audit` 自 `guardx/audit` 迁入（v0.8.0）：它依赖 `oekit/logx`，而 guardx 是 tier 0
  零依赖底层，依赖面按 module 结算。包名与职责不变，只是 import 路径变了。
- **层位仍为 tier 2**：层位标签的原始理由（带 `eino` 地板）随 langfuse 迁出已不成立，
  但层位是**声明面**（仓内 AGENTS.md / README.md 与 modules.json 必须一致），
  改层位是独立决策，不在本仓降级动作内顺带做。

## 日志约定

- 日志走 `oekit/logx`，组件 logger 用 `logx.Delegating("oagentkit-obs")`。
- **观测数据不得携带凭据原文**，落盘前过 `guardx/logredact`。
- `audit` 包的 logger 为 nil 时回退 `logx.NewAuditLogger`（级别锁 `Info`、不受 `LOG_LEVEL` 降级、SetLevel 到 WARN/ERROR 被拒）—— 这是刻意设计，别改回普通 logger。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [模型调用与路由](/guide/llm-routing.html)
- [可观测](/guide/observability.html)
