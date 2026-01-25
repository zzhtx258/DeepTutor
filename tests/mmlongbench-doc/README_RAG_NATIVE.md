# RAG Native 测试

使用 RAGAnything 原生 API 直接测试 RAG 的检索和回答能力。

## 与 test_rag_direct.py 的区别

- **test_rag_direct.py**: 通过 DeepTutor 的 `src/tools/rag_tool.py` 封装调用 RAG
- **test_rag_native.py**: 直接使用 RAGAnything 的 `aquery()` 方法，完全绕过 DeepTutor 的封装层

## 特点

1. **原生 API**: 直接使用 RAGAnything 官方示例的调用方式
2. **复用知识库**: 使用已创建的知识库（`rag_storage`），无需重新处理文档
3. **独立测试**: 完全独立于 DeepTutor 的工具层，用于排查封装层问题

## 使用方法

### 基本用法

```bash
# 测试所有样本
./run_rag_native_test.sh

# 测试前 10 个样本
./run_rag_native_test.sh --max_samples 10

# 从第 50 个样本开始测试
./run_rag_native_test.sh --start_index 50

# 强制重新运行所有测试
./run_rag_native_test.sh --force_rerun
```

### 组合参数

```bash
# 测试第 10-20 个样本
./run_rag_native_test.sh --start_index 10 --max_samples 20
```

## 输出文件

- **results_rag_native.json**: 详细的测试结果（包括每个问题的答案和评分）
- **report_rag_native.txt**: 汇总报告（准确率统计）

## 知识库路径

默认使用 `../../data/knowledge_bases` 下的知识库，对应结构：
```
knowledge_bases/
├── mmlongbench_PH_2016_06_08_Economy-Final/
│   └── rag_storage/
│       ├── graph_chunk_entity_relation.graphml
│       ├── vdb_chunks.json
│       └── ...
├── mmlongbench_Independents-Report/
│   └── rag_storage/
│       └── ...
└── ...
```

## 调试

如果需要查看详细日志，修改 `test_rag_native.py` 中的日志级别：

```python
# 改为 INFO 或 DEBUG
logging.getLogger().setLevel(logging.INFO)
```

## 环境变量

确保 `.env` 文件配置了以下变量：
- `LLM_BINDING_API_KEY`: LLM API 密钥
- `LLM_BINDING_HOST`: LLM API 地址
- `LLM_MODEL`: LLM 模型名称
- `EMBEDDING_BINDING_API_KEY`: Embedding API 密钥
- `EMBEDDING_BINDING_HOST`: Embedding API 地址
- `EMBEDDING_MODEL`: Embedding 模型名称
- `EMBEDDING_DIM`: Embedding 维度

