| 模块 | 层 | 说明 | 仓内依赖 |
| --- | --- | --- | --- |
| [`guardx`](/modules/guardx.html) | <span class="matrix-tier">tier 0</span> | 安全围栏——凭据脱敏/URL 出口 SSRF 防护/工具许可判定链/提示注入卫生（tier0 零外部依赖底座） | <span class="matrix-tier">—</span> |
| [`runtime`](/modules/runtime.html) | <span class="matrix-tier">tier 0</span> | Agent 进程运行时——LLM token 流式节控/泛型事件总线/子进程最小环境/运行时热插拔/生命周期钩子 | <span class="matrix-tier">—</span> |
| [`textx`](/modules/textx.html) | <span class="matrix-tier">tier 0</span> | 文本与差异处理——增量切片/unified diff 解析/代码符号索引/会话滚动窗口与压缩/评审报告指纹 | <span class="matrix-tier">—</span> |
| [`toolname`](/modules/toolname.html) | <span class="matrix-tier">tier 0</span> | 工具名净化原语——工具名→程序内标识符的单一真相（JS 标识符判定 + 规整），装配两侧必须逐字一致 | <span class="matrix-tier">—</span> |
| [`promptx`](/modules/promptx.html) | <span class="matrix-tier">tier 1</span> | 提示词上下文——system prompt 分段组装/运行中转向队列/文件读后写一致性状态 | <span class="matrix-tier">`textx`、`guardx`</span> |
| [`llm`](/modules/llm.html) | <span class="matrix-tier">tier 2</span> | 模型客户端——多模型降级链/任务级预算/成本记账/分阶段路由/LLM 调用观测 | <span class="matrix-tier">`textx`</span> |
| [`mcpkit`](/modules/mcpkit.html) | <span class="matrix-tier">tier 2</span> | MCP 工具池——客户端封装/工具目录/建连单飞/自愈与租约管理 | <span class="matrix-tier">—</span> |
| [`obs`](/modules/obs.html) | <span class="matrix-tier">tier 2</span> | 敏感操作审计——结构化审计留痕，字段值统一经 logredact 打码（不引 eino 框架） | <span class="matrix-tier">`guardx`</span> |
| [`queue`](/modules/queue.html) | <span class="matrix-tier">tier 2</span> | DB 即队列 + Postgres Lease 选主——任务表驱动的工作池与主备单活回调 | <span class="matrix-tier">—</span> |
| [`rag`](/modules/rag.html) | <span class="matrix-tier">tier 2</span> | 知识检索与本体层——向量化/混合召回/重排（向量后端可插拔，独立子包隔离 sdk 地板）+ 实体关系本体契约与判据 | <span class="matrix-tier">`textx`</span> |
| [`skillkit`](/modules/skillkit.html) | <span class="matrix-tier">tier 2</span> | 技能与资产契约——SKILL.md 渐进披露/领域包布局契约/装配血缘图 | <span class="matrix-tier">`textx`、`guardx`</span> |
| [`toolgate`](/modules/toolgate.html) | <span class="matrix-tier">tier 2</span> | 工具治理——优先级三层约束/注解驱动并发调度/操作审计门/构造期不可绕过的工具调用链 | <span class="matrix-tier">`guardx`、`mcpkit`</span> |
| [`tools`](/modules/tools.html) | <span class="matrix-tier">tier 2</span> | 外部工具接入——CLI 编码 agent 统一调用/公开资料检索/git 工作副本沙箱/确定性 SAST 扫描/Shell 命令静态裁决 | <span class="matrix-tier">`textx`、`guardx`</span> |
| [`agent`](/modules/agent.html) | <span class="matrix-tier">tier 3</span> | Agent 编排——ReAct 运行样板/计划先行/反思循环/意图路由/多专家黑板/派发守卫 | <span class="matrix-tier">`llm`、`textx`</span> |
| [`goagent-kernel`](/modules/goagent-kernel.html) | <span class="matrix-tier">tier 4</span> | 多智能体编排通用内核：编排是代码，LLM 只做单环节——确定性编排的机制面（报告协议/状态机/事件总线/副作用闸/续跑契约/介入面），不认识任何领域概念 | <span class="matrix-tier">`guardx`、`runtime`、`toolgate`、`toolname`</span> |
| [`goagent-runtime`](/modules/goagent-runtime.html) | <span class="matrix-tier">tier 5</span> | Agent 运行时装配层：把 goagent-kernel 的确定性机制装配成业务方可直接用的 runtime（Loop/Pipeline/存储/事件接线与默认口径） | <span class="matrix-tier">`agent`、`goagent-kernel`、`guardx`</span> |
