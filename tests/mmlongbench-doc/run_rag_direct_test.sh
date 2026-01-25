#!/bin/bash

# RAG Direct 测试脚本
# 直接使用 RAGAnything (hybrid mode) 回答问题，不经过完整的 solver pipeline

set -e  # 遇到错误立即退出

# 切换到脚本所在目录
cd "$(dirname "$0")"

echo "========================================"
echo "RAG Direct 测试 (Hybrid Mode)"
echo "========================================"

# 检查 conda 环境
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "错误: 未激活 conda 环境"
    echo "请运行: conda activate deeptutor"
    exit 1
fi

if [ "$CONDA_DEFAULT_ENV" != "deeptutor" ]; then
    echo "警告: 当前环境是 $CONDA_DEFAULT_ENV，建议使用 deeptutor"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查必要的文件
if [ ! -f "../../.env" ]; then
    echo "错误: 未找到 .env 文件"
    exit 1
fi

if [ ! -f "llm_answer_evaluator.py" ]; then
    echo "错误: 未找到 llm_answer_evaluator.py"
    exit 1
fi

# 解析命令行参数
MAX_SAMPLES=""
START_INDEX=""
FORCE_RERUN=""
INCLUDE_MISSING_KB=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --max_samples)
            MAX_SAMPLES="--max_samples $2"
            shift 2
            ;;
        --start_index)
            START_INDEX="--start_index $2"
            shift 2
            ;;
        --force_rerun)
            FORCE_RERUN="--force_rerun"
            shift
            ;;
        --include_missing_kb)
            INCLUDE_MISSING_KB="--include_missing_kb"
            shift
            ;;
        *)
            echo "未知参数: $1"
            echo "用法: $0 [--max_samples N] [--start_index N] [--force_rerun] [--include_missing_kb]"
            exit 1
            ;;
    esac
done

# 构建 Python 命令
PYTHON_CMD="python test_rag_direct.py $MAX_SAMPLES $START_INDEX $FORCE_RERUN $INCLUDE_MISSING_KB"

echo "运行命令: $PYTHON_CMD"
echo "========================================"

# 运行测试并过滤日志
set +e
eval $PYTHON_CMD 2>&1 | grep -v -E "INFO|DEBUG|WARNING|Warning:|HTTP Request:|httpx|^[0-9]{4}-[0-9]{2}-[0-9]{2}"
EXIT_CODE=${PIPESTATUS[0]}
set -e

echo ""
echo "========================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 测试完成"
else
    echo "❌ 测试失败 (退出码: $EXIT_CODE)"
fi
echo "========================================"

exit $EXIT_CODE

