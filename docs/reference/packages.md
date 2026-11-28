# 机器事实：模块 × 包 × 版本

这一页是**机器可读事实的人读投影**：模块数、包数、import 路径、旧单仓路径、最新版本全部来自 `data/modules.json` 与 `docs/public/versions.json`，由 `scripts/gen_module_pages.py` 生成——**手改会在下次生成时消失**。

同一份事实的机器可读形态：[`versions.json`](/versions.json) 与 [`llms.txt`](/llms.txt)。

## 总计

| 项 | 值 |
| --- | --- |
| 模块 | 16 |
| 包 | 139 |
| 层 | 6（tier 0 – tier 5） |
| 组织 | `oagentkit` |
| 源 | `oagentkit/matrix-tools`（模块与版本两份产物分别生成后对账） |

## 逐模块

| 模块 | 层 | 包数 | 最新版 | 仓内依赖 | 第三方地板 |
| --- | --- | --- | --- | --- | --- |
| [`guardx`](/modules/guardx.html) | <span class="matrix-tier">tier 0</span> | 13 | `v0.30.0` | <span class="matrix-tier">—</span> | <span class="matrix-tier">零</span> |
| [`runtime`](/modules/runtime.html) | <span class="matrix-tier">tier 0</span> | 7 | `v0.14.0` | <span class="matrix-tier">—</span> | <span class="matrix-tier">零</span> |
| [`textx`](/modules/textx.html) | <span class="matrix-tier">tier 0</span> | 10 | `v0.14.0` | <span class="matrix-tier">—</span> | <span class="matrix-tier">零</span> |
| [`toolname`](/modules/toolname.html) | <span class="matrix-tier">tier 0</span> | 1 | `v0.2.1` | <span class="matrix-tier">—</span> | <span class="matrix-tier">零</span> |
| [`promptx`](/modules/promptx.html) | <span class="matrix-tier">tier 1</span> | 6 | `v0.11.0` | <span class="matrix-tier">`textx`、`guardx`</span> | <span class="matrix-tier">零</span> |
| [`llm`](/modules/llm.html) | <span class="matrix-tier">tier 2</span> | 6 | `v0.27.0` | <span class="matrix-tier">`textx`</span> | <span class="matrix-tier">`github.com/cloudwego/eino`、`github.com/cloudwego/eino-ext/components/model/openai`、`github.com/meguminnnnnnnnn/go-openai`、`go.opentelemetry.io/otel`、`go.opentelemetry.io/otel/sdk`、`go.opentelemetry.io/otel/trace`</span> |
| [`mcpkit`](/modules/mcpkit.html) | <span class="matrix-tier">tier 2</span> | 2 | `v0.15.0` | <span class="matrix-tier">—</span> | <span class="matrix-tier">`github.com/mark3labs/mcp-go`、`github.com/eino-contrib/jsonschema`、`github.com/cloudwego/eino`</span> |
| [`obs`](/modules/obs.html) | <span class="matrix-tier">tier 2</span> | 1 | `v0.9.18` | <span class="matrix-tier">`guardx`</span> | <span class="matrix-tier">零</span> |
| [`queue`](/modules/queue.html) | <span class="matrix-tier">tier 2</span> | 5 | `v0.13.0` | <span class="matrix-tier">—</span> | <span class="matrix-tier">`github.com/lib/pq`、`modernc.org/sqlite`</span> |
| [`rag`](/modules/rag.html) | <span class="matrix-tier">tier 2</span> | 5 | `v0.13.0` | <span class="matrix-tier">`textx`</span> | <span class="matrix-tier">`github.com/cloudwego/eino`、`github.com/milvus-io/milvus-sdk-go/v2`、`gopkg.in/yaml.v3`</span> |
| [`skillkit`](/modules/skillkit.html) | <span class="matrix-tier">tier 2</span> | 3 | `v0.10.7` | <span class="matrix-tier">`textx`、`guardx`</span> | <span class="matrix-tier">`github.com/cloudwego/eino`、`gopkg.in/yaml.v3`、`github.com/Masterminds/semver/v3`</span> |
| [`toolgate`](/modules/toolgate.html) | <span class="matrix-tier">tier 2</span> | 3 | `v0.17.5` | <span class="matrix-tier">`guardx`、`mcpkit`</span> | <span class="matrix-tier">`github.com/cloudwego/eino`、`gopkg.in/yaml.v3`</span> |
| [`tools`](/modules/tools.html) | <span class="matrix-tier">tier 2</span> | 7 | `v0.17.0` | <span class="matrix-tier">`textx`、`guardx`</span> | <span class="matrix-tier">`github.com/cloudwego/eino`、`mvdan.cc/sh/v3`</span> |
| [`agent`](/modules/agent.html) | <span class="matrix-tier">tier 3</span> | 8 | `v0.17.0` | <span class="matrix-tier">`llm`、`textx`</span> | <span class="matrix-tier">`github.com/cloudwego/eino`、`github.com/cloudwego/eino-ext/components/model/openai`、`gopkg.in/yaml.v3`</span> |
| [`goagent-kernel`](/modules/goagent-kernel.html) | <span class="matrix-tier">tier 4</span> | 46 | `v0.80.0` | <span class="matrix-tier">`guardx`、`runtime`、`toolgate`、`toolname`</span> | <span class="matrix-tier">`github.com/dop251/goja`、`github.com/santhosh-tekuri/jsonschema/v6`、`golang.org/x/tools`、`gopkg.in/yaml.v3`</span> |
| [`goagent-runtime`](/modules/goagent-runtime.html) | <span class="matrix-tier">tier 5</span> | 16 | `v0.9.0` | <span class="matrix-tier">`agent`、`goagent-kernel`、`guardx`</span> | <span class="matrix-tier">`github.com/jackc/pgx/v5`、`modernc.org/sqlite`</span> |

