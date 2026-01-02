# MMLongBench-Doc 测试

本目录包含用于测试 DeepTutor solve 模块在 MMLongBench-Doc 基准上的脚本。

## 目录结构

```
tests/mmlongbench-doc/
├── README.md                    # 本文件
├── test_solve_mmlongbench.py   # 主测试脚本
├── prepare_kb.py               # 知识库准备脚本（已弃用）
├── run_test.sh                 # 便捷运行脚本
├── fix_embedding_dim.sh        # 修复 Embedding 维度不匹配问题的脚本
└── test_results/               # 测试结果目录（运行后生成）
    ├── results.json            # 详细测试结果
    ├── report.txt              # 评估报告
    └── solve_outputs/         # solve 模块的输出目录
```

## 前置要求

1. **Conda 环境**
   - **重要**：所有操作必须在 `deeptutor` conda 环境中进行
   - 激活环境：`conda activate deeptutor`
   - 确保环境已安装所有必要的依赖

2. **MMLongBench-Doc 数据集**
   - 确保 `MMLongBench-Doc` 目录位于 `DeepTutor` 的父目录下
   - 或者使用 `--samples_path` 和 `--document_path` 参数指定路径

3. **环境配置**
   - **重要**：必须在项目根目录下配置 `.env` 文件，包含以下必需的环境变量：
   
   ```bash
   # LLM 配置（必需）
   LLM_MODEL=gpt-4o                    # 或其他支持的模型
   LLM_BINDING_API_KEY=your_api_key     # LLM API 密钥
   LLM_BINDING_HOST=https://api.openai.com/v1  # LLM API 地址
   
   # Embedding 配置（必需，用于知识库）
   EMBEDDING_MODEL=text-embedding-3-large      # 或其他 embedding 模型
   EMBEDDING_BINDING_API_KEY=your_api_key      # Embedding API 密钥
   EMBEDDING_BINDING_HOST=https://api.openai.com/v1  # Embedding API 地址
   EMBEDDING_DIM=3072                          # ⚠️ 重要：必须与模型实际维度匹配！
                                                # text-embedding-3-large: 3072
                                                # text-embedding-3-small: 1536
                                                # text-embedding-ada-002: 1536
                                                # 其他模型：请查看 API 文档确认维度
   
   # 答案提取配置
   # 注意：答案提取会自动使用 LLM_BINDING_API_KEY 和 LLM_BINDING_HOST
   # 支持任何兼容 OpenAI API 格式的服务提供商（如 DeepSeek、Qwen、Azure OpenAI 等）
   # 无需单独配置 OPENAI_API_KEY
   
   # 可选配置
   LLM_BINDING=openai                   # LLM 服务提供商（默认：openai）
   EMBEDDING_BINDING=openai             # Embedding 服务提供商（默认：openai）
   ```
   
   - 确保已安装所有依赖（如果未安装，运行 `pip install -r requirements.txt`）
   - 如果缺少环境变量，脚本会给出明确的错误提示

4. **知识库准备**
   - **重要**：测试脚本现在会**自动为每个文档创建独立的知识库**
   - 无需手动准备知识库，脚本会在首次处理文档时自动创建
   - 知识库命名规则：`mmlongbench_<文档名>`（去除特殊字符）

## 使用方法

### 步骤 1: 激活 Conda 环境

**重要**：所有操作必须在 `deeptutor` conda 环境中进行。

```bash
# 激活 deeptutor 环境
conda activate deeptutor

# 确认环境已激活（应该显示 (deeptutor)）
which python  # 应该指向 conda 环境的 python
```

### 步骤 2: 运行测试

**注意**：测试脚本现在会自动为每个文档创建独立的知识库，无需手动准备。

```bash
# 从项目根目录运行
cd /Users/howard/Documents/forks/DeepTutor

# 方法 1: 直接运行 Python 脚本
python tests/mmlongbench-doc/test_solve_mmlongbench.py

# 方法 2: 使用便捷脚本（推荐，会自动检查并激活 deeptutor 环境）
./tests/mmlongbench-doc/run_test.sh
```

