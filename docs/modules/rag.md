# rag

知识检索与本体层——向量化/混合召回/重排（向量后端可插拔，独立子包隔离 sdk 地板）+ 实体关系本体契约与判据

## 概况

| 项 | 值 |
| --- | --- |
| 层 | tier 2 · 集成层（依赖 tier 0/1 + 重第三方地板） |
| oekit 对应 | `data` |
| 仓内依赖 | `textx` |
| 被依赖 | —（矩阵叶子） |
| 第三方地板 | `github.com/cloudwego/eino`、`github.com/milvus-io/milvus-sdk-go/v2`、`gopkg.in/yaml.v3` |
| 包数 | 6 |

## 安装

```bash
go get github.com/oagentkit/rag@latest
```

源码与该仓 `AGENTS.md`：[oagentkit/rag](https://github.com/oagentkit/rag)

## 包

| 包 | 说明 |
| --- | --- |
| `knowledge/rag` | 知识检索：Embedding 接口、向量后端可插拔、混合召回与重排 |
| `wiki` | 持久 wiki 的写入面：页面 upsert/删除/乐观版本 + 增量摄取与结构检查；不做检索（读侧索引由宿主交给 Indexer 接缝） |
| `wiki/fsstore` | wiki.Store 的文件系统参考实现：一页一个 markdown（元数据 YAML front-matter），同目录临时文件 + Rename 原子替换 |
| `milvus` | 向量后端（Milvus）实现：rag/milvus 子包——**只有它链向量 sdk**，根包零向量依赖（本地索引/混合召回调用方不必拖进 milvus 传递链） |
| `ontology` | 实体/关系本体层：Schema/Type/Field 与 Triple 契约 + Validate 判据面 + Store 接口（内存参考实现）——不做抽取、不建图库，契约与领域无关 |
| `embedtest` | Embedder 契约套件：确定性/排序一致性分级声明 + 批量单条一致 + 维度契约 + 边界 + 错误不静默（正/负对照，面向第三方实现者） |

## 本仓硬规则

以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，此处是摘要，不是替代。

- **单路召回失败不得降级为 `(nil, nil)`。** 混合召回中任一路 panic 或失败
  要作为该路失败参与裁决；全部路失败时**返回 panic 错误而非静默空结果**。
- 向量后端可插拔，新增后端不得改 `Embedding`/`Retriever` 接口形状 —— 那会让所有后端同时 breaking。
- **层位 t1 → t2**：带 `eino` + `milvus-sdk` 地板（向量化/混合召回本身绑 SDK）——属集成层。重定位后 tier0/tier1 = 零重量级第三方地板的层（可被零依赖核心安全依赖）。
- **向量后端只住 `rag/milvus` 子包**（oagentkit/rag#156）：根包不得 import 向量 sdk——否则任何 import 根包的调用方都会链接整条传递链（cockroachdb/errors、sentry-go、gogo/protobuf）。`make dep-guard` 是这条不变量的机判（反向验证过：注入即红）。
- **`rag/ontology` 是本体层的契约与判据面**（oagentkit/rag#145）：只定义 Schema/Triple/Validate/Store，**不做抽取**（提示词与领域强相关，留宿主）、**不建图数据库**（Store 接口 + 内存参考实现）；与 `wiki` 分工——wiki 页是「叙事」、ontology 是「结构」。

## 日志约定

- 日志走 `oekit/logx`，组件 logger 用 `logx.Delegating("oagentkit-rag")`。
  - 索引/检索路径不得把原始文档内容整段落日志。

## 相关

- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向
