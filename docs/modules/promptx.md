# promptx

提示词上下文——system prompt 分段组装/运行中转向队列/文件读后写一致性状态

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 1 · 能力层（依赖 tier 0） |
| oekit 对应 | `core` |
| 仓内依赖 | `runtime`、`textx` |
| 被依赖 | —（矩阵叶子） |
| 第三方地板 | 零 |
| 包数 | 3 |

## 安装

```bash
go get github.com/oagentkit/promptx@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/promptx](https://github.com/oagentkit/promptx)

## 包

| 包 | 说明 |
| --- | --- |
| `sysprompt` | system prompt 分段组装：Section 化收集 → stable/dynamic 分离 |
| `steering` | 运行中转向队列：turn 执行中用户插入的新输入按投递语义生效 |
| `filestate` | 读后写一致性状态：编辑/覆写文件前必须读过，且读后文件未被改动 |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

- `sysprompt` 的 Section 化收集必须区分 **stable / dynamic** 两类：
  stable 段进缓存前缀，dynamic 段每轮重算。混淆会导致缓存命中率归零。

## 日志约定

- **本仓不引入日志依赖。** tier0 加日志等于给所有下游抬地板；需要观测输出时返回 error 或交给调用方。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [AI Agent 编排](/guide/ai-agent.html)