### 参数说明

```bash
python tests/mmlongbench-doc/test_solve_mmlongbench.py \
    --samples_path ../MMLongBench-Doc/data/samples.json \
    --document_path ../MMLongBench-Doc/data/documents \
    --output_dir ./test_results \
    --kb_name mmlongbench_test \
    --max_samples 10 \
    --start_index 0
```

**参数说明：**
- `--samples_path`: samples.json 文件路径（默认：`../MMLongBench-Doc/data/samples.json`）
- `--document_path`: PDF 文档目录路径（默认：`../MMLongBench-Doc/data/documents`）
- `--output_dir`: 输出目录（默认：`./test_results`）
- `--kb_name`: 知识库名称（**已弃用**，现在每个文档使用独立知识库）
- `--max_samples`: 最大测试样本数，用于快速测试（默认：None，测试全部）
- `--start_index`: 起始索引，用于断点续传（默认：0）
- `--force`: 强制重新运行，删除旧的结果文件（如果之前运行失败，可以使用此选项重新运行）

### 快速测试

```bash
# 确保在 deeptutor 环境中
conda activate deeptutor

# 只测试前 10 个样本
python tests/mmlongbench-doc/test_solve_mmlongbench.py --max_samples 10

# 或使用便捷脚本（会自动检查环境）
./tests/mmlongbench-doc/run_test.sh --max_samples 10
```

### 断点续传

如果测试中断，可以使用 `--start_index` 参数从指定位置继续：

```bash
# 确保在 deeptutor 环境中
conda activate deeptutor

# 从第 50 个样本开始继续测试
python tests/mmlongbench-doc/test_solve_mmlongbench.py --start_index 50
```

### 重新运行测试

如果之前运行失败（例如因为环境变量未配置），可以使用 `--force` 选项强制重新运行：

```bash
# 确保在 deeptutor 环境中
conda activate deeptutor

# 强制重新运行（删除旧结果）
python tests/mmlongbench-doc/test_solve_mmlongbench.py --max_samples 10 --force

# 或使用便捷脚本
./tests/mmlongbench-doc/run_test.sh --max_samples 10 --force
```

**注意**：如果不使用 `--force`，脚本会从现有的 `results.json` 文件加载结果，这可能导致使用之前失败的结果。

## 输出说明

### results.json

包含所有测试样本的详细结果，每个样本包含：
- `question`: 问题
- `answer`: 正确答案
- `response`: solve 模块的完整响应
- `pred`: 提取的预测答案
- `score`: 评估得分（0.0-1.0）
- `extracted_res`: 答案提取的原始结果
- `output_dir`: solve 模块的输出目录
- `kb_name`: 使用的知识库名称（每个文档对应一个知识库）

### report.txt

包含评估报告，包括：
- 总体准确率和 F1 分数
- 单页问题 vs 跨页问题的准确率
- 不可回答问题（Unanswerable）的准确率
- 不同证据来源的准确率
- 不同文档类型的准确率

## 注意事项

1. **知识库管理**
   - 测试脚本会**自动为每个文档创建独立的知识库**
   - 知识库命名格式：`mmlongbench_<文档名>`（例如：`mmlongbench_PH_2016_06_08_Economy_Final`）
   - 知识库存储在 `./data/knowledge_bases/` 目录下
   - 如果文档的知识库已存在，会直接使用，不会重复创建
   - 这种方式的好处：
     - 每个文档独立处理，避免知识库过大
     - 可以更精确地测试每个文档的处理能力
     - 支持并行处理不同文档（如果未来需要）

2. **API 成本**
   - 测试会调用大量 LLM API，请注意成本
   - 建议先用 `--max_samples` 参数进行小规模测试

3. **时间消耗**
   - 每个样本的处理时间取决于问题的复杂度和文档长度
   - 完整测试可能需要数小时甚至更长时间