## 全包清单

「旧单仓路径」是单仓时代（`git.enjoye.top/enjoydream/agentkit`）的包位置，改写工具据此做纯前缀映射——消费方改 import 时只需要替换前缀。

| 模块 | 包 | import 路径 | 旧单仓路径 |
| --- | --- | --- | --- |
| `guardx` | `fence` | `github.com/oagentkit/guardx/fence` | `agentkit/fence` |
| `guardx` | `logredact` | `github.com/oagentkit/guardx/logredact` | `agentkit/logredact` |
| `guardx` | `egress` | `github.com/oagentkit/guardx/egress` | `agentkit/egress` |
| `guardx` | `egressproxy` | `github.com/oagentkit/guardx/egressproxy` | `—` |
| `guardx` | `permgate` | `github.com/oagentkit/guardx/permgate` | `agentkit/permgate` |
| `guardx` | `injectband` | `github.com/oagentkit/guardx/injectband` | `agentkit/injectband` |
| `guardx` | `invoke` | `github.com/oagentkit/guardx/invoke` | `agentkit/invoke` |
| `guardx` | `toolfail` | `github.com/oagentkit/guardx/toolfail` | `—` |
| `guardx` | `sandbox` | `github.com/oagentkit/guardx/sandbox` | `—` |
| `guardx` | `wire` | `github.com/oagentkit/guardx/wire` | `—` |
| `guardx` | `netguard` | `github.com/oagentkit/guardx/netguard` | `—` |
| `guardx` | `rbac` | `github.com/oagentkit/guardx/rbac` | `—` |
| `guardx` | `ticket` | `github.com/oagentkit/guardx/ticket` | `—` |
| `runtime` | `pacer` | `github.com/oagentkit/runtime/pacer` | `agentkit/pacer` |
| `runtime` | `progress` | `github.com/oagentkit/runtime/progress` | `agentkit/progress` |
| `runtime` | `procx` | `github.com/oagentkit/runtime/procx` | `agentkit/procx` |
| `runtime` | `hotplug` | `github.com/oagentkit/runtime/hotplug` | `agentkit/hotplug` |
| `runtime` | `hookx` | `github.com/oagentkit/runtime/hookx` | `agentkit/hookx` |
| `runtime` | `notifyx` | `github.com/oagentkit/runtime/notifyx` | `—` |
| `runtime` | `notifyx/hook` | `github.com/oagentkit/runtime/hook` | `—` |
| `textx` | `textutil` | `github.com/oagentkit/textx/textutil` | `agentkit/textutil` |
| `textx` | `diffx` | `github.com/oagentkit/textx/diffx` | `agentkit/diffx` |
| `textx` | `codeintel` | `github.com/oagentkit/textx/codeintel` | `agentkit/codeintel` |
| `textx` | `compact` | `github.com/oagentkit/textx/compact` | `agentkit/compact` |
| `textx` | `conversation` | `github.com/oagentkit/textx/conversation` | `agentkit/conversation` |
| `textx` | `reportutil` | `github.com/oagentkit/textx/reportutil` | `agentkit/reportutil` |
| `textx` | `gotyped` | `github.com/oagentkit/textx/gotyped` | `—` |
| `textx` | `budget` | `github.com/oagentkit/textx/budget` | `—` |
| `textx` | `spill` | `github.com/oagentkit/textx/spill` | `—` |
| `textx` | `offload` | `github.com/oagentkit/textx/offload` | `—` |
| `toolname` | `toolname` | `github.com/oagentkit/toolname` | `oekit/pkg/toolname` |
| `promptx` | `sysprompt` | `github.com/oagentkit/promptx/sysprompt` | `agentkit/sysprompt` |
| `promptx` | `steering` | `github.com/oagentkit/promptx/steering` | `agentkit/steering` |
| `promptx` | `filestate` | `github.com/oagentkit/promptx/filestate` | `agentkit/filestate` |
| `promptx` | `pending` | `github.com/oagentkit/promptx/pending` | `—` |
| `promptx` | `sessionref` | `github.com/oagentkit/promptx/sessionref` | `—` |
| `promptx` | `memorypipe` | `github.com/oagentkit/promptx/memorypipe` | `—` |
| `llm` | `llm` | `github.com/oagentkit/llm` | `agentkit/llm` |
| `llm` | `llm/port` | `github.com/oagentkit/llm/port` | `agentkit/llm/port` |
| `llm` | `llm/wrap` | `github.com/oagentkit/llm/wrap` | `agentkit/llm/wrap` |
| `llm` | `llm/llmtest` | `github.com/oagentkit/llm/llmtest` | `agentkit/llm/llmtest` |
| `llm` | `obsx` | `github.com/oagentkit/llm/obsx` | `agentkit/obsx` |
| `llm` | `llm/decision` | `github.com/oagentkit/llm/decision` | `—` |
| `mcpkit` | `mcp` | `github.com/oagentkit/mcpkit/mcp` | `agentkit/mcp` |
| `mcpkit` | `iface` | `github.com/oagentkit/mcpkit/iface` | `—` |
| `obs` | `audit` | `github.com/oagentkit/obs/audit` | `agentkit/audit` |
| `queue` | `worker` | `github.com/oagentkit/queue/worker` | `agentkit/worker` |
| `queue` | `worker/pglease` | `github.com/oagentkit/queue/pglease` | `agentkit/worker/pglease` |
| `queue` | `sqllease` | `github.com/oagentkit/queue/sqllease` | `—` |
| `queue` | `sqlqueue` | `github.com/oagentkit/queue/sqlqueue` | `—` |
| `queue` | `outbox` | `github.com/oagentkit/queue/outbox` | `—` |
| `rag` | `knowledge/rag` | `github.com/oagentkit/rag` | `agentkit/knowledge/rag` |
| `rag` | `wiki` | `github.com/oagentkit/rag/wiki` | `—` |
| `rag` | `wiki/fsstore` | `github.com/oagentkit/rag/fsstore` | `—` |
| `rag` | `milvus` | `github.com/oagentkit/rag/milvus` | `—` |
| `rag` | `ontology` | `github.com/oagentkit/rag/ontology` | `—` |
| `skillkit` | `skill` | `github.com/oagentkit/skillkit/skill` | `agentkit/skill` |
| `skillkit` | `pack` | `github.com/oagentkit/skillkit/pack` | `agentkit/pack` |
| `skillkit` | `lineage` | `github.com/oagentkit/skillkit/lineage` | `agentkit/lineage` |
| `toolgate` | `toolprior` | `github.com/oagentkit/toolgate/toolprior` | `agentkit/toolprior` |
| `toolgate` | `toolsched` | `github.com/oagentkit/toolgate/toolsched` | `agentkit/toolsched` |
| `toolgate` | `policy` | `github.com/oagentkit/toolgate/policy` | `agentkit/policy` |
| `tools` | `acpx` | `github.com/oagentkit/tools/acpx` | `agentkit/acpx` |
| `tools` | `websearch` | `github.com/oagentkit/tools/websearch` | `agentkit/websearch` |
| `tools` | `workcopy` | `github.com/oagentkit/tools/workcopy` | `agentkit/workcopy` |
| `tools` | `sast` | `github.com/oagentkit/tools/sast` | `agentkit/sast` |
| `tools` | `bashguard` | `github.com/oagentkit/tools/bashguard` | `agentkit/bashguard` |
| `tools` | `bgjob` | `github.com/oagentkit/tools/bgjob` | `—` |
| `tools` | `cmdpolicy` | `github.com/oagentkit/tools/cmdpolicy` | `—` |
| `agent` | `iface` | `github.com/oagentkit/agent/iface` | `—` |
| `agent` | `agentrun` | `github.com/oagentkit/agent/agentrun` | `agentkit/agentrun` |
| `agent` | `reflection` | `github.com/oagentkit/agent/reflection` | `agentkit/reflection` |
| `agent` | `router` | `github.com/oagentkit/agent/router` | `agentkit/router` |
| `agent` | `blackboard` | `github.com/oagentkit/agent/blackboard` | `agentkit/blackboard` |
| `agent` | `dispatch` | `github.com/oagentkit/agent/dispatch` | `agentkit/dispatch` |
| `agent` | `clarify` | `github.com/oagentkit/agent/clarify` | `agentkit/clarify` |
| `agent` | `roundguard` | `github.com/oagentkit/agent/roundguard` | `—` |
| `goagent-kernel` | `archcheck` | `github.com/yi-nology/goagent-kernel/archcheck` | `—` |
| `goagent-kernel` | `backend` | `github.com/yi-nology/goagent-kernel/backend` | `—` |
| `goagent-kernel` | `checkpoint` | `github.com/yi-nology/goagent-kernel/checkpoint` | `—` |
| `goagent-kernel` | `commitgate` | `github.com/yi-nology/goagent-kernel/commitgate` | `—` |
| `goagent-kernel` | `contract` | `github.com/yi-nology/goagent-kernel/contract` | `—` |
| `goagent-kernel` | `controlplane` | `github.com/yi-nology/goagent-kernel/controlplane` | `—` |
| `goagent-kernel` | `coord` | `github.com/yi-nology/goagent-kernel/coord` | `—` |
| `goagent-kernel` | `cost` | `github.com/yi-nology/goagent-kernel/cost` | `—` |
| `goagent-kernel` | `deadline` | `github.com/yi-nology/goagent-kernel/deadline` | `—` |
| `goagent-kernel` | `delegate` | `github.com/yi-nology/goagent-kernel/delegate` | `—` |
| `goagent-kernel` | `delta` | `github.com/yi-nology/goagent-kernel/delta` | `—` |
| `goagent-kernel` | `dispatch` | `github.com/yi-nology/goagent-kernel/dispatch` | `agentkit/dispatch` |
| `goagent-kernel` | `drain` | `github.com/yi-nology/goagent-kernel/drain` | `—` |
| `goagent-kernel` | `egress` | `github.com/yi-nology/goagent-kernel/egress` | `agentkit/egress` |
| `goagent-kernel` | `eval` | `github.com/yi-nology/goagent-kernel/eval` | `—` |
| `goagent-kernel` | `eventbus` | `github.com/yi-nology/goagent-kernel/eventbus` | `—` |
| `goagent-kernel` | `finalize` | `github.com/yi-nology/goagent-kernel/finalize` | `—` |
| `goagent-kernel` | `gatecheck` | `github.com/yi-nology/goagent-kernel/gatecheck` | `—` |
| `goagent-kernel` | `guardset` | `github.com/yi-nology/goagent-kernel/guardset` | `—` |
| `goagent-kernel` | `handoff` | `github.com/yi-nology/goagent-kernel/handoff` | `—` |
| `goagent-kernel` | `hookengine` | `github.com/yi-nology/goagent-kernel/hookengine` | `—` |
| `goagent-kernel` | `invocation` | `github.com/yi-nology/goagent-kernel/invocation` | `—` |
| `goagent-kernel` | `invocation/invocationtest` | `github.com/yi-nology/goagent-kernel/invocationtest` | `—` |
| `goagent-kernel` | `metrics` | `github.com/yi-nology/goagent-kernel/metrics` | `—` |
| `goagent-kernel` | `ownership` | `github.com/yi-nology/goagent-kernel/ownership` | `—` |
| `goagent-kernel` | `preset` | `github.com/yi-nology/goagent-kernel/preset` | `—` |
| `goagent-kernel` | `protocol` | `github.com/yi-nology/goagent-kernel/protocol` | `—` |
| `goagent-kernel` | `ptc` | `github.com/yi-nology/goagent-kernel/ptc` | `—` |
| `goagent-kernel` | `raceprobe` | `github.com/yi-nology/goagent-kernel/raceprobe` | `—` |
| `goagent-kernel` | `reconcile` | `github.com/yi-nology/goagent-kernel/reconcile` | `—` |
| `goagent-kernel` | `retryplan` | `github.com/yi-nology/goagent-kernel/retryplan` | `—` |
| `goagent-kernel` | `scheduling` | `github.com/yi-nology/goagent-kernel/scheduling` | `—` |
| `goagent-kernel` | `sideeffect` | `github.com/yi-nology/goagent-kernel/sideeffect` | `—` |
| `goagent-kernel` | `sidetest` | `github.com/yi-nology/goagent-kernel/sidetest` | `—` |
| `goagent-kernel` | `skilldisclose` | `github.com/yi-nology/goagent-kernel/skilldisclose` | `—` |
| `goagent-kernel` | `statemachine` | `github.com/yi-nology/goagent-kernel/statemachine` | `—` |
| `goagent-kernel` | `steer` | `github.com/yi-nology/goagent-kernel/steer` | `—` |
| `goagent-kernel` | `taskboard` | `github.com/yi-nology/goagent-kernel/taskboard` | `—` |
| `goagent-kernel` | `taskboard/boardtest` | `github.com/yi-nology/goagent-kernel/boardtest` | `—` |
| `goagent-kernel` | `tenant` | `github.com/yi-nology/goagent-kernel/tenant` | `—` |
| `goagent-kernel` | `tooldisclose` | `github.com/yi-nology/goagent-kernel/tooldisclose` | `—` |
| `goagent-kernel` | `trajectory` | `github.com/yi-nology/goagent-kernel/trajectory` | `—` |
| `goagent-kernel` | `watchdog` | `github.com/yi-nology/goagent-kernel/watchdog` | `—` |
| `goagent-kernel` | `worker` | `github.com/yi-nology/goagent-kernel/worker` | `agentkit/worker` |
| `goagent-kernel` | `worktree` | `github.com/yi-nology/goagent-kernel/worktree` | `—` |
| `goagent-kernel` | `worker/faultmatrix` | `github.com/yi-nology/goagent-kernel/faultmatrix` | `—` |
| `goagent-runtime` | `chat` | `github.com/yi-nology/goagent-runtime/chat` | `—` |
| `goagent-runtime` | `pipeline` | `github.com/yi-nology/goagent-runtime/pipeline` | `—` |
| `goagent-runtime` | `agentloop` | `github.com/yi-nology/goagent-runtime/agentloop` | `—` |
| `goagent-runtime` | `adjudicate` | `github.com/yi-nology/goagent-runtime/adjudicate` | `—` |
| `goagent-runtime` | `storage` | `github.com/yi-nology/goagent-runtime/storage` | `—` |
| `goagent-runtime` | `storage/sqlitestore` | `github.com/yi-nology/goagent-runtime/sqlitestore` | `—` |
| `goagent-runtime` | `sqliteadapter` | `github.com/yi-nology/goagent-runtime/sqliteadapter` | `—` |
| `goagent-runtime` | `pgstore` | `github.com/yi-nology/goagent-runtime/pgstore` | `—` |
| `goagent-runtime` | `runtime` | `github.com/yi-nology/goagent-runtime/runtime` | `—` |
| `goagent-runtime` | `cluster` | `github.com/yi-nology/goagent-runtime/cluster` | `—` |
| `goagent-runtime` | `observe` | `github.com/yi-nology/goagent-runtime/observe` | `—` |
| `goagent-runtime` | `containerbackend` | `github.com/yi-nology/goagent-runtime/containerbackend` | `—` |
| `goagent-runtime` | `bridge/llmchat` | `github.com/yi-nology/goagent-runtime/llmchat` | `—` |
| `goagent-runtime` | `bridge/einotool` | `github.com/yi-nology/goagent-runtime/einotool` | `—` |
| `goagent-runtime` | `trace` | `github.com/yi-nology/goagent-runtime/trace` | `—` |
| `goagent-runtime` | `agentiface` | `github.com/yi-nology/goagent-runtime/agentiface` | `—` |

## 装机

```bash
go get github.com/oagentkit/textx@latest
```

装**模块**（`github.com/oagentkit/<仓名>`），不要装**包路径**——包路径只是模块里的一个目录，单独装拿不到版本。

## 相关

- [模块总览](/modules/)
- [坑速查](/reference/pitfalls.html) —— 已退役的包、兼容壳期限、层地板
- [架构总览](/guide/architecture.html)
