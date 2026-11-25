# goagent-kernel

多智能体编排通用内核：编排是代码，LLM 只做单环节——确定性编排的机制面（报告协议/状态机/事件总线/副作用闸/续跑契约/介入面），不认识任何领域概念

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 4 · 编排判据层（依赖 guardx/toolgate 等 tier 0~2，编排判据单源（ADR-0010）） |
| oekit 对应 | `workflow` |
| 仓内依赖 | `guardx`、`runtime`、`toolgate`、`toolname` |
| 被依赖 | `goagent-runtime` |
| 第三方地板 | `github.com/dop251/goja`、`github.com/santhosh-tekuri/jsonschema/v6`、`golang.org/x/tools` |
| 包数 | 46 |

## 安装

```bash
go get github.com/oagentkit/goagent-kernel@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/goagent-kernel](https://github.com/oagentkit/goagent-kernel)

## 包

| 包 | 说明 |
| --- | --- |
| `archcheck` | 架构门禁执行体（可被宿主复用：policy 声明面→逐条判定） |
| `backend` | 任务式执行后端契约（EgressEnforcer/Capable/Spec） |
| `checkpoint` | 编排续跑契约：进度快照 + CAS + 「续跑而非重放」恢复判定 |
| `commitgate` | 环节终态独占提交闸（凭令牌放闸/释放） |
| `contract` | 编排引擎↔宿主状态的唯一边界（纯接口面，零实现） |
| `controlplane` | 介入契约：任务查看/运行状态/失败诊断/人工介入 + Store 原子提交 |
| `coord` | Board/Store 适配形态约定（控制面/集群面共用） |
| `cost` | 运行成本治理口径面 |
| `deadline` | 会话级墙钟锚点（首轮认领写一次、续跑轮沿用） |
| `delegate` | 异构委托契约面 |
| `delta` | 增量节流的编排层：(kind,iteration) 键控 + 确定性收口（底座=runtime/pacer） |
| `dispatch` | 改派失败面：三档分类 + 两级判定 + 改派环（可达性归上游 agent/dispatch） |
| `drain` | 优雅排水：轮 ctx 与根 ctx 取消脱钩 + 在途轮收敛 |
| `egress` | 出口策略：三档单调可比 + 兑现判据 + 强度（declared/enforced 分开） |
| `eval` | 录制/重放/差异（轨迹回放判定） |
| `eventbus` | 进程内有损广播 + durable 发布面 + event-tail 补灌（Store 由宿主实现） |
| `finalize` | 中止→终态四分路由 |
| `gatecheck` | 审批层×沙箱层联合判据（两层都同意才放行） |
| `guardset` | 守卫装配契约：多守卫合成一条拒绝（接上游 guardx/invoke） |
| `handoff` | 跨进程交接契约（交接点/幂等键/回执地址/时限四问） |
| `hookengine` | hook 匹配/超时/fail-closed 裁决判据（传输协议归上游 runtime/hookx） |
| `invocation` | 工具调用账本：崩溃后调用身份存续（planned/failed 终态） |
| `invocation/invocationtest` |  |
| `metrics` | 内核指标口径契约面（名称/类型/维度/基数上界单一来源） |
| `ownership` | 跨区域所有权权威（提交栅栏纯判据） |
| `preset` | 具名不可变组合件（egress+gatecheck 预设） |
| `protocol` | 统一报告协议：Report 契约 + 五级容错解析 + 白名单校验 + Markdown 渲染 |
| `ptc` | 程序化工具编排沙箱：模型写程序→VM 执行→经 bindings 调宿主工具（三重预算） |
| `raceprobe` | race 门禁失败形态判定（纯函数层） |
| `reconcile` | 启动对账/归因收敛 |
| `retryplan` | 重试处置决策：幂等键重放 vs 原样重发的编排级合成（判据=上游 toolfail） |
| `scheduling` | Agent 调度判据面：优先级/加权公平/配额/背压（纯函数，不做队列不做执行） |
| `sideeffect` | 副作用「至多一次」跨进程契约：幂等键 + 租约 + 栅栏令牌 + 结果未知态 |
| `sidetest` | sideeffect.Store 共享契约测试套件（宿主存储实现跑同一套断言） |
| `skilldisclose` | 技能披露三信号确定性挑选（与 skillkit/skill 邻接） |
| `statemachine` | 环节状态机：条件迁移的纯函数件 |
| `steer` | 运行中接管五件套 |
| `taskboard` | 多 agent 任务板：DAG 依赖 + 认领租约 + 接管代次（boardtest 契约套件随行） |
| `taskboard/boardtest` |  |
| `tenant` | 多租户判据面：隔离/配额/权限上下文（数据面归宿主） |
| `tooldisclose` | 渐进式工具披露：确定性打分检索换完整 schema + 两类失败二分执行门禁 |
| `trajectory` | 事件→轨迹行的投影判据（实测/估算不混用） |
| `watchdog` | 被动配对不变量监视（只告警不裁决） |
| `worker` | 任务驱动循环：注册→心跳→领取→续期→恢复→退出 |
| `worktree` | 工作区冲突判据（声明面） |
| `worker/faultmatrix` | 故障注入矩阵本体（NetworkPolicy/PG HA 等真环境判据；CI 提供环境后由宿主测试入口执行） |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

### 分层口径（v0.70 确立，ADR-0010）

- **纯基础设施→oekit；工具/沙箱/执行安全→oagentkit（guardx/tools）；编排判据→本仓；装配/参考实现→goagent-runtime。** 按概念域分派，不按实现依赖分派。
- 判定口诀：「这个包需要知道自己在给谁干活吗？」需要 → 编排域留本仓；对话域判据已上抛（roundguard→agent、budget/spill/offload→textx、pending/sessionref/memorypipe→promptx，v0.77.0）。
- 本仓不 import 领域词表；门禁由自带 archcheck + architecture-policy.yaml 强制（策略先行：新依赖方向先改 policy 再写代码）。
- 发版是**纯 git tag + 自有 releasecheck 门禁**，不走 matrix release.py；CHANGELOG 由 gen_changelogs.py 生成。
- 2026-11-26 归属迁移：yi-nology → oagentkit org，module path 为 github.com/oagentkit/goagent-kernel（旧路径经 GitHub 重定向）。

## 日志约定

- 日志走 `oekit/logx`；编排事件优先走 `eventbus`（结构化、可投影），日志只留人读的判据结论。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
