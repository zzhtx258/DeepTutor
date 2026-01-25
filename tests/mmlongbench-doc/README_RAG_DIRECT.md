# RAG Direct 测试

## 概述

`test_rag_direct.py` 是一个简化的测试脚本，用于评估 RAGAnything (hybrid mode) 的基础检索能力。

与 `test_solve_mmlongbench.py` 的区别：
- **不使用完整的 solver pipeline**（不经过 investigate/solve/manager agents）
- **直接调用 RAG hybrid 搜索**获取答案
- **更快速**，适合快速评估 RAG 的检索质量
- **更简单**，减少了中间处理环节

## 使用场景

1. 快速评估 RAG 的基础检索能力
2. 对比 RAG 直接输出 vs Solver 处理后的输出
3. 识别 RAG 检索的瓶颈（vs Agent 推理的瓶颈）

## 前置条件

### 1. 激活 conda 环境
```bash
conda activate deeptutor
```

### 2. 确保知识库已存在

测试脚本会使用 `test_solve_mmlongbench.py` 创建的知识库，路径格式：
```
DeepTutor/data/knowledge_bases/mmlongbench_<doc_id>/
```

如果知识库不存在，脚本会跳过该样本并标记错误。

### 3. 环境变量配置

确保 `.env` 文件包含：
```bash
LLM_API_KEY=your_api_key
LLM_BASE_URL=your_base_url
LLM_MODEL=gpt-4o  # 或其他模型
```

## 使用方法

### 基本用法

```bash
# 使用 shell 脚本运行（推荐）
./run_rag_direct_test.sh

# 或直接运行 Python 脚本
python test_rag_direct.py
```

### 高级选项

```bash
# 只测试前 10 个样本
./run_rag_direct_test.sh --max_samples 10

# 从第 50 个样本开始测试
./run_rag_direct_test.sh --start_index 50

# 强制重新运行所有测试（忽略已有结果）
./run_rag_direct_test.sh --force_rerun

# 组合使用
./run_rag_direct_test.sh --max_samples 20 --start_index 10
```

### Python 脚本参数

```bash
python test_rag_direct.py \
    --samples <样本文件路径> \
    --results <结果文件路径> \
    --kb_dir <知识库目录> \
    --max_samples <最大样本数> \
    --start_index <起始索引> \
    --force_rerun
```

## 输出结果

### 1. 实时输出

测试过程中会显示：
- 当前处理的问题
- RAG 输出的答案
- 正确答案
- 评估得分
- 累计准确率

示例：
```
📝 问题: What year is the report for?
💬 RAG输出: The report covers fiscal year 2015-2016.
✓  正确: 2015-2016
✅ 得分: 1.0
📊 累计准确率: 45.00% (9/20)
```

### 2. 结果文件

**位置**: `test_results/results_rag_direct.json`

**格式**:
```json
[
  {
    "question": "What year is the report for?",
    "answer": "2015-2016",
    "doc_id": "fdac8d1e9ef56519371df7e6532df27d.pdf",
    "response": "The report covers fiscal year 2015-2016.",
    "score": 1.0,
    "llm_reasoning": "The generated answer correctly identifies...",
    "kb_name": "mmlongbench_fdac8d1e9ef56519371df7e6532df27d",
    "rag_sources": [...]
  }
]
```

### 3. 评估报告

**位置**: `test_results/report_rag_direct.txt`

**内容**:
```
================================================================================
RAG Direct 测试报告 (Hybrid Mode)
生成时间: 2026-01-07 12:30:45
================================================================================
Overall Accuracy: 0.4500 | Question Number: 40
Correct: 18 | Incorrect: 22

按知识库统计:
  mmlongbench_fdac8d1e9ef56519371df7e6532df27d: Accuracy: 0.5000 | Questions: 10
  mmlongbench_earlybird_110722143746_phpapp02_95: Accuracy: 0.4000 | Questions: 15
  ...
```

## 与 Solver 测试对比

| 特性 | RAG Direct | Solver Pipeline |
|------|-----------|----------------|
| 测试脚本 | `test_rag_direct.py` | `test_solve_mmlongbench.py` |
| 处理流程 | 直接 RAG 搜索 | Investigate → Solve → Response |
| 速度 | 快 (~5s/问题) | 慢 (~30s/问题) |
| 准确率 | 较低（基础检索） | 较高（经过推理） |
| 适用场景 | 评估检索质量 | 评估完整系统 |

## 故障排查

### 1. 知识库不存在

**错误**:
```
⚠️  知识库不存在: mmlongbench_xxx
```

**解决**:
先运行 `test_solve_mmlongbench.py` 创建知识库，或手动创建知识库。

### 2. RAG 搜索失败

**错误**:
```
❌ 处理失败: RAG search failed
```

**解决**:
- 检查知识库目录结构是否完整
- 检查 `vdb_entities.json` 是否存在
- 检查 API 配置是否正确

### 3. 评估失败

**错误**:
```
LLM评估失败: Connection timeout
```

**解决**:
- 检查网络连接
- 检查 LLM API 配置
- 增加超时时间

## 注意事项

1. **知识库格式兼容性**: 
   - 脚本会自动使用 `mmlongbench_<doc_id>` 格式的知识库
   - 确保知识库是由 DeepTutor 系统创建的

2. **结果可恢复**:
   - 测试结果会实时保存到 `results_rag_direct.json`
   - 如果测试中断，下次运行会自动跳过已完成的样本
   - 使用 `--force_rerun` 强制重新测试

3. **评估模型**:
   - 使用与 `test_solve_mmlongbench.py` 相同的 LLM-as-a-Judge
   - 确保评估标准一致

## 示例工作流

```bash
# 1. 先运行完整 Solver 测试（创建知识库 + 评估）
./run_test.sh --max_samples 50

# 2. 运行 RAG Direct 测试（使用相同知识库）
./run_rag_direct_test.sh --max_samples 50

# 3. 对比两个结果文件
# - test_results/results.json (Solver)
# - test_results/results_rag_direct.json (RAG Direct)

# 4. 分析差异
python analyze_rag_vs_solver.py  # 需要自己创建分析脚本
```

## 开发说明

### 代码结构

- `RAGDirectTester`: 主测试类
  - `_load_samples()`: 加载样本并恢复进度
  - `_check_kb_exists()`: 检查知识库是否存在
  - `_extract_answer_from_rag()`: 从 RAG 结果提取答案
  - `test_sample()`: 测试单个样本
  - `run_tests()`: 运行所有测试
  - `_save_results()`: 保存结果
  - `_generate_report()`: 生成报告

### 扩展建议

1. 添加多种 RAG 模式对比（naive/hybrid/local/global）
2. 添加检索结果详细分析（sources 质量）
3. 添加错误案例分析工具
4. 支持批量并行处理

## 许可证

与 DeepTutor 主项目相同

