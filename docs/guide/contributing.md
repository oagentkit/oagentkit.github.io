---
title: CI 门禁与模块规则
---

# CI 门禁与模块规则

## 规则本体只在 `.github` 一个仓

> **改 CI 规则只去 [`oagentkit/.github`](https://github.com/oagentkit/.github) 仓**
> （`go-ci.yml@main`）；各仓 `ci.yml` 只是薄调用层，**不要在各仓复制规则**。

各仓的 `ci.yml` 长这样，十几行：

```yaml
name: CI
on:
  push:    { branches: [main] }
  pull_request: { branches: [main] }
  workflow_dispatch:
permissions:
  contents: read
concurrency:
  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
jobs:
  ci:
    name: Lint & Test
    uses: oagentkit/.github/.github/workflows/go-ci.yml@main
    with:
      go-version: '1.26'
```

规则本体在 `oagentkit/.github/.github/workflows/go-ci.yml`，分 `lint` 和 `test` 两个 job。
因为是 reusable workflow，改一处全 org 生效——这也是为什么不要在分仓复制。

### 门禁项

| input | 默认 | 作用 |
| --- | --- | --- |
| `go-version` | `1.24` | setup-go 语义（`1.24` → 最新 `1.24.x`） |
| `golangci-lint-version` | `v2.14.0` | golangci-lint 版本 |
| `coverage-threshold` | `30` | 总覆盖率下限（百分比），`0` = 关闭 |
| `test-script` | `go test -race -count=1 -coverprofile=coverage.out ./...` | 产物含 `coverage.out` 时自动接覆盖率门禁 |
| `additional-script` | 空 | 测试后附加检查；嵌套模块已自动测，这里只放特例 |
| `test-nested` | `true` | 自动发现并测试嵌套 go.mod 子模块（build + test -race） |
| `govulncheck` | `true` | 漏洞扫描，**非阻塞报告** |
| `tidy-check` | `true` | `go mod tidy -diff`，检测 go.mod/go.sum 漂移 |

`tidy-check` 抓的是这几类问题：**指向已删 tag 的版本地板、旧 import 路径、排序不规范**。
改了 module 路径忘改 import，会在这里被拦住。

`.github` 仓还有 `workflow-lint.yml` 跑 **actionlint**，以及 `sync-callers.sh` /
`sync-dependabot.sh` 负责同步各仓的调用层和 dependabot 配置。

## 每仓的 `AGENTS.md` 是权威规范

> **每个仓库根目录的 `AGENTS.md` 是该仓的权威规范**：分层不变量、错误处理、日志、
> 并发安全、API 命名，以及该仓特有的工程红线。

本站的[模块页](/modules/)只是**摘要**。改代码前以仓库里的 `AGENTS.md` 为准。

矩阵通用的几条：

- 错误一律 `github.com/oekit/pkg/errors`，业务错误用 `BizError`；禁止 `_` 忽略
- 禁裸 `go func`，用 `oekit/concurrency/async` 的 `GoSafe` 系列
- 共享状态用 mutex / atomic；包级全局可变状态用 `atomic.Pointer[T]`
- 函数选项命名 `XxxOption`，**禁止裸 `Option`**（多包 co-import 会冲突）
- 日志走 `oekit/logx`，组件 logger 用 `logx.Delegating("oagentkit-<repo>")`
- 用户可见输出落日志前过 `guardx/fence`

## `matrix-tools`：一切从 `modules.json` 生成

| 脚本 | 作用 |
| --- | --- |
| `gen_docs.py` | 从 `modules.json` 生成**各仓**的 `README.md` 与 `AGENTS.md` |
| `gen_llms_txt.py` | 生成 [`llms.txt`](https://oagentkit.github.io/llms.txt) |
| `gen_versions.py` | 生成 [`versions.json`](https://oagentkit.github.io/versions.json) |
| `verify_split.py` | 校验拆分结果 |
| `rewrite_imports.py` | import 路径改写（⚠️ **不是纯前缀映射**，见下方路径规则） |
| `matrix_paths.py` | 旧→新 import 路径构造规则的**唯一事实源**，被上面几个脚本共用 |
| `verify_docs.py` | 防漂移：重新生成 `llms.txt` 与提交版比对，不一致 exit 1 |
| `create_repos.py` / `publish_repo.sh` | 建仓与发布 |

**`modules.json` 是唯一数据源。** 13 个仓的文档有 90% 是同构的（分层声明、硬规则、
依赖表、「不属于本仓」表），手写必然漂移——所以生成。

### import 路径规则（迁移必读）

import 路径**不是纯前缀映射**：

```
新路径 = github.com/oagentkit/{仓名}/{包名末段}
```

旧单仓路径的**中间层目录会被丢掉**，因为新矩阵里那层组织职责由**仓**承担：

| 旧单仓 | 新路径 | 直觉会写成（错） |
| --- | --- | --- |
| `agentkit/knowledge/rag` | `oagentkit/rag` | `oagentkit/rag/knowledge/rag` |
| `agentkit/worker/pglease` | `oagentkit/queue/pglease` | `oagentkit/queue/worker/pglease` |
| `agentkit/llm` | `oagentkit/llm` | `oagentkit/llm/llm` |

最后一条最坑：**包名末段与仓名相同时收口到 module 根**，路径不重复末段。

完整对照：

```bash
python3 ../matrix-tools/scripts/rewrite_imports.py --org oagentkit --print-rules
```

机器可读映射在 [`versions.json`](https://oagentkit.github.io/versions.json) 的
`fromLegacy` 字段——工具做旧→新替换时读它，不必解析脚本源码。

本站的模块页同理：[`oagentkit.github.io`](https://github.com/oagentkit/oagentkit.github.io)
的 `scripts/gen_module_pages.py` 从同一份 `modules.json` 生成 13 个模块页 + 侧边栏 +
首页矩阵表。

```bash
npm run gen:modules          # 重新生成
python3 scripts/gen_module_pages.py --check   # 只校验是否同步（CI 用）
```

CI 页面类改动只需要改 `data/modules.json`，不要手改 `docs/modules/*.md`。

## 本地开发

```bash
go test ./... -race
go vet ./...
gofmt -l .
```

CI 跑 golangci-lint + `govulncheck`。**本地至少跑通 `go test -race`**——
矩阵里涉及 goroutine 的包（`runtime`、`queue`、`mcpkit` 的建连单飞、
`toolgate` 的并发调度）都必须带 `-race` 验过。

## 文档站

```bash
npm ci
npm run docs:dev        # 本地预览
npm run docs:build      # 产出到 docs/.vitepress/dist
```

站点从 `main` 分支构建部署到 GitHub Pages，配置文件在
`.github/workflows/pages.yml`。

## 相关

- [架构总览](/guide/architecture) —— 分层不变量与依赖方向
- [快速开始](/guide/getting-started) —— 矩阵通用规约
