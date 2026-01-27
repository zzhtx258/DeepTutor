#!/usr/bin/env python
"""
Test script for Multi-KB RAG Search

Tests the multi_kb_rag_search function with different configurations.

Usage:
    python scripts/test_multi_kb_rag.py [--kb-dir PATH] [--query "your query"]
    
Examples:
    # Use default knowledge bases directory
    python scripts/test_multi_kb_rag.py
    
    # Use custom knowledge bases directory
    python scripts/test_multi_kb_rag.py --kb-dir /path/to/knowledge_bases
    
    # Custom query
    python scripts/test_multi_kb_rag.py --query "What is deep learning?"
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.multi_kb_rag_tool import multi_kb_rag_search
from src.knowledge.manager import KnowledgeBaseManager


async def test_list_knowledge_bases(kb_base_dir: str = None):
    """Test listing available knowledge bases"""
    print("=" * 60)
    print("1. Listing available knowledge bases")
    print("=" * 60)
    
    if kb_base_dir is None:
        kb_base_dir = str(project_root / "data" / "knowledge_bases")
    
    print(f"Knowledge bases directory: {kb_base_dir}")
    kb_manager = KnowledgeBaseManager(kb_base_dir)
    kb_list = kb_manager.list_knowledge_bases()
    
    print(f"Found {len(kb_list)} knowledge bases:")
    for kb in kb_list:
        print(f"  - {kb}")
    print()
    
    return kb_list, kb_base_dir


async def test_multi_kb_search_simple(query: str, kb_names: list[str] | None = None, kb_base_dir: str = None):
    """Test simple format (merged context)"""
    print("=" * 60)
    print("2. Testing Multi-KB Search (Simple Format)")
    print("=" * 60)
    print(f"Query: {query}")
    print(f"Knowledge bases: {kb_names or 'ALL'}")
    print()
    
    try:
        result = await multi_kb_rag_search(
            query=query,
            kb_names=kb_names,
            top_k_per_kb=10,
            final_top_k=5,
            mode="naive",
            return_detailed=False,
            kb_base_dir=kb_base_dir,
        )
        
        print(f"Source KBs: {result.get('source_kbs', [])}")
        print(f"Mode: {result.get('mode')}")
        print()
        print("Answer (merged context):")
        print("-" * 40)
        answer = result.get("answer", "")
        # Truncate if too long
        if len(answer) > 2000:
            print(answer[:2000] + "\n... [truncated]")
        else:
            print(answer if answer else "(empty)")
        print()
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_multi_kb_search_detailed(query: str, kb_names: list[str] | None = None, kb_base_dir: str = None):
    """Test detailed format (with scores)"""
    print("=" * 60)
    print("3. Testing Multi-KB Search (Detailed Format)")
    print("=" * 60)
    print(f"Query: {query}")
    print(f"Knowledge bases: {kb_names or 'ALL'}")
    print()
    
    try:
        result = await multi_kb_rag_search(
            query=query,
            kb_names=kb_names,
            top_k_per_kb=10,
            final_top_k=5,
            mode="naive",
            return_detailed=True,
            kb_base_dir=kb_base_dir,
        )
        
        print(f"Source KBs: {result.get('source_kbs', [])}")
        print(f"Mode: {result.get('mode')}")
        print()
        
        results = result.get("results", [])
        print(f"Retrieved {len(results)} chunks after reranking:")
        print("-" * 40)
        
        for i, r in enumerate(results):
            print(f"\n[{i+1}] KB: {r.get('source_kb')} | Rerank Score: {r.get('rerank_score', 0):.4f}")
            content = r.get("content", "")
            # Truncate content for display
            if len(content) > 300:
                print(f"    {content[:300]}...")
            else:
                print(f"    {content}")
        
        print()
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_single_kb(query: str, kb_name: str, kb_base_dir: str = None):
    """Test with a single specific knowledge base"""
    print("=" * 60)
    print(f"4. Testing Single KB Search: {kb_name}")
    print("=" * 60)
    print(f"Query: {query}")
    print()
    
    try:
        result = await multi_kb_rag_search(
            query=query,
            kb_names=[kb_name],
            top_k_per_kb=10,
            final_top_k=5,
            mode="naive",
            return_detailed=True,
            kb_base_dir=kb_base_dir,
        )
        
        print(f"Source KBs: {result.get('source_kbs', [])}")
        results = result.get("results", [])
        print(f"Retrieved {len(results)} chunks")
        
        if results:
            print(f"\nTop result (score: {results[0].get('rerank_score', 0):.4f}):")
            print("-" * 40)
            content = results[0].get("content", "")
            if len(content) > 500:
                print(content[:500] + "...")
            else:
                print(content)
        
        print()
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main(kb_base_dir: str = None, test_query: str = None):
    """Main test function"""
    print("\n" + "=" * 60)
    print("Multi-KB RAG Search Test")
    print("=" * 60 + "\n")
    
    # 1. List available knowledge bases
    kb_list, kb_base_dir = await test_list_knowledge_bases(kb_base_dir)
    
    if not kb_list:
        print("No knowledge bases found.")
        print("\nTo create a knowledge base, run:")
        print("  python scripts/init_kb_from_content_list.py --help")
        print("\nOr specify a custom directory with --kb-dir")
        return
    
    # Default test query
    if test_query is None:
        test_query = "什么是机器学习？"  # "What is machine learning?"
    
    # 2. Test with all KBs (simple format)
    await test_multi_kb_search_simple(test_query, kb_base_dir=kb_base_dir)
    
    # 3. Test with all KBs (detailed format)
    await test_multi_kb_search_detailed(test_query, kb_base_dir=kb_base_dir)
    
    # 4. Test with first KB only
    if kb_list:
        await test_single_kb(test_query, kb_list[0], kb_base_dir=kb_base_dir)
    
    print("=" * 60)
    print("Test completed!")
    print("=" * 60)


def parse_args():
    parser = argparse.ArgumentParser(description="Test Multi-KB RAG Search")
    parser.add_argument(
        "--kb-dir",
        type=str,
        default=None,
        help="Knowledge bases directory path",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Test query string",
    )
    return parser.parse_args()


if __name__ == "__main__":
    # Handle Windows encoding
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    
    args = parse_args()
    asyncio.run(main(kb_base_dir=args.kb_dir, test_query=args.query))
