#!/bin/bash
# RAG Native 测试脚本 - 使用 RAGAnything 原生 API

set -e

# 解析参数
MAX_SAMPLES=""
START_INDEX=""
FORCE_RERUN=""

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --max_samples) MAX_SAMPLES="$2"; shift ;;
        --start_index) START_INDEX="$2"; shift ;;
        --force_rerun) FORCE_RERUN="--force_rerun" ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
    shift
done

echo "========================================"
echo "RAG Native 测试 (RAGAnything 原生 API)"
echo "========================================"

PYTHON_CMD="python test_rag_native.py"
if [ -n "$MAX_SAMPLES" ]; then
    PYTHON_CMD+=" --max_samples $MAX_SAMPLES"
fi
if [ -n "$START_INDEX" ]; then
    PYTHON_CMD+=" --start_index $START_INDEX"
fi
if [ -n "$FORCE_RERUN" ]; then
    PYTHON_CMD+=" $FORCE_RERUN"
fi

echo "运行命令: $PYTHON_CMD"
echo "========================================"

# 运行测试
set +e
eval $PYTHON_CMD
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ 测试完成"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "❌ 测试失败 (退出码: $EXIT_CODE)"
    echo "========================================"
fi

exit $EXIT_CODE

