# tools

外部工具接入——CLI 编码 agent 统一调用/公开资料检索/git 工作副本沙箱/确定性 SAST 扫描

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 2 · 集成层（依赖 tier 0/1 + 重第三方地板） |
| oekit 对应 | `kitex-examples` |
| 仓内依赖 | `guardx`、`runtime`、`textx` |
| 被依赖 | —（矩阵叶子） |
| 第三方地板 | `github.com/cloudwego/eino` |
| 包数 | 4 |

## 安装

```bash
go get github.com/oagentkit/tools@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/tools](https://github.com/oagentkit/tools)

## 包

| 包 | 说明 |
| --- | --- |
| `acpx` | CLI 编码 agent 统一调用（claude / codex / gemini / kimi / mcode 等） |
| `websearch` | 公开资料检索抽象，接口可插拔（缺省 SearXNG 自建实例） |
| `workcopy` | Git 工作副本沙箱：隔离环境 + merge-base 校验 |
| `sast` | 确定性 SAST 前置扫描（不执行被扫代码） |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

- **CLI 编码 agent 调用必须隔离环境**（用 `runtime.ChildEnv` 构造最小环境），
  不得继承完整宿主环境 —— 凭据泄漏面。
- `workcopy` 的 git 操作必须限制在沙箱目录内，`EnsureMergeBase` 失败要显式报错，
  不得跳过继续。
- SAST 扫描是**确定性前置扫描**，不执行被扫代码。

## 日志约定

- 日志走 `oekit/logx`，组件 logger 用 `logx.Delegating("oagentkit-tools")`。
- 子进程输出落日志前过 `guardx/logredact` —— 外部 CLI 的输出不可信。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
- [工具接入与治理](/guide/tools-and-mcp.html)
