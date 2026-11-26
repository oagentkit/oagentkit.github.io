# 坑速查

矩阵里最容易踩的几坑，全部由 `data/modules.json` 的账本与层规则推导，由 `scripts/gen_module_pages.py` 生成——**手改会在下次生成时消失**。

## 1. 已退役的包：那条路径已经没了

import 一个已退役的包**不会降级、不会告警，直接编译失败**——因为那条路径上已经没有包了。

| 包 | 迁往 | 状态 |
| --- | --- | --- |
| `breaker` | `github.com/oekit/concurrency/breaker` | 已完成：llm v0.4.0 起全量使用上游 GenBreaker |
| `llm/llm` | `github.com/oagentkit/llm` | 已完成：llm v0.22.0 删除兼容镜像（BREAKING，llm#181）——旧路径 import 一律改根包 github.com/oagentkit/llm（符号同名，调用点零改动） |
| `obs/langfuse` | `github.com/oagentkit/llm/obsx` | 已完成：obs 删除 obs/langfuse（BREAKING）——旧路径 import 一律改 github.com/oagentkit/llm/obsx（承接方 llm#231 已合） |

- `breaker` —— 消费方：llm/breaker.go —— 只做按模型名分桶 + 转发，不再有任何本地语义兜底
- `breaker` —— 需求链：
  - [`#17`](https://github.com/oekit/concurrency/issues/17) —— 三态 + 代绑定 + 探测时限 —— 已落地 v0.9.0
  - [`#19`](https://github.com/oekit/concurrency/issues/19) —— 冷却期与探测时限解耦（WithCooldown）—— 已落地 v0.12.0
  - [`#20`](https://github.com/oekit/concurrency/issues/20) —— 计数型触发（WithConsecutiveFailures）—— 已落地 v0.12.0
  - [`#25`](https://github.com/oekit/concurrency/issues/25) —— 计数型只切状态、切不了放行决策 —— 已落地 v0.13.0，llm 侧兜底已删除

- `llm/llm` —— 需求链：
  - [`#47`](https://github.com/oagentkit/llm/issues/47) —— 需求：llm/llm 扁平化后缺兼容子包 —— 跨大版本升级的下游需整仓改 import 路径（已关闭）
  - [`#48`](https://github.com/oagentkit/llm/issues/48) —— 实现：补 llm/llm 兼容层 —— 恢复 v0.7.0~v0.8.0 的历史 import 路径（已合入 llm v0.18.0）

- `obs/langfuse` —— 消费方：llm/obsx —— Langfuse 写/发射端与读端同域；读端实现迁入本包
- `obs/langfuse` —— 需求链：
  - [`#129`](https://github.com/oagentkit/obs/issues/129) —— langfuse 读端并入 llm/obsx（读写同域）；obs 降为 audit 单包仓 —— 已落地

## 2. 兼容镜像与兼容壳：路径还在，但有期限

兼容层是**有保质期**的：到期后上游删掉它，依赖它的代码在**升级上游之后**才编译失败——本地还绿、CI 才红，是最难查的一类断。

| 仓 | 壳路径 | 旧 import 路径 | 兼容至 | 已删除于 |
| --- | --- | --- | --- | --- |
| `toolgate` | `invoke` | `github.com/oagentkit/toolgate/invoke` | `v0.16.0` | `v0.17.0` |

## 3. 门面仓已退役：转发层不再转发

`agentkit` 是门面仓（re-export 兼容层），**v1.9.0 起已退役**（2026-11-13）：48 个转发包全部删除，旧 import 路径 `oagentkit/agentkit/*` 一律编译失败。

- 退役原因：兼容逻辑清仓车道：矩阵内零消费已验证，48 个转发包全部删除（BREAKING），旧 import 路径 github.com/oagentkit/agentkit/* 自 v1.9.0 起编译失败；go.mod 清空全部 require（零代码零依赖），README 留 48 包 → 上游对照表作迁移指引。较 notAfter 2027-05-31 提前退役；归档待旧单仓 git.enjoye.top/enjoydream/agentkit 下线后执行
- 决策：agentkit#198

## 4. 层地板：tier 0 / tier 1 不得有重量级第三方依赖

tier 由**依赖地板**决定，不是由功能多少决定。tier 0 / tier 1 必须零重量级第三方依赖——所以它们能被任何下游安全依赖；一旦某个 tier 0 仓引了 eino 或数据库驱动，它就不再是 tier 0，整条依赖链的地基都跟着变重。

| 模块 | 层 | 重量级第三方依赖 |
| --- | --- | --- |
| [`guardx`](/modules/guardx.html) | <span class="matrix-tier">tier 0</span> | <span class="matrix-tier">零</span> |
| [`runtime`](/modules/runtime.html) | <span class="matrix-tier">tier 0</span> | <span class="matrix-tier">零</span> |
| [`textx`](/modules/textx.html) | <span class="matrix-tier">tier 0</span> | <span class="matrix-tier">零</span> |
| [`toolname`](/modules/toolname.html) | <span class="matrix-tier">tier 0</span> | <span class="matrix-tier">零</span> |
| [`promptx`](/modules/promptx.html) | <span class="matrix-tier">tier 1</span> | <span class="matrix-tier">零</span> |
| [`llm`](/modules/llm.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`github.com/cloudwego/eino`、`github.com/cloudwego/eino-ext/components/model/openai`、`github.com/meguminnnnnnnnn/go-openai`、`go.opentelemetry.io/otel`、`go.opentelemetry.io/otel/sdk`、`go.opentelemetry.io/otel/trace`</span> |
| [`mcpkit`](/modules/mcpkit.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`github.com/mark3labs/mcp-go`、`github.com/eino-contrib/jsonschema`、`github.com/cloudwego/eino`</span> |
| [`obs`](/modules/obs.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">零</span> |
| [`queue`](/modules/queue.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`github.com/lib/pq`、`modernc.org/sqlite`</span> |
| [`rag`](/modules/rag.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`github.com/cloudwego/eino`、`github.com/milvus-io/milvus-sdk-go/v2`、`gopkg.in/yaml.v3`</span> |
| [`skillkit`](/modules/skillkit.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`github.com/cloudwego/eino`、`gopkg.in/yaml.v3`、`github.com/Masterminds/semver/v3`</span> |
| [`toolgate`](/modules/toolgate.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`github.com/cloudwego/eino`、`gopkg.in/yaml.v3`</span> |
| [`tools`](/modules/tools.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`github.com/cloudwego/eino`、`mvdan.cc/sh/v3`</span> |
| [`agent`](/modules/agent.html) | <span class="matrix-tier">tier 3</span> | <span class="matrix-tier">`github.com/cloudwego/eino`、`github.com/cloudwego/eino-ext/components/model/openai`、`gopkg.in/yaml.v3`</span> |
| [`goagent-kernel`](/modules/goagent-kernel.html) | <span class="matrix-tier">tier 4</span> | <span class="matrix-tier">`github.com/dop251/goja`、`github.com/santhosh-tekuri/jsonschema/v6`、`golang.org/x/tools`、`gopkg.in/yaml.v3`</span> |
| [`goagent-runtime`](/modules/goagent-runtime.html) | <span class="matrix-tier">tier 5</span> | <span class="matrix-tier">`github.com/jackc/pgx/v5`、`modernc.org/sqlite`</span> |

判据脚本：`matrix-tools/scripts/verify_dep_floor.py`——它读的是 `heavyDeps` 登记，不是读 go.mod 猜。

## 5. 依赖方向：tier N 不得依赖 tier > N

依赖严格自底向上。**反向依赖（tier 0 依赖 tier 3）不是「暂时方便」，是分层失效**——它让「上层坐在下层之上」的读法不再成立，依赖图也就没法用层号排序了。

| 模块 | 层 | 仓内依赖 |
| --- | --- | --- |
| [`guardx`](/modules/guardx.html) | <span class="matrix-tier">tier 0</span> | <span class="matrix-tier">—</span> |
| [`runtime`](/modules/runtime.html) | <span class="matrix-tier">tier 0</span> | <span class="matrix-tier">—</span> |
| [`textx`](/modules/textx.html) | <span class="matrix-tier">tier 0</span> | <span class="matrix-tier">—</span> |
| [`toolname`](/modules/toolname.html) | <span class="matrix-tier">tier 0</span> | <span class="matrix-tier">—</span> |
| [`promptx`](/modules/promptx.html) | <span class="matrix-tier">tier 1</span> | <span class="matrix-tier">`textx`（tier 0）、`guardx`（tier 0）</span> |
| [`llm`](/modules/llm.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`textx`（tier 0）</span> |
| [`mcpkit`](/modules/mcpkit.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">—</span> |
| [`obs`](/modules/obs.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`guardx`（tier 0）</span> |
| [`queue`](/modules/queue.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">—</span> |
| [`rag`](/modules/rag.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`textx`（tier 0）</span> |
| [`skillkit`](/modules/skillkit.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`textx`（tier 0）、`guardx`（tier 0）</span> |
| [`toolgate`](/modules/toolgate.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`guardx`（tier 0）、`mcpkit`（tier 2）</span> |
| [`tools`](/modules/tools.html) | <span class="matrix-tier">tier 2</span> | <span class="matrix-tier">`textx`（tier 0）、`guardx`（tier 0）</span> |
| [`agent`](/modules/agent.html) | <span class="matrix-tier">tier 3</span> | <span class="matrix-tier">`llm`（tier 2）、`textx`（tier 0）</span> |
| [`goagent-kernel`](/modules/goagent-kernel.html) | <span class="matrix-tier">tier 4</span> | <span class="matrix-tier">`guardx`（tier 0）、`runtime`（tier 0）、`toolgate`（tier 2）、`toolname`（tier 0）</span> |
| [`goagent-runtime`](/modules/goagent-runtime.html) | <span class="matrix-tier">tier 5</span> | <span class="matrix-tier">`agent`（tier 3）、`goagent-kernel`（tier 4）、`guardx`（tier 0）</span> |

判据脚本：`matrix-tools/scripts/verify_import_direction.py`（层级方向 + 依赖声明对账）。

## 相关

- [机器事实](/reference/packages.html) —— 模块 × 包 × 版本
- [模块总览](/modules/)
- [架构总览](/guide/architecture.html)
