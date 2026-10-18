# 模块总览

oagentkit 是 **13 个独立发版的 Go 模块**，依赖严格自底向上，每仓独立 SemVer + 独立 CI。

> 每个仓库根目录都有 `AGENTS.md` —— 面向 AI Agent 的权威规范与硬规则。

## tier 0 · 基础层

*零仓内依赖或仅依赖同仓包*

| 模块 | 说明 | 仓内依赖 |
| --- | --- | --- |
| [`guardx`](/modules/guardx.html) | 脱敏/出口围栏/权限判定/沙箱解析/审计 | <span class="matrix-tier">—</span> |
| [`queue`](/modules/queue.html) | DB 即队列 + Postgres 选主 Lease | <span class="matrix-tier">—</span> |
| [`runtime`](/modules/runtime.html) | agent 进程运行时——流式节控/泛型事件总线/子进程环境/热插拔/钩子 | <span class="matrix-tier">—</span> |
| [`textx`](/modules/textx.html) | 文本/差异/会话/报告纯函数集 | <span class="matrix-tier">—</span> |

## tier 1 · 能力层

*依赖 tier 0*

| 模块 | 说明 | 仓内依赖 |
| --- | --- | --- |
| [`mcpkit`](/modules/mcpkit.html) | MCP 客户端/工具池/建连单飞 | <span class="matrix-tier">`runtime`</span> |
| [`obs`](/modules/obs.html) | 用量观测 + Langfuse 追踪 | <span class="matrix-tier">`textx`</span> |
| [`promptx`](/modules/promptx.html) | system prompt 分段组装/运行中转向/文件读后写一致性 | <span class="matrix-tier">`runtime`、`textx`</span> |
| [`rag`](/modules/rag.html) | 知识检索——向量化/混合召回/重排 | <span class="matrix-tier">`textx`</span> |
| [`skillkit`](/modules/skillkit.html) | SKILL.md 渐进披露 + 领域包契约 + 装配血缘 | <span class="matrix-tier">`guardx`、`textx`</span> |

## tier 2 · 集成层

*依赖 tier 0/1 + 重第三方地板*

| 模块 | 说明 | 仓内依赖 |
| --- | --- | --- |
| [`llm`](/modules/llm.html) | 模型客户端/降级链/预算/成本/阶段路由 | <span class="matrix-tier">`obs`、`runtime`、`textx`</span> |
| [`toolgate`](/modules/toolgate.html) | 工具优先级/并发调度/操作审计门 | <span class="matrix-tier">`mcpkit`</span> |
| [`tools`](/modules/tools.html) | CLI 编码 agent 统一调用/公开检索/git 沙箱/SAST 扫描 | <span class="matrix-tier">`guardx`、`runtime`、`textx`</span> |

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

## 已移除的包

- `<root>` —— 仓根 integration_test.go 依赖全部包，拆分后无处安放

## 相关

- [快速开始](/guide/getting-started.html)
- [架构总览](/guide/architecture.html)
- [CI 门禁与模块规则](/guide/contributing.html)
