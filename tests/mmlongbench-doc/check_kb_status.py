#!/usr/bin/env python
"""
检查知识库状态脚本

功能：
1. 列出所有 MMLongBench-Doc 文档
2. 检查每个文档对应的知识库是否存在
3. 统计已创建/未创建的知识库数量
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# 路径配置
project_root = Path(__file__).parent.parent.parent
mmlongbench_root = project_root.parent / "MMLongBench-Doc"
kb_base_dir = project_root / "data" / "knowledge_bases"

def get_kb_name_from_doc_id(doc_id: str) -> str:
    """从文档ID生成知识库名称"""
    name = doc_id.replace(".pdf", "")
    name = re.sub(r'[^\w\-_]', '_', name)
    name = re.sub(r'_+', '_', name)
    if not name.startswith("mmlongbench_"):
        name = f"mmlongbench_{name}"
    return name

def check_kb_exists(kb_name: str) -> bool:
    """检查知识库是否存在"""
    kb_dir = kb_base_dir / kb_name
    # DeepTutor 知识库的标志：存在 rag_storage 目录和 metadata.json 文件
    return kb_dir.exists() and (kb_dir / "rag_storage").exists() and (kb_dir / "metadata.json").exists()

def main():
    # 读取样本文件
    samples_path = mmlongbench_root / "data" / "samples.json"
    with open(samples_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    # 统计每个文档的样本数量
    doc_stats = defaultdict(lambda: {"total": 0, "kb_exists": False, "kb_name": ""})
    
    for sample in samples:
        doc_id = sample.get("doc_id", "")
        if doc_id:
            kb_name = get_kb_name_from_doc_id(doc_id)
            doc_stats[doc_id]["total"] += 1
            doc_stats[doc_id]["kb_name"] = kb_name
            doc_stats[doc_id]["kb_exists"] = check_kb_exists(kb_name)

    # 分类统计
    kb_exists_docs = [doc for doc, info in doc_stats.items() if info["kb_exists"]]
    kb_missing_docs = [doc for doc, info in doc_stats.items() if not info["kb_exists"]]

    # 统计样本数量
    samples_with_kb = sum(info["total"] for doc, info in doc_stats.items() if info["kb_exists"])
    samples_without_kb = sum(info["total"] for doc, info in doc_stats.items() if not info["kb_exists"])

    # 打印报告
    print("=" * 100)
    print("MMLongBench-Doc 知识库状态报告")
    print("=" * 100)
    print(f"\n总文档数: {len(doc_stats)}")
    print(f"  已创建知识库: {len(kb_exists_docs)} ({len(kb_exists_docs)/len(doc_stats)*100:.1f}%)")
    print(f"  未创建知识库: {len(kb_missing_docs)} ({len(kb_missing_docs)/len(doc_stats)*100:.1f}%)")
    
    print(f"\n总样本数: {len(samples)}")
    print(f"  有知识库的样本: {samples_with_kb} ({samples_with_kb/len(samples)*100:.1f}%)")
    print(f"  无知识库的样本: {samples_without_kb} ({samples_without_kb/len(samples)*100:.1f}%)")

    # 打印已存在知识库的文档
    if kb_exists_docs:
        print(f"\n{'='*100}")
        print(f"已创建知识库的文档 ({len(kb_exists_docs)}个):")
        print(f"{'='*100}")
        for i, doc_id in enumerate(sorted(kb_exists_docs)[:20], 1):  # 只显示前20个
            info = doc_stats[doc_id]
            print(f"{i:3d}. {doc_id[:60]:60s} | 样本数: {info['total']:3d} | KB: {info['kb_name'][:40]}")
        if len(kb_exists_docs) > 20:
            print(f"... 还有 {len(kb_exists_docs) - 20} 个文档")

    # 打印未创建知识库的文档
    if kb_missing_docs:
        print(f"\n{'='*100}")
        print(f"未创建知识库的文档 ({len(kb_missing_docs)}个):")
        print(f"{'='*100}")
        for i, doc_id in enumerate(sorted(kb_missing_docs)[:10], 1):  # 只显示前10个
            info = doc_stats[doc_id]
            print(f"{i:3d}. {doc_id[:60]:60s} | 样本数: {info['total']:3d}")
        if len(kb_missing_docs) > 10:
            print(f"... 还有 {len(kb_missing_docs) - 10} 个文档")

    # 建议
    print(f"\n{'='*100}")
    print("建议:")
    print(f"{'='*100}")
    if kb_missing_docs:
        print(f"1. 要测试所有样本，需要先运行 test_solve_mmlongbench.py 创建知识库")
        print(f"2. 或者只测试已有知识库的样本：")
        print(f"   ./run_rag_direct_test.sh  # 默认跳过没有知识库的样本")
        print(f"3. 如果要包含所有样本（会有很多失败）：")
        print(f"   ./run_rag_direct_test.sh --include_missing_kb")
    else:
        print(f"所有文档的知识库都已创建，可以直接运行测试！")

    print(f"\n知识库目录: {kb_base_dir}")

if __name__ == "__main__":
    main()

