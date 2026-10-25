# 模块总览

oagentkit 是 **13 个独立发版的 Go 模块**，依赖严格自底向上，每仓独立 SemVer + 独立 CI。

> 每个仓库根目录都有 `AGENTS.md` —— 面向 AI Agent 的权威规范与硬规则。

## tier 0 · 基础层

*零仓内依赖或仅依赖同仓包*

| 模块 | 说明 | 仓内依赖 |
| --- | --- | --- |
| [`guardx`](/modules/guardx.html) | 脱敏/出口围栏/权限判定/沙箱档位/跨进程协议 | <span class="matrix-tier">—</span> |
| [`runtime`](/modules/runtime.html) | agent 进程运行时——流式节控/泛型事件总线/子进程环境/热插拔/钩子 | <span class="matrix-tier">—</span> |
| [`textx`](/modules/textx.html) | 文本/差异/会话/报告纯函数集 | <span class="matrix-tier">—</span> |

## tier 1 · 能力层

*依赖 tier 0*

| 模块 | 说明 | 仓内依赖 |
| --- | --- | --- |
| [`promptx`](/modules/promptx.html) | system prompt 分段组装/运行中转向/文件读后写一致性 | <span class="matrix-tier">`runtime`、`textx`</span> |

## tier 2 · 集成层

*依赖 tier 0/1 + 重第三方地板*

| 模块 | 说明 | 仓内依赖 |
| --- | --- | --- |
| [`llm`](/modules/llm.html) | 模型客户端/降级链/预算/成本/阶段路由/调用观测 | <span class="matrix-tier">`textx`</span> |
| [`mcpkit`](/modules/mcpkit.html) | MCP 客户端/工具池/建连单飞 | <span class="matrix-tier">`runtime`</span> |
| [`obs`](/modules/obs.html) | 观测客户端 + 审计留痕 | <span class="matrix-tier">`guardx`</span> |
| [`queue`](/modules/queue.html) | DB 即队列 + Postgres 选主 Lease | <span class="matrix-tier">—</span> |
| [`rag`](/modules/rag.html) | 知识检索——向量化/混合召回/重排 | <span class="matrix-tier">`textx`</span> |
| [`skillkit`](/modules/skillkit.html) | SKILL.md 渐进披露 + 领域包契约 + 装配血缘 | <span class="matrix-tier">`textx`、`guardx`</span> |
| [`toolgate`](/modules/toolgate.html) | 工具优先级/并发调度/操作审计门/不可绕过的调用链 | <span class="matrix-tier">`guardx`、`mcpkit`</span> |
| [`tools`](/modules/tools.html) | CLI 编码 agent 统一调用/公开检索/git 沙箱/SAST 扫描/Shell 静态裁决 | <span class="matrix-tier">`textx`、`runtime`、`guardx`</span> |

## tier 3 · 编排层

*依赖 llm 等 tier 2 门面*

| 模块 | 说明 | 仓内依赖 |
| --- | --- | --- |
| [`agent`](/modules/agent.html) | ReAct 运行样板/反思循环/意图路由/多专家黑板/派发守卫/澄清 | <span class="matrix-tier">`llm`、`textx`</span> |

## 基建仓

| 仓 | 角色 |
| --- | --- |
| [`agentkit`](https://github.com/oagentkit/agentkit) | 门面仓——46 包 re-export 零逻辑，发 v1.0.0 后按 README 写死的期限退役 |
| [`.github`](https://github.com/oagentkit/.github) | org profile + 共享 reusable workflow（照抄 oekit/.github，改 org 与域名） |
| [`matrix-tools`](https://github.com/oagentkit/matrix-tools) | 版本矩阵生成/审计/巡检（照抄 oekit/matrix-tools：gen_versions.py、ekit2oekit.py 同源思路） |
| [`oagentkit.github.io`](https://github.com/oagentkit/oagentkit.github.io) | llms.txt 模块索引 + 文档站点 |

## 过渡期兼容镜像：llm/llm

`llm/llm` 是 `llm` 仓的**过渡期兼容镜像**——把根包的导出符号镜像过来（类型别名 / 函数转发 / 常量转发），**不含任何自己的实现**，只为存量下游存在。

- 实现：llm/llm/compat.go —— 镜像根包全部 71 个导出符号（31 type / 31 func / 2 var / 7 const）；类型用 type 别名、函数用 var 转发、常量原样转发，一致性由 llm/llm/compat_test.go 的 AST 比对强制
- 可用 import 路径：`github.com/oagentkit/llm/llm`（llm v0.18.0 起）
- 规范路径：`github.com/oagentkit/llm` —— 矩阵的规范包清单只登记它
- 不进规范包清单的原因：规范包清单的 import 路径规则把「包名末段 == 仓名」收口到 module 根（matrix_paths.new_import_path）；登记它会让 versions.json 给根包与它登记同一个 importPath
- 相关 issue（已关闭）：
  - [`#47`](https://github.com/oagentkit/llm/issues/47) —— 需求：llm/llm 扁平化后缺兼容子包 —— 跨大版本升级的下游需整仓改 import 路径（已关闭）
  - [`#48`](https://github.com/oagentkit/llm/issues/48) —— 实现：补 llm/llm 兼容层 —— 恢复 v0.7.0~v0.8.0 的历史 import 路径（已合入 llm v0.18.0）
- 状态：过渡期兼容镜像 —— 包是活的（v0.18.0 起可 import），只为存量下游存在
- 下一步：新代码一律直接 import github.com/oagentkit/llm；本镜像随 0.x 版本线退役

完整说明见 [`llm` 模块页](/modules/llm.html) 的「过渡期兼容镜像」段。

## 已退役的包：breaker

`breaker` 已从本矩阵移出，迁往 `github.com/oekit/concurrency/breaker`。**退役是分阶段完成的**——消费方先改依赖上游、上游能力补齐，最后才删包，任何一步提前做都是构建断裂。

- 消费方：llm/breaker.go —— 只做按模型名分桶 + 转发，不再有任何本地语义兜底
- 上游需求链（全部已关闭）：
  - [`#17`](https://github.com/oekit/concurrency/issues/17) —— 三态 + 代绑定 + 探测时限 —— 已落地 v0.9.0
  - [`#19`](https://github.com/oekit/concurrency/issues/19) —— 冷却期与探测时限解耦（WithCooldown）—— 已落地 v0.12.0
  - [`#20`](https://github.com/oekit/concurrency/issues/20) —— 计数型触发（WithConsecutiveFailures）—— 已落地 v0.12.0
  - [`#25`](https://github.com/oekit/concurrency/issues/25) —— 计数型只切状态、切不了放行决策 —— 已落地 v0.13.0，llm 侧兜底已删除
- 状态：已完成：llm v0.4.0 起全量使用上游 GenBreaker

退役完整时间线见 [`runtime` 模块页](/modules/runtime.html) 的「本仓硬规则」。

## 已移除的包

- `<root>` —— 仓根 integration_test.go 依赖全部包，拆分后无处安放

## 相关

- [快速开始](/guide/getting-started.html)
- [架构总览](/guide/architecture.html)
- [CI 门禁与模块规则](/guide/contributing.html)
