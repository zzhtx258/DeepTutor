#!/usr/bin/env python
"""
从已有的 content list 初始化知识库（跳过 MinerU 解析）

用法:
    python scripts/init_kb_from_content_list.py

这个脚本会:
1. 读取 hybrid_auto 文件夹中的 content_list.json
2. 创建名为 "calc" 的知识库
3. 直接插入 content list 到 LightRAG（跳过 PDF 解析）
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 添加 RAG-Anything 路径
raganything_path = project_root.parent / "RAG-Anything"
if raganything_path.exists():
    sys.path.insert(0, str(raganything_path))

from dotenv import load_dotenv
load_dotenv(dotenv_path=project_root / ".env", override=False)

from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from raganything import RAGAnything, RAGAnythingConfig

# ============== 配置 ==============
KB_NAME = "calc"  # 知识库名称
CONTENT_LIST_PATH = Path("/Users/howard/Documents/forks/hybrid_auto/calculus1-3_content_list.json")
IMAGES_DIR = Path("/Users/howard/Documents/forks/hybrid_auto/images")
SOURCE_FILE_NAME = "calculus1-3.pdf"  # 用于引用的源文件名

# 知识库输出目录
KB_BASE_DIR = project_root / "data" / "knowledge_bases"
# ================================


def get_env_config():
    """获取环境变量配置"""
    return {
        "api_key": os.environ.get("LLM_BINDING_API_KEY", ""),
        "base_url": os.environ.get("LLM_BINDING_HOST", ""),
        "llm_model": os.environ.get("LLM_BINDING_MODEL", "qwen-plus"),
        "embed_model": os.environ.get("EMBEDDING_MODEL", "text-embedding-v3"),
        "embed_dim": int(os.environ.get("EMBEDDING_DIM", "1024")),
    }


def fix_image_paths(content_list: list, images_dir: Path) -> list:
    """
    修复 content list 中的图片路径为绝对路径
    """
    fixed_list = []
    for item in content_list:
        if item.get("type") == "image":
            img_path = item.get("img_path", "")
            if img_path and not os.path.isabs(img_path):
                # 转换为绝对路径
                abs_path = str(images_dir / Path(img_path).name)
                item = item.copy()
                item["img_path"] = abs_path
        fixed_list.append(item)
    return fixed_list


async def init_knowledge_base():
    """初始化知识库"""
    print("\n" + "=" * 60)
    print(f"🚀 从 Content List 初始化知识库: {KB_NAME}")
    print("=" * 60 + "\n")
    
    # 1. 检查 content list 文件
    if not CONTENT_LIST_PATH.exists():
        print(f"❌ Content list 文件不存在: {CONTENT_LIST_PATH}")
        return
    
    print(f"📄 Content List: {CONTENT_LIST_PATH}")
    print(f"🖼️  Images Dir: {IMAGES_DIR}")
    
    # 2. 读取 content list
    print("\n📖 读取 content list...")
    with open(CONTENT_LIST_PATH, "r", encoding="utf-8") as f:
        content_list = json.load(f)
    
    print(f"   总条目数: {len(content_list)}")
    
    # 统计内容类型
    type_counts = {}
    for item in content_list:
        t = item.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    print(f"   类型分布: {type_counts}")
    
    # 3. 修复图片路径
    print("\n🔧 修复图片路径...")
    content_list = fix_image_paths(content_list, IMAGES_DIR)
    
    # 4. 创建知识库目录
    kb_dir = KB_BASE_DIR / KB_NAME
    rag_storage_dir = kb_dir / "rag_storage"
    rag_storage_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 知识库目录: {kb_dir}")
    
    # 5. 获取 API 配置
    env_config = get_env_config()
    api_key = env_config["api_key"]
    base_url = env_config["base_url"]
    llm_model = env_config["llm_model"]
    embed_model = env_config["embed_model"]
    embed_dim = env_config["embed_dim"]
    
    if not api_key:
        print("❌ 未设置 LLM_BINDING_API_KEY 环境变量")
        return
    
    print(f"\n⚙️  LLM Model: {llm_model}")
    print(f"⚙️  Embed Model: {embed_model}")
    print(f"⚙️  Embed Dim: {embed_dim}")
    
    # 6. 配置 RAGAnything
    config = RAGAnythingConfig(
        working_dir=str(rag_storage_dir),
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )
    
    # 7. 定义 LLM 函数
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return openai_complete_if_cache(
            llm_model,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )
    
    # 8. 定义 Vision Model 函数（支持 image_data 和 messages 参数）
    def vision_model_func(
        prompt,
        system_prompt=None,
        history_messages=[],
        image_data=None,
        messages=None,
        **kwargs,
    ):
        # 清理 kwargs 中的重复参数
        clean_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k not in ["messages", "prompt", "system_prompt", "history_messages"]
        }
        
        # 如果提供了 messages 格式，直接使用
        if messages:
            return openai_complete_if_cache(
                llm_model,
                prompt="",
                system_prompt=None,
                history_messages=[],
                messages=messages,
                api_key=api_key,
                base_url=base_url,
                **clean_kwargs,
            )
        
        # 如果提供了 image_data（base64 编码的图片）
        if image_data:
            vision_messages = []
            if system_prompt:
                vision_messages.append({"role": "system", "content": system_prompt})
            vision_messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        },
                    },
                ],
            })
            return openai_complete_if_cache(
                llm_model,
                prompt="",
                system_prompt=None,
                history_messages=[],
                messages=vision_messages,
                api_key=api_key,
                base_url=base_url,
                **clean_kwargs,
            )
        
        # 纯文本格式
        return llm_model_func(prompt, system_prompt, history_messages, **kwargs)
    
    async def embedding_func(texts):
        return await openai_embed(
            texts,
            model=embed_model,
            api_key=api_key,
            base_url=base_url,
        )
    
    # 9. 创建 RAGAnything 实例
    print("\n🔄 初始化 RAGAnything...")
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,  # 使用支持 image_data 的 vision 函数
        embedding_func=EmbeddingFunc(
            embedding_dim=embed_dim,
            max_token_size=8192,
            func=embedding_func,
        ),
    )
    
    # 10. 初始化 LightRAG
    print("🔄 初始化 LightRAG...")
    await rag._ensure_lightrag_initialized()
    
    # 11. 插入 content list（跳过 MinerU 解析！）
    print(f"\n📥 插入 content list 到知识库...")
    print(f"   这可能需要一些时间，请耐心等待...")
    
    start_time = datetime.now()
    
    await rag.insert_content_list(
        content_list=content_list,
        file_path=SOURCE_FILE_NAME,
        display_stats=True,
    )
    
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n⏱️  耗时: {elapsed:.1f} 秒")
    
    # 12. 创建 metadata.json
    metadata = {
        "kb_name": KB_NAME,
        "created_at": datetime.now().isoformat(),
        "source_file": SOURCE_FILE_NAME,
        "content_list_path": str(CONTENT_LIST_PATH),
        "total_items": len(content_list),
        "type_distribution": type_counts,
        "initialization_method": "content_list_direct",
    }
    
    metadata_path = kb_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 知识库初始化完成!")
    print(f"   知识库路径: {kb_dir}")
    print(f"   RAG 存储: {rag_storage_dir}")
    print(f"   Metadata: {metadata_path}")
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(init_knowledge_base())
