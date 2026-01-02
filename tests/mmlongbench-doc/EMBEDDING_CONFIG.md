# Embedding 配置指南

## 错误分析

如果遇到以下错误：
```
Embedding dimension mismatch detected: total elements (1024) cannot be evenly divided by expected dimension (1536)
```

**原因**：`EMBEDDING_DIM` 配置的维度与实际 embedding 模型返回的维度不匹配。

## 常见 Embedding 模型维度

### OpenAI 模型
- `text-embedding-3-large`: **3072** 维
- `text-embedding-3-small`: **1536** 维
- `text-embedding-ada-002`: **1536** 维

### 其他供应商模型
不同供应商的 embedding 模型可能有不同的维度，常见的有：
- **1024** 维（某些供应商的模型）
- **768** 维（某些开源模型）
- **1536** 维（兼容 OpenAI 的模型）
- **3072** 维（大模型）

## 配置方法

### 1. 确定您的模型实际维度

**方法一：查看 API 文档**
- 查看您使用的 API 供应商文档，确认模型的实际维度

**方法二：测试 API 调用**
```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("EMBEDDING_BINDING_API_KEY"),
    base_url=os.getenv("EMBEDDING_BINDING_HOST")
)

response = client.embeddings.create(
    model=os.getenv("EMBEDDING_MODEL"),
    input=["test"]
)

print(f"实际维度: {len(response.data[0].embedding)}")
```

### 2. 在 .env 文件中配置

根据您的模型实际维度，设置 `EMBEDDING_DIM`：

```bash
# 如果您的模型返回 1024 维
EMBEDDING_MODEL=your-model-name
EMBEDDING_DIM=1024

# 如果您的模型返回 1536 维（如 text-embedding-3-small）
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536

# 如果您的模型返回 3072 维（如 text-embedding-3-large）
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIM=3072
```

## 重要提示

1. **EMBEDDING_DIM 必须与实际模型维度完全匹配**
   - 如果配置错误，会导致向量存储和检索失败

2. **默认值**
   - 如果未设置 `EMBEDDING_DIM`，系统默认使用 **3072**（对应 text-embedding-3-large）
   - 如果您的模型不是 3072 维，必须显式设置 `EMBEDDING_DIM`

3. **检查现有知识库**
   - 如果已经创建了知识库，修改 `EMBEDDING_DIM` 后可能需要重新创建知识库
   - 因为向量存储的维度必须一致

## 完整配置示例

```bash
# LLM 配置
LLM_MODEL=your-llm-model
LLM_BINDING_API_KEY=your-key
LLM_BINDING_HOST=https://your-api-host/v1

# Embedding 配置（根据您的模型调整）
EMBEDDING_MODEL=your-embedding-model
EMBEDDING_BINDING_API_KEY=your-key
EMBEDDING_BINDING_HOST=https://your-api-host/v1
EMBEDDING_DIM=1024  # ⚠️ 必须与模型实际维度匹配！

# 可选配置
EMBEDDING_MAX_TOKENS=8192  # 默认值，通常不需要修改
```

## 故障排除

1. **检查当前配置**
   ```bash
   echo $EMBEDDING_MODEL
   echo $EMBEDDING_DIM
   ```

2. **验证维度**
   - 使用上面的 Python 代码测试实际返回的维度
   - 确保 `EMBEDDING_DIM` 与测试结果一致

3. **重新创建知识库**
   - 如果修改了 `EMBEDDING_DIM`，可能需要删除旧的知识库并重新创建
   - 知识库路径：`./data/knowledge_bases/<kb_name>/`

