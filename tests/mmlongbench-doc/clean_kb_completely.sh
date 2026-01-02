#!/bin/bash
# 完全清理知识库，包括所有存储数据
# 用于修复 embedding 维度不匹配问题

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# 检查并激活 conda 环境
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到 conda 命令"
    exit 1
fi

# 初始化 conda（如果尚未初始化）
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/anaconda3/etc/profile.d/conda.sh"
    fi
fi

# 激活 deeptutor 环境
if [ "$CONDA_DEFAULT_ENV" != "deeptutor" ]; then
    echo "激活 deeptutor conda 环境..."
    conda activate deeptutor || {
        echo "错误: 无法激活 deeptutor 环境"
        exit 1
    }
fi

echo "当前 Python 环境: $(which python)"
echo "Conda 环境: $CONDA_DEFAULT_ENV"
echo ""

# 检查当前配置
echo "检查当前 Embedding 配置..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv('.env')
print(f'  EMBEDDING_MODEL: {os.getenv(\"EMBEDDING_MODEL\")}')
print(f'  EMBEDDING_DIM: {os.getenv(\"EMBEDDING_DIM\", \"未设置（默认3072）\")}')
"

echo ""
echo "⚠️  警告: 将完全删除所有 mmlongbench 相关的知识库"
echo "包括所有向量存储、缓存和元数据"
echo ""
read -p "是否继续？(y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# 完全删除 mmlongbench 相关的知识库
KB_DIR="$PROJECT_ROOT/data/knowledge_bases"
if [ -d "$KB_DIR" ]; then
    echo ""
    echo "正在删除 mmlongbench 知识库..."
    
    # 查找所有 mmlongbench 知识库
    deleted_count=0
    while IFS= read -r -d '' kb_path; do
        if [ -d "$kb_path" ]; then
            kb_name=$(basename "$kb_path")
            echo "  删除: $kb_name"
            # 完全删除，包括 rag_storage、images、content_list 等所有子目录
            rm -rf "$kb_path"
            deleted_count=$((deleted_count + 1))
        fi
    done < <(find "$KB_DIR" -maxdepth 1 -type d -name "mmlongbench_*" -print0)
    
    if [ $deleted_count -eq 0 ]; then
        echo "  没有找到需要删除的知识库"
    else
        echo "✓ 已删除 $deleted_count 个知识库（包括所有存储数据）"
    fi
else
    echo "知识库目录不存在: $KB_DIR"
fi

# 更新 kb_config.json（移除已删除的知识库）
if [ -f "$KB_DIR/kb_config.json" ]; then
    echo ""
    echo "更新 kb_config.json..."
    python -c "
import json
from pathlib import Path

kb_config_file = Path('$KB_DIR/kb_config.json')
if kb_config_file.exists():
    with open(kb_config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 移除 mmlongbench 相关的知识库
    if 'knowledge_bases' in config:
        original_count = len(config['knowledge_bases'])
        config['knowledge_bases'] = {
            k: v for k, v in config['knowledge_bases'].items()
            if not k.startswith('mmlongbench_')
        }
        removed_count = original_count - len(config['knowledge_bases'])
        if removed_count > 0:
            with open(kb_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f'  ✓ 从配置中移除了 {removed_count} 个知识库')
        else:
            print('  没有需要移除的知识库')
"
fi

echo ""
echo "✓ 完成！现在可以重新运行测试，知识库将使用新的维度配置创建"
echo ""
echo "提示: 运行测试时使用 --force 选项以确保完全重新创建"
echo "  ./tests/mmlongbench-doc/run_test.sh --force"

