# goagent-runtime

Agent 运行时装配层：把 goagent-kernel 的确定性机制装配成业务方可直接用的 runtime（Loop/Pipeline/存储/事件接线与默认口径）

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 5 · 装配层（依赖 goagent-kernel + agent，只接线不另写判据） |
| oekit 对应 | `bootstrap` |
| 仓内依赖 | `agent`、`goagent-kernel`、`guardx` |
| 被依赖 | —（矩阵叶子） |
| 第三方地板 | `github.com/jackc/pgx/v5`、`modernc.org/sqlite` |
| 包数 | 14 |

## 安装

```bash
go get github.com/yi-nology/goagent-runtime@latest
```

源码与该仓 `AGENTS.md`：[yi-nology/goagent-runtime](github.com/yi-nology/goagent-runtime)

## 包

| 包 | 说明 |
| --- | --- |
| `chat` | 供应商中立模型窄接口（单方法非流式契约保底 + Delta 流式承载 + DeltaAggregator 归并器） |
| `pipeline` | 工具注册与副作用施加映射（幂等键/资源互斥/重试安全声明 → kernel sideeffect） |
| `agentloop` | 可恢复回合循环：预算→模型→审批→施加→Joint 联合提交→账本续跑 |
| `adjudicate` | 副作用未知态的周期裁决框架（枚举→grace→Resolver 链→kernel Runner.Reconcile） |
| `storage` | 存储判据面 Provider 聚合契约 + 内存实现（零驱动边） |
| `storage/sqlitestore` | standalone 形态 SQLite Provider 绑定（驱动边只在此包） |
| `sqliteadapter` | SQLite(WAL) 参考实现：11 面统一门面（kernel 契约套件同源） |
| `pgstore` | PostgreSQL 参考实现：11 面统一门面 + Outbox 事件面 + SIGKILL 故障恢复 e2e |
| `runtime` | 模板装配（NewEmbedded 内存 / NewStandalone SQLite） |
| `cluster` | 多副本模板装配（PG + worker 池：认领/租约/接管代次/跨副本事件面） |
| `observe` | eventbus → 宿主回调薄适配 |
| `containerbackend` | 容器执行后端参考实现（Docker/K8s Job）——宿主抄它不 import 它 |
| `bridge/llmchat` | 钦定适配器：oagentkit/llm → chat.Model（嵌套模块，LLM SDK 边只在 bridge） |
| `bridge/einotool` | 钦定适配器：eino InvokableTool → pipeline.Tool（副作用闸字段不猜） |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

### 判据单源纪律（ADR-0001/0002）

- 判据全部来自 goagent-kernel 契约（sideeffect/taskboard/checkpoint/roundguard/eventbus），本仓**只做接线不另写第二套**：三套副作用闸实现（storage 内存/sqliteadapter/pgstore）都跑 kernel `sidetest` 共享套件。
- **驱动边分包**：`storage` 纯判据零驱动（scripts/check-dep-edges.sh 门禁）；驱动只落在 sqliteadapter/pgstore。
- **LLM SDK 边嵌套模块**：`bridge`（独立 go.mod）承载 llm/eino 适配器（llmchat/einotool），主 module 零 LLM SDK import（ADR-0003）；不用 bridge 的宿主依赖图里没有 eino。
- 命名消歧：`oagentkit/runtime`（tier 0）是家族生命周期原语仓（hookx/hotplug/notifyx/pacer/progress）；本仓是装配层，`goagent-` 前缀即家族装配层约定。
- 发版纯 git tag；2026-11-26 归属回迁：oagentkit → yi-nology org（v0.8.0 起；v0.7.0-v0.7.1 的 oagentkit tag 只能经 oagentkit 路径消费）。

## 日志约定

- 日志走 `oekit/logx`；loop/cluster 的关键事件（审批挂起/接管/对账）经 `eventbus` 发结构化事件。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
