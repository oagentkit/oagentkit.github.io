---
title: 破坏性变更与升级指南
---

# 破坏性变更与升级指南

本页只讲**破坏性变更**（升级会坏的那种）与**怎么迁**。能力说明在[模块页](/modules/)，
架构在[架构总览](/guide/architecture)。

## 机器可读源在哪

矩阵对下游公开的破坏性变更清单是**机器可读**的，不要手抄：

| 载体 | 位置 | 说明 |
| --- | --- | --- |
| 版本矩阵 | [`/versions.json`](https://oagentkit.github.io/versions.json) | 每个模块的 `breakingIndex` 数组；`detail` 存版本段全文（**迁移说明在里面**） |
| AI Agent 入口 | [`/llms.txt`](https://oagentkit.github.io/llms.txt) | 同一份事实的散文投影，含每条破坏的一句话摘要 |
| 源 | [`matrix-tools/scripts/breaking_index.py`](https://github.com/oagentkit/matrix-tools) | 抽取规则本体（由各仓 CHANGELOG 自动抽） |

**认破坏的方式**：看 `versions.json` 里 `modules[].breakingIndex` 有没有你要升的那个版本
⇒ 有 ⇒ 读它的 `summary` 与 `detail`（迁移说明）⇒ 没有 ⇒ 按 SemVer 判断（0.x 的
minor 版**可能**是破坏的，但矩阵只在明确标了 BREAKING 时才登记 ⇒ 没登记不代表
一定不破坏，看 CHANGELOG）。

## 当前待迁移：mcpkit v0.9.0

mcpkit v0.9.0 有**两处**破坏式变更（`versions.json` → `mcpkit.breakingIndex`）。

### ① `ToolSpec.Allow` 空列表不再等于「全部工具」

```go
// 改前：空 = 该 server 的全部工具（含破坏性工具）
spec := mcp.ToolSpec{Server: "ask-ops"}

// 改后：空 = **一个工具都不授予**（缺省拒绝）
spec := mcp.ToolSpec{Server: "ask-ops"}
```

**为什么改**：这个默认值在配置里**不可见**——一份 `allow: []` 看起来像「没限制」，
实际是「把该 server 的全部工具（含删除/执行类）都授予了模型」。最小权限的责任
整个落到了下游（下游只能靠事后门禁兜，那时配置已生效、模型已拿到工具）。

**怎么迁**：要「全给」必须**显式写出来**（两种等价写法）：

```go
// 写法 A：显式开关
spec := mcp.ToolSpec{Server: "ask-ops", AllowAll: true}

// 写法 B：白名单里的通配符
spec := mcp.ToolSpec{Server: "ask-ops", Allow: []string{"*"}}
```

配置侧同理（字段名随宿主而异，语义一致）：

```yaml
# 改前
- server: ask-ops
  allow: []            # ← 以前是「全部」，现在是「零个」

# 改后（显式全给）
- server: ask-ops
  allow: ["*"]
```

> ⚠️ **升级后必查**：把配置里**所有** `allow: []` / 缺省 `allow` 的条目找出来。
> 它们现在拿到的是**零个工具** ⇒ agent 看不到该 server 的任何能力，
> 而配置里看不出任何变化（这是静默失能，不是报错）。

### ② 工具暴露名带 server 命名空间

```go
// 改前：模型看到的是 MCP 原始名
//   get_system_inventory
// 改后：模型看到的是 server.原始名
//   ask-ops.get_system_inventory
```

**为什么改**：同一个工具名可以来自不同 server ⇒ 不带命名空间时，给模型的工具清单
里会出现两组同名工具，模型无法从名字分辨来源，命中哪个取决于装配顺序。

**怎么迁**：

- **按名字找工具的地方**：模型 prompt 里的工具名、历史 checkpoint 里的
  `tool_call.name` ⇒ 升级后对不上 ⇒ 需要按 `server.原始名` 重新对齐；
- **按名字过滤的地方**：白名单（`ToolSpec.Allow`）**两种写法都命中** ——
  原始名（server 内）与全名（`server.原始名`）⇒ 既有配置不用改；
- **调用 server 时**：线上仍用**原始名**（`server` 那边登记的就是它）⇒
  下游代码不需要改。

### 按名取单个工具：新增入口

v0.9.0 还新增了一个一等入口（不是破坏，是给「取指定 server 的指定工具」用）：

```go
// 改前：只能靠位置假设（res.Tools[0]）——Allow 给多个工具时会取到**另一个**
inv, err := pool.Tools(ctx, []mcp.ToolSpec{{Server: srv, Allow: []string{name}}})
got := inv.Tools[0]

// 改后：按名取，取不到是**显式错误**
got, err := pool.Tool(ctx, srv, name)
if err != nil {
    // 显式失败，不会静默拿到别的工具
}
```

批量场景还可以用结构化归属面：`ToolsResult.ByServer`（server → 该 server 的工具）。

## 升级自检清单

- [ ] 配置里所有 `allow: []` / 缺省 `allow` 的条目，已改成显式全给（`allow: ["*"]`
      或 `AllowAll: true`）；
- [ ] 按工具名过滤/匹配的代码，确认用的是**原始名**或**全名**（两种都命中）；
- [ ] 模型 prompt 与历史 checkpoint 里的工具名，按 `server.原始名` 对齐；
- [ ] 跑一遍集成测试，确认该 server 的工具**数量**符合预期（数量变了就是踩到 ①）；
- [ ] 升级后核一遍 `versions.json` 里该模块的 `breakingIndex`，确认没有别的破坏项。

## 相关

- [工具接入与治理](/guide/tools-and-mcp) —— 三个工具仓怎么拼
- [mcpkit 模块页](/modules/mcpkit) —— 能力与硬规则
- [CI 门禁与模块规则](/guide/contributing) —— 矩阵自己的门禁与发版流程
