# toolname

工具名净化原语——工具名→程序内标识符的单一真相（JS 标识符判定 + 规整），装配两侧必须逐字一致

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 0 · 基础层（零仓内依赖或仅依赖同仓包） |
| oekit 对应 | `pkg/toolname（曾内嵌 oekit/pkg：v0.58.2 标记 Deprecated、v0.59.0 删除）` |
| 仓内依赖 | —（零仓内依赖） |
| 被依赖 | —（矩阵叶子） |
| 第三方地板 | 零 |
| 包数 | 1 |

## 安装

```bash
go get github.com/oagentkit/toolname@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/toolname](https://github.com/oagentkit/toolname)

## 包

| 包 | 说明 |
| --- | --- |
| `toolname` | 工具名 → 程序内标识符：IsJSIdent 判定原样可用、Normalize 给出规整名（数字开头补 _、前导非法字符跳过、已开始后记 _） |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

- **保持零依赖纯函数形态**：本包被 tier0 核心与工具治理链共同依赖，地板抬高会波及全矩阵。
- `Normalize` **不保证唯一**（`get-logs` 与 `get_logs` 同得 `get_logs`），撞名是否允许由调用方判定——本包只提供规则，不做集合级判定。
- 规整规则必须**两侧一致**：生产侧（形态派生）与消费侧（绑定挂载）共用同一套字符规则；改一边不改另一边 ⇒ 契约静默断掉（症状是「工具在目录里，程序就是调不通」）。

## 日志约定

- **本仓不引入日志依赖。** tier0 加日志等于给所有下游抬地板；需要观测输出时返回 error 或交给调用方。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
