# skillkit

技能与资产契约——SKILL.md 渐进披露/领域包布局契约/装配血缘图

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 2 · 集成层（依赖 tier 0/1 + 重第三方地板） |
| oekit 对应 | `pack` |
| 仓内依赖 | `textx`、`guardx` |
| 被依赖 | —（矩阵叶子） |
| 第三方地板 | `github.com/cloudwego/eino`、`gopkg.in/yaml.v3`、`github.com/Masterminds/semver/v3` |
| 包数 | 3 |

## 安装

```bash
go get github.com/oagentkit/skillkit@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/skillkit](https://github.com/oagentkit/skillkit)

## 包

| 包 | 说明 |
| --- | --- |
| `skill` | SKILL.md 渐进披露：元数据常驻、正文按需加载；多根技能库与版本判定 |
| `pack` | 领域包（expert/pack 目录布局）的契约面 |
| `lineage` | 装配血缘：expert → skill → MCP server 三类资产节点的依赖图 |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

- SKILL.md 的**渐进披露**是硬要求：元数据常驻、正文按需加载。
  不得为了「一次读全」把正文塞进元数据 —— 那会让常驻上下文无谓膨胀。
- `pack` 的目录布局是契约面，改动布局等于 breaking，必须升 major。
- **层位 t1 → t2**：带 `eino` 地板（skill 的工具决策用 eino tool schema）——属集成层。重定位后 tier0/tier1 = 零重量级第三方地板的层（可被零依赖核心安全依赖）。

## 日志约定

- **本仓不引入日志依赖。** tier0 加日志等于给所有下游抬地板；需要观测输出时返回 error 或交给调用方。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
