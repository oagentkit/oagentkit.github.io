# queue

DB 即队列 + Postgres Lease 选主——任务表驱动的工作池与主备单活回调

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 0 · 基础层（零仓内依赖或仅依赖同仓包） |
| oekit 对应 | `k8s` |
| 仓内依赖 | —（零仓内依赖） |
| 被依赖 | —（矩阵叶子） |
| 第三方地板 | `github.com/lib/pq` |
| 包数 | 2 |

## 安装

```bash
go get github.com/oagentkit/queue@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/queue](https://github.com/oagentkit/queue)

## 包

| 包 | 说明 |
| --- | --- |
| `worker` | 任务表驱动的工作池（DB 即队列）+ `LeaseStore` 选主存储接口 |
| `worker/pglease` | `worker.LeaseStore` 的 PostgreSQL 实现（条件 UPSERT 一行即成） |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

### 选主语义（正确性红线）

- **`LeaseStore` 必须保证「同一时刻至多一个 leader」。** 条件 UPSERT 不能退化成「先查后写」——
  那是竞态，不是选主。
- 租约续期失败/进程失联后，其他实例**必须**能在租约过期后接管。
- 租约丢失属必须上报事件，`OnStoppedLeading` 要真的执行清理，不得静默吞 error。

### lib/pq 是测试依赖

`github.com/lib/pq` 仅用于 `pglease` 的 DSN 门控集成测试驱动，
**生产代码禁止 import**。仓内零生产依赖是刻意设计，不要引入。
集成测试在未设 `postgres://…` DSN 时自动跳过。

## 日志约定

- 日志走 `oekit/logx`，组件 logger 用 `logx.Delegating("oagentkit-queue")`，
  禁止 `Default()`/`WithService` 声明包级 logger。
- leader 变更、租约丢失属关键事件，kv 字段须带 lease 名与实例 id。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
