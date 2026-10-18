# rag

知识检索——向量化/混合召回/重排，向量后端可插拔

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 1 · 能力层（依赖 tier 0） |
| oekit 对应 | `data` |
| 仓内依赖 | `textx` |
| 被依赖 | —（矩阵叶子） |
| 第三方地板 | `github.com/cloudwego/eino`、`github.com/milvus-io/milvus-sdk-go/v2` |
| 包数 | 1 |

## 安装

```bash
go get github.com/oagentkit/rag@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/rag](https://github.com/oagentkit/rag)

## 包

| 包 | 说明 |
| --- | --- |
| `knowledge/rag` | 知识检索：Embedding 接口、向量后端可插拔、混合召回与重排 |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

- **单路召回失败不得降级为 `(nil, nil)`。** 混合召回中任一路 panic 或失败
  要作为该路失败参与裁决；全部路失败时**返回 panic 错误而非静默空结果**。
- 向量后端可插拔，新增后端不得改 `Embedding`/`Retriever` 接口形状 —— 那会让所有后端同时 breaking。

## 日志约定

- **本仓不引入日志依赖。** tier0 加日志等于给所有下游抬地板；需要观测输出时返回 error 或交给调用方。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
