# AGENTS.md — oagentkit/oagentkit.github.io

> oagentkit 文档站 —— VitePress 源（`docs/`），GitHub Pages 线上站
> 线上地址：[https://oagentkit.github.io](https://oagentkit.github.io)
> 定位：**本仓只有文档，没有 Go 代码** —— 矩阵里 13 个模块仓各自独立发版，
> 本仓负责把它们讲清楚（模块页、架构指南、依赖图、AI Agent 入口 `llms.txt`）。

## 本仓包含

```
docs/
├── .vitepress/config.mts      站点配置：导航、侧边栏、主题色、editLink
├── .vitepress/modules-nav.json 生成物（13 模块的侧边栏数据）
├── .vitepress/graph-data.json  生成物（依赖图数据：tiers / nodes / edges / dependents）
├── index.md                    首页（矩阵表由 parts/matrix-table.md 注入）
├── guide/                      8 篇指南（手写，不受生成物约束）
├── modules/                    13 个模块页 —— 生成物
├── parts/matrix-table.md       首页矩阵表 —— 生成物
└── public/                     原样拷贝：llms.txt / versions.json / logo.svg / robots.txt
data/modules.json               站点侧模块数据源（matrix-tools 的副本）
scripts/gen_module_pages.py     页面 + 依赖图数据生成器
```

## 硬规则

### 数据来源：单一数据源 + 站点侧副本

- **权威源在 `matrix-tools` 仓**：[oagentkit/matrix-tools](https://github.com/oagentkit/matrix-tools)
  的 `matrix-tools/modules.json` 定义了 13 个模块及其 `packages` / `pkgDesc` / `tier` /
  `dependsOn` / `heavyDeps` / `agentNotes` / `loggingRule` 等字段。
  那边用它生成各仓的 README / AGENTS.md 与 `llms.txt`。
- **本仓 `data/modules.json` 是该文件的副本**，schema 相同、内容必须**逐字段一致**。
  改模块信息（加包、改分层、改依赖）时：
  1. 先在 `matrix-tools` 仓改源并提交；
  2. 再把源同步到本仓 `data/modules.json`；
  3. 然后 `npm run gen:modules` 重新生成。
- **禁止在本仓单方面发明模块信息。** 站点与源一旦漂移，就会出现两套互相矛盾的对外清单：
  AI Agent 读的 `docs/public/llms.txt` 里有某个包，人类读的模块页/依赖图里没有——
  这类矛盾比缺信息更糟。改动后应逐字段比对两边的 `modules.json`。
- 仓间依赖（谁依赖谁）只认 `dependsOn` 字段，**不要在脚本或页面里另抄一份依赖表**。

### 生成物不许手改

以下 **17 个文件**由 `data/modules.json` 生成，**手改会被 CI 直接拦下**
（`.github/workflows/pages.yml` 里跑 `python3 scripts/gen_module_pages.py --check`）：

```
docs/modules/*.md（13 个模块页 + docs/modules/index.md）
docs/parts/matrix-table.md
docs/.vitepress/modules-nav.json
docs/.vitepress/graph-data.json
```

- 要改模块信息 → 改 `data/modules.json` → `npm run gen:modules` → 提交生成物。
- **不要只改生成物**：那样下次生成会被覆盖，且 CI 校验会失败。
- `docs/guide/*.md` 与 `docs/index.md` 是手写的，不受此约束 —— 但里面引用的模块事实
  （包名、分层、依赖方向）仍要与数据源对得上。

### llms.txt / versions.json 是副本

- `docs/public/llms.txt` 由 `matrix-tools/scripts/gen_llms_txt.py` 从矩阵源生成，
  本仓只持有**逐字节一致的副本**；需要更新时去 `matrix-tools` 重新生成再同步过来。
- `docs/public/versions.json` 是 `matrix-tools/versions.json` 的副本，字段 `fromLegacy` /
  `importPath` 是机器可读的旧 import 路径映射，改动同样以源为准。
- 站点面向两类读者：**AI Agent 读 `llms.txt`，人类读页面**。两者的模块/包清单必须一致。

### 提交前必跑校验

```bash
python3 scripts/gen_module_pages.py --check   # CI 的校验命令：生成物与 modules.json 是否同步
npm run gen:modules                          # 如上一步报不同步，改数据源后重新生成
```

`--check` 必须输出 `OK：17 个生成文件均与 modules.json 同步` 才算通过。
CI（Pages workflow）还会跑 `npm ci` + `npm run docs:build`，
并断言 `docs/.vitepress/dist/guide/ai-agent.html` 存在。

### 站内链接

- 站内链接一律带 `.html` 后缀（`config.mts` 里 `cleanUrls: false`）。
  GitHub Pages 是静态托管、没有 rewrite 兜底，不带后缀的 URL 会 404。
- 改页面结构时注意 `guide/ai-agent.html` 有 CI 断言守着。

## 仓特有纪律

- **不要引入构建期新依赖**来干 `scripts/gen_module_pages.py` 已经能干的活；
  生成器只用 Python 标准库，CI 在 `npm ci` 之前就调它。
- **页面文案与矩阵事实分离**：文案（`guide/`）可以润色，事实（模块/包/分层/依赖）
  只能来自数据源，不在页面里硬写第二份。
- 站点不承载 Go 代码：**不要**在本仓建 `go.mod`、不要在站点 CI 里跑 `go build`。
  各仓的 CI 门禁在 `oagentkit/.github` 的 reusable workflow 里，与本仓无关。

## 明确不属于本仓的

| 能力 | 归属 |
|---|---|
| 模块实现（13 个 Go 模块） | `github.com/oagentkit/{模块名}` 各自独立仓 |
| 矩阵数据源与生成脚本 | `github.com/oagentkit/matrix-tools` |
| 各仓 CI 门禁 | `github.com/oagentkit/.github`（reusable workflow） |
| Pages 部署 | 本仓 `.github/workflows/pages.yml`（GitHub Actions Source） |
