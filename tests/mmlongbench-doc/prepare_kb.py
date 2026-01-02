#!/usr/bin/env python
"""
准备知识库脚本：将 MMLongBench-Doc 的 PDF 文档添加到知识库

该脚本会：
1. 检查或创建知识库
2. 将 MMLongBench-Doc 的 PDF 文档添加到知识库
3. 支持增量添加（跳过已存在的文档）

注意：所有操作必须在 deeptutor conda 环境中进行
运行前请确保：conda activate deeptutor

注意：此脚本已弃用，现在测试脚本会自动为每个文档创建独立知识库
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv(project_root / ".env", override=False)

from src.knowledge.initializer import KnowledgeBaseInitializer
from src.knowledge.add_documents import DocumentAdder


def prepare_knowledge_base(
    kb_name: str,
    document_path: str,
    force_recreate: bool = False,
):
    """
    准备知识库

    Args:
        kb_name: 知识库名称
        document_path: PDF 文档目录路径
        force_recreate: 是否强制重新创建知识库
    """
    document_path = Path(document_path)

    if not document_path.exists():
        raise FileNotFoundError(f"文档目录不存在: {document_path}")

    # 检查知识库是否存在
    kb_dir = Path("./data/knowledge_bases") / kb_name
    kb_exists = kb_dir.exists()

    if force_recreate and kb_exists:
        print(f"删除现有知识库: {kb_name}")
        import shutil
        shutil.rmtree(kb_dir)

    # 创建或初始化知识库
    if not kb_exists or force_recreate:
        print(f"创建知识库: {kb_name}")
        initializer = KnowledgeBaseInitializer(
            kb_name=kb_name,
            base_dir="./data/knowledge_bases",
        )
        # 创建目录结构
        initializer.create_directory_structure()
        print("知识库目录结构创建完成")
    else:
        print(f"使用现有知识库: {kb_name}")

    # 添加文档
    print(f"\n添加文档到知识库...")
    print(f"文档目录: {document_path}")

    # 获取所有 PDF 文件
    pdf_files = list(document_path.glob("*.pdf"))
    print(f"找到 {len(pdf_files)} 个 PDF 文件")

    if not pdf_files:
        print("警告: 没有找到 PDF 文件")
        return

    # 创建 DocumentAdder
    adder = DocumentAdder(
        kb_name=kb_name,
        base_dir="./data/knowledge_bases",
    )

    # 获取已存在的文件
    existing_files = adder.get_existing_files()
    print(f"知识库中已有 {len(existing_files)} 个文件")

    # 过滤出需要添加的文件
    files_to_add = [
        str(f) for f in pdf_files if f.name not in existing_files
    ]

    if not files_to_add:
        print("所有文档已存在于知识库中")
        return

    print(f"需要添加 {len(files_to_add)} 个新文件")

    # 添加文档
    added_files = adder.add_documents(
        source_files=files_to_add,
        skip_duplicates=True,
    )

    print(f"\n成功添加 {len(added_files)} 个文档到知识库")
    print(f"知识库路径: {kb_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="准备 MMLongBench-Doc 测试知识库"
    )
    parser.add_argument(
        "--kb_name",
        type=str,
        default="mmlongbench_test",
        help="知识库名称",
    )
    parser.add_argument(
        "--document_path",
        type=str,
        default="../MMLongBench-Doc/data/documents",
        help="PDF 文档目录路径",
    )
    parser.add_argument(
        "--force_recreate",
        action="store_true",
        help="强制重新创建知识库（会删除现有知识库）",
    )

    args = parser.parse_args()

    try:
        prepare_knowledge_base(
            kb_name=args.kb_name,
            document_path=args.document_path,
            force_recreate=args.force_recreate,
        )
        print("\n知识库准备完成！")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