4. **内存使用**
   - solve 模块会为每个问题创建输出目录
   - 确保有足够的磁盘空间

## 故障排除

### 导入错误

如果遇到 `ImportError`，请确保：
1. MMLongBench-Doc 目录位于正确的位置
2. 已安装 MMLongBench-Doc 的依赖

### 知识库创建失败

如果知识库创建失败，请检查：
1. 文档路径是否正确
2. 是否有写入权限
3. 磁盘空间是否充足

知识库会在首次处理文档时自动创建，无需手动操作。

### 环境变量配置错误

如果遇到 `LLM_MODEL not set` 或 `EMBEDDING_MODEL not set` 错误：

1. 检查 `.env` 文件是否存在于项目根目录
2. 确保所有必需的环境变量都已配置：
   - `LLM_MODEL` - LLM 模型名称（如：gpt-4o）
   - `LLM_BINDING_API_KEY` - LLM API 密钥
   - `LLM_BINDING_HOST` - LLM API 地址
   - `EMBEDDING_MODEL` - Embedding 模型名称（如：text-embedding-3-large）
   - `EMBEDDING_BINDING_API_KEY` - Embedding API 密钥
   - `EMBEDDING_BINDING_HOST` - Embedding API 地址

3. 示例 `.env` 文件内容：
```bash
# LLM 配置
LLM_MODEL=gpt-4o
LLM_BINDING_API_KEY=sk-...
LLM_BINDING_HOST=https://api.openai.com/v1

# Embedding 配置
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_BINDING_API_KEY=sk-...
EMBEDDING_BINDING_HOST=https://api.openai.com/v1
EMBEDDING_DIM=3072  # ⚠️ 必须与模型维度匹配！
```

### Embedding 维度错误

如果遇到 `Embedding dimension mismatch` 错误：

1. **问题原因**：`EMBEDDING_DIM` 配置的维度与实际模型返回的维度不匹配
   - 错误示例：配置 `EMBEDDING_DIM=1536`，但模型实际返回 1024 维

2. **解决方法**：
   - 查看您使用的 embedding 模型的文档，确认实际维度
   - 在 `.env` 文件中设置正确的 `EMBEDDING_DIM`
   - 常见模型的维度：
     - `text-embedding-3-large`: 3072 维
     - `text-embedding-3-small`: 1536 维
     - `text-embedding-ada-002`: 1536 维
     - 其他供应商模型：可能是 1024、768 等，请查看文档

3. **测试实际维度**：
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

4. **重要提示**：
   - `EMBEDDING_DIM` 必须与实际模型维度完全匹配
   - 如果修改了 `EMBEDDING_DIM`，**必须删除旧知识库并重新创建**
   - 默认值：如果未设置，系统默认使用 3072（对应 text-embedding-3-large）

5. **修复维度不匹配问题**：
   
   **重要**：如果修改了 `EMBEDDING_DIM`，必须完全删除旧知识库（包括 `rag_storage` 中的向量数据），否则会出现维度不匹配错误。
   
   ```bash
   # 方法1：使用完全清理脚本（推荐）
   ./tests/mmlongbench-doc/clean_kb_completely.sh
   
   # 方法2：使用修复脚本
   ./tests/mmlongbench-doc/fix_embedding_dim.sh
   
   # 方法3：手动删除（确保删除整个知识库目录，包括 rag_storage）
   rm -rf ./data/knowledge_bases/mmlongbench_*
   ```
   
   **注意**：仅删除知识库目录可能不够，必须确保 `rag_storage` 目录也被删除，因为其中存储了使用旧维度创建的向量数据。
   
   然后重新运行测试，知识库将使用新的维度配置创建：
   ```bash
   ./tests/mmlongbench-doc/run_test.sh --force
   ```

### API 错误

如果遇到 API 错误，请检查：
1. `.env` 文件中的 API 密钥是否正确
2. API 配额是否充足
3. 网络连接是否正常
4. API 地址是否正确

