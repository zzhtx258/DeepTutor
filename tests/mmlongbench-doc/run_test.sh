#!/bin/bash
# MMLongBench-Doc 测试运行脚本
# 注意：所有操作必须在 deeptutor conda 环境中进行

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# 检查并激活 conda 环境
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到 conda 命令"
    echo "请确保已安装 conda 并配置好环境"
    exit 1
fi

# 初始化 conda（如果尚未初始化）
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    # 尝试初始化 conda
    if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/anaconda3/etc/profile.d/conda.sh"
    else
        echo "警告: 无法自动初始化 conda，请手动运行: conda activate deeptutor"
    fi
fi

# 激活 deeptutor 环境
if [ "$CONDA_DEFAULT_ENV" != "deeptutor" ]; then
    echo "激活 deeptutor conda 环境..."
    conda activate deeptutor || {
        echo "错误: 无法激活 deeptutor 环境"
        echo "请确保已创建 deeptutor 环境: conda create -n deeptutor python=3.10"
        exit 1
    }
fi

echo "当前 Python 环境: $(which python)"
echo "Conda 环境: $CONDA_DEFAULT_ENV"

# 默认参数（注意：kb_name 已弃用，现在每个文档使用独立知识库）
KB_NAME=""
SAMPLES_PATH="../MMLongBench-Doc/data/samples.json"
DOCUMENT_PATH="../MMLongBench-Doc/data/documents"
OUTPUT_DIR="./tests/mmlongbench-doc/test_results"
MAX_SAMPLES=""
START_INDEX="0"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --kb_name)
            echo "警告: --kb_name 参数已弃用，现在每个文档使用独立知识库"
            KB_NAME="$2"
            shift 2
            ;;
        --samples_path)
            SAMPLES_PATH="$2"
            shift 2
            ;;
        --document_path)
            DOCUMENT_PATH="$2"
            shift 2
            ;;
        --output_dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --max_samples)
            MAX_SAMPLES="$2"
            shift 2
            ;;
        --start_index)
            START_INDEX="$2"
            shift 2
            ;;
        --force)
            FORCE_RERUN="--force"
            shift
            ;;
        --prepare_kb)
            echo "准备知识库..."
            echo "注意: 现在每个文档使用独立知识库，无需手动准备"
            echo "脚本会在首次处理文档时自动创建知识库"
            exit 0
            ;;
        --help)
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --kb_name NAME          知识库名称 (已弃用，现在每个文档使用独立知识库)"
            echo "  --samples_path PATH      samples.json 路径 (默认: $SAMPLES_PATH)"
            echo "  --document_path PATH     PDF 文档目录路径 (默认: $DOCUMENT_PATH)"
            echo "  --output_dir DIR         输出目录 (默认: $OUTPUT_DIR)"
            echo "  --max_samples N          最大测试样本数"
            echo "  --start_index N          起始索引 (用于断点续传)"
            echo "  --prepare_kb             准备知识库（添加 PDF 文档）"
            echo "  --help                   显示此帮助信息"
            echo ""
            echo "示例:"
            echo "  # 注意: 测试脚本会自动为每个文档创建独立知识库，无需手动准备"
            echo ""
            echo "  # 快速测试（前 10 个样本）"
            echo "  $0 --max_samples 10"
            echo ""
            echo "  # 完整测试"
            echo "  $0"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            echo "使用 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

# 构建 Python 命令
PYTHON_CMD="python tests/mmlongbench-doc/test_solve_mmlongbench.py"
if [ -n "$KB_NAME" ]; then
    PYTHON_CMD="$PYTHON_CMD --kb_name $KB_NAME"
fi
PYTHON_CMD="$PYTHON_CMD --samples_path $SAMPLES_PATH"
PYTHON_CMD="$PYTHON_CMD --document_path $DOCUMENT_PATH"
PYTHON_CMD="$PYTHON_CMD --output_dir $OUTPUT_DIR"
PYTHON_CMD="$PYTHON_CMD --start_index $START_INDEX"

if [ -n "$MAX_SAMPLES" ]; then
    PYTHON_CMD="$PYTHON_CMD --max_samples $MAX_SAMPLES"
fi

if [ -n "$FORCE_RERUN" ]; then
    PYTHON_CMD="$PYTHON_CMD $FORCE_RERUN"
fi

# 运行测试
echo "运行测试..."
echo "命令: $PYTHON_CMD"
echo ""

eval $PYTHON_CMD

