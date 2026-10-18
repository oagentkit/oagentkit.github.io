# oagentkit.github.io

oagentkit 文档站 —— VitePress 源。线上：[https://oagentkit.github.io](https://oagentkit.github.io)

## 结构

```
docs/
├── .vitepress/
│   ├── config.mts          站点配置：导航、侧边栏、主题色、editLink
│   ├── modules-nav.json    生成物（13 模块的侧边栏数据）
│   └── theme/
│       ├── index.ts        主题入口
│       └── custom.css      品牌色覆盖（浅色 #0a58ca / 深色 #6cb6ff）
├── index.md                首页（模块矩阵表由 parts/matrix-table.md 注入）
├── guide/                  7 篇指南
├── modules/                13 个模块页 —— 生成物，不要手改
├── parts/matrix-table.md   首页矩阵表 —— 生成物
└── public/                 原样拷贝：llms.txt / versions.json / logo.svg / .nojekyll
data/modules.json           矩阵数据源（与 matrix-tools 同源）
scripts/gen_module_pages.py 页面生成器
```

## 构建

```bash
npm ci
npm run docs:dev      # 本地预览
npm run docs:build    # 产出到 docs/.vitepress/dist
```

## 改内容前先搞清楚什么是生成的

`docs/modules/*.md`、`docs/modules/index.md`、`docs/parts/matrix-table.md`、
`docs/.vitepress/modules-nav.json` 共 16 个文件是 **`data/modules.json` 生成的**。

要改模块信息，**改 `data/modules.json` 然后重新生成**：

```bash
npm run gen:modules                      # 重新生成
python3 scripts/gen_module_pages.py --check   # 只校验是否同步（CI 用）
```

CI 里跑的就是 `--check`，手改生成物会被直接拦下。

`docs/guide/*.md` 和 `docs/index.md` 是手写的，不受此约束。

## 矩阵数据源

`data/modules.json` 从 agentkit 源的 `docs/split-matrix/modules.json` 同步而来，
schema 与 [`oagentkit/matrix-tools`](https://github.com/oagentkit/matrix-tools) 一致——
那边用它生成各仓的 README / AGENTS.md，本仓用它生成站点页面。

⚠️ 生成器里的 `INTRA_DEPS`（仓间依赖）是显式维护的，
`modules.json` 只记录第三方依赖地板。**改仓间依赖时要同步 `llms.txt`**
（由 `matrix-tools/scripts/gen_llms_txt.py` 从同一份数据生成）。

## URL 形态

站内链接一律带 `.html` 后缀（`config.mts` 里 `cleanUrls: false`）。
GitHub Pages 走静态文件、没有 rewrite 兜底，带后缀的完整 URL 才能直接命中。

因此 `https://oagentkit.github.io/guide/ai-agent.html` 是有效地址 ——
CI 里有一条断言专门守它，防止以后重构把页面结构改掉。

## 部署

`.github/workflows/pages.yml`：`push` 到 `main` → 构建 → 部署到 GitHub Pages。
Pages 的 Source 必须是 **GitHub Actions**（不是 `main` 分支根目录）。

## License

MIT
