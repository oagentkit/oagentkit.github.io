# llm

模型客户端——多模型降级链/任务级预算/成本记账/分阶段路由/LLM 调用观测

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 2 · 集成层（依赖 tier 0/1 + 重第三方地板） |
| oekit 对应 | `httpx` |
| 仓内依赖 | `textx` |
| 被依赖 | `agent` |
| 第三方地板 | `github.com/cloudwego/eino`、`github.com/meguminnnnnnnnn/go-openai`、`github.com/cloudwego/eino-ext/components/model/openai`、`golang.org/x/time` |
| 包数 | 6 |

## 安装

```bash
go get github.com/oagentkit/llm@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/llm](https://github.com/oagentkit/llm)

## 包

| 包 | 说明 |
| --- | --- |
| `llm` | 模型客户端：多模型降级链、任务级预算、成本记账、分阶段路由、主备切换 |
| `llm/port` | 窄接口层（不引 eino）：Complete(ctx,req) 形态的降级链/预算/成本记账；无 eino 的内核（预算/成本/价表/熔断）由根包下沉而来，两条路径共用同一份实现 |
| `llm/wrap` | 调用包装与限流适配 |
| `llm/llmtest` | 模型层契约测试套件 |
| `obsx` | eino callbacks 体系的 LLM 调用追踪 + token 用量采集 + 分阶段打标（自 obs/obsx 迁入） |
| `llm/decision` | System One 协议判定面客户端（非自回归判定模型）：choice/score/noul 三原语 + 校准置信口径（本地算，两端同义） |

## 过渡期兼容镜像

- `llm/llm`
  - 实现：llm/llm/compat.go —— 镜像根包全部 71 个导出符号（31 type / 31 func / 2 var / 7 const）；类型用 type 别名、函数用 var 转发、常量原样转发，一致性由 llm/llm/compat_test.go 的 AST 比对强制
  - 可用 import 路径：`github.com/oagentkit/llm/llm`（llm v0.18.0 起）
  - 规范路径：`github.com/oagentkit/llm` —— 新代码用它
  - 不进规范包清单的原因：规范包清单的 import 路径规则把「包名末段 == 仓名」收口到 module 根（matrix_paths.new_import_path）；登记它会让 versions.json 给根包与它登记同一个 importPath
  - 状态：过渡期兼容镜像 —— 包是活的（v0.18.0 起可 import），只为存量下游存在
  - 下一步：新代码一律直接 import github.com/oagentkit/llm；本镜像随 0.x 版本线退役

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

- **降级链的每一跳都必须记录原因**（成本/限流/超时/内容策略），不得静默换模型。
- **预算判定必须在调用前**，不能事后扣减 —— 事后扣减等于没有预算。
- **panic 不能只转成 error。** `RunSafe*` 系列会把 panic 收进全局 `PanicHandler`
  （库不接 `SetPanicHandler`，默认 `log.Printf`）且返回的 `panic: X` 无哨兵类型，
  无法挂回领域上下文。用 `RunSafeErr` 前先确认丢掉的结构化上下文可接受。
- **`obsx` 自 `obs/obsx` 迁入**（v0.12.0）：它绑 eino 框架（callbacks 适配层），而本仓早已 import 它做成本记账与阶段打标——同一关注点，两个包住一起更顺。

## 日志约定

- 日志走 `oekit/logx`，组件 logger 用 `logx.Delegating("oagentkit-llm")`，
  禁止 `Default()`/`WithService` 声明包级 logger。
- 模型请求/响应落日志前必须脱敏（凭据与用户数据都可能出现在 prompt 里）。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [AI Agent 编排](/guide/ai-agent.html)
- [模型调用与路由](/guide/llm-routing.html)
- [可观测](/guide/observability.html)
