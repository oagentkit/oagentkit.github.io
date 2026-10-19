| 模块 | 层 | 说明 | 仓内依赖 |
| --- | --- | --- | --- |
| [`guardx`](/modules/guardx.html) | <span class="matrix-tier">tier 0</span> | 安全围栏——凭据脱敏/URL 出口 SSRF 防护/工具许可判定链/提示注入卫生（tier0 零外部依赖底座） | <span class="matrix-tier">—</span> |
| [`queue`](/modules/queue.html) | <span class="matrix-tier">tier 0</span> | DB 即队列 + Postgres Lease 选主——任务表驱动的工作池与主备单活回调 | <span class="matrix-tier">—</span> |
| [`runtime`](/modules/runtime.html) | <span class="matrix-tier">tier 0</span> | Agent 进程运行时——LLM token 流式节控/泛型事件总线/子进程最小环境/运行时热插拔/生命周期钩子 | <span class="matrix-tier">—</span> |
| [`textx`](/modules/textx.html) | <span class="matrix-tier">tier 0</span> | 文本与差异处理——增量切片/unified diff 解析/代码符号索引/会话滚动窗口与压缩/评审报告指纹 | <span class="matrix-tier">—</span> |
| [`mcpkit`](/modules/mcpkit.html) | <span class="matrix-tier">tier 1</span> | MCP 工具池——客户端封装/工具目录/建连单飞/自愈与租约管理 | <span class="matrix-tier">`runtime`</span> |
| [`obs`](/modules/obs.html) | <span class="matrix-tier">tier 1</span> | LLM 可观测与审计——eino callbacks 埋点/token 用量采集/分阶段打标/Langfuse 追踪客户端/敏感操作结构化审计 | <span class="matrix-tier">`guardx`、`textx`</span> |
| [`promptx`](/modules/promptx.html) | <span class="matrix-tier">tier 1</span> | 提示词上下文——system prompt 分段组装/运行中转向队列/文件读后写一致性状态 | <span class="matrix-tier">`runtime`、`textx`</span> |
| [`rag`](/modules/rag.html) | <span class="matrix-tier">tier 1</span> | 知识检索——向量化/混合召回/重排，向量后端可插拔 | <span class="matrix-tier">`textx`</span> |
| [`skillkit`](/modules/skillkit.html) | <span class="matrix-tier">tier 1</span> | 技能与资产契约——SKILL.md 渐进披露/领域包布局契约/装配血缘图 | <span class="matrix-tier">`textx`、`guardx`</span> |
| [`llm`](/modules/llm.html) | <span class="matrix-tier">tier 2</span> | 模型客户端——多模型降级链/任务级预算/成本记账/分阶段模型路由/主备切换 | <span class="matrix-tier">`textx`、`obs`、`runtime`</span> |
| [`toolgate`](/modules/toolgate.html) | <span class="matrix-tier">tier 2</span> | 工具治理——优先级三层约束/注解驱动并发调度/操作审计门/构造期不可绕过的工具调用链 | <span class="matrix-tier">`mcpkit`</span> |
| [`tools`](/modules/tools.html) | <span class="matrix-tier">tier 2</span> | 外部工具接入——CLI 编码 agent 统一调用/公开资料检索/git 工作副本沙箱/确定性 SAST 扫描/Shell 命令静态裁决 | <span class="matrix-tier">`textx`、`runtime`、`guardx`</span> |
| [`agent`](/modules/agent.html) | <span class="matrix-tier">tier 3</span> | Agent 编排——ReAct 运行样板/计划先行/反思循环/意图路由/多专家黑板/派发守卫 | <span class="matrix-tier">`llm`、`textx`</span> |
