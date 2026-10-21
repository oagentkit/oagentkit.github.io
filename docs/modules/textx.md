# textx

文本与差异处理——增量切片/unified diff 解析/代码符号索引/会话滚动窗口与压缩/评审报告指纹

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 0 · 基础层（零仓内依赖或仅依赖同仓包） |
| oekit 对应 | `pkg` |
| 仓内依赖 | —（零仓内依赖） |
| 被依赖 | `promptx`、`llm`、`rag`、`skillkit`、`tools`、`agent` |
| 第三方地板 | 零 |
| 包数 | 6 |

## 安装

```bash
go get github.com/oagentkit/textx@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/textx](https://github.com/oagentkit/textx)

## 包

| 包 | 说明 |
| --- | --- |
| `textutil` | 按行边界把文本切成 ≤target(rune) 的增量片，凑片不跨行 |
| `diffx` | unified diff 解析纯函数 |
| `codeintel` | 轻量代码符号索引 |
| `compact` | 会话压缩策略面：auto-compact 判定（阈值/熔断/token 三轨）+ 压缩/恢复 |
| `conversation` | 多轮会话历史原语：滚动窗口切分、历史渲染 |
| `reportutil` | 评审/评测报告后处理：severity 归并、sampling、stats、Fingerprint 精确指纹 |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

- 保持**零仓内依赖的纯函数形态**：能用返回值表达的错误不要用回调里的副作用。
- 涉及 token / 预算的判定（如 `compact` 的三轨 auto-compact）必须有边界测试，
  阈值不得写死在实现里。

## 日志约定

- **本仓不引入日志依赖。** tier0 加日志等于给所有下游抬地板；需要观测输出时返回 error 或交给调用方。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
