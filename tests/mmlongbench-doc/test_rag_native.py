#!/usr/bin/env python
"""
使用 RAGAnything 原生 API 测试 MMLongBench-Doc 问题

直接使用 RAGAnything 的 aquery() 方法，不经过 DeepTutor 的封装
复用已有的知识库（rag_storage）
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加 RAGAnything 路径
raganything_path = project_root.parent / "RAG-Anything"
sys.path.insert(0, str(raganything_path))

from dotenv import load_dotenv
from tqdm import tqdm

# 加载环境变量
load_dotenv(project_root / ".env", override=False)

from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from raganything import RAGAnything, RAGAnythingConfig

# 导入 LLM 评估模块
sys.path.insert(0, str(Path(__file__).parent))
from llm_answer_evaluator import LLMAnswerEvaluator

# 抑制日志
logging.getLogger().setLevel(logging.ERROR)
for logger_name in ["httpx", "httpcore", "openai", "urllib3", "asyncio", "lightrag", "raganything"]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

# MMLongBench-Doc 数据路径
mmlongbench_root = project_root.parent / "MMLongBench-Doc"


class LLMEvaluatorConfig:
    """LLM评估器配置"""
    def __init__(self, output_dir: str, api_key: str, base_url: str, model: str = "gpt-4o", quiet: bool = False):
        self.output_dir = output_dir
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.quiet = quiet


class RAGNativeTester:
    """RAGAnything 原生 API 测试器"""

    def __init__(
        self,
        samples_path: str,
        results_file: str,
        kb_base_dir: str,
        max_samples: int = None,
        start_index: int = 0,
        force_rerun: bool = False,
    ):
        self.samples_path = Path(samples_path)
        self.results_file = Path(results_file)
        self.kb_base_dir = Path(kb_base_dir)
        self.max_samples = max_samples
        self.start_index = start_index
        self.force_rerun = force_rerun

        # 加载样本
        self.samples = self._load_samples()
        
        # LLM 评估器配置
        self.llm_evaluator = self._init_llm_evaluator()
        
        # RAG 实例缓存（每个知识库一个）
        self.rag_instances = {}
        
        # 首次查询标记
        self._first_query = True

    def _init_llm_evaluator(self):
        """初始化 LLM 评估器"""
        llm_api_key = os.getenv("LLM_BINDING_API_KEY")
        llm_base_url = os.getenv("LLM_BINDING_HOST")
        llm_model = os.getenv("LLM_MODEL", "qwen-plus")
        
        config = LLMEvaluatorConfig(
            output_dir=str(self.results_file.parent),
            api_key=llm_api_key,
            base_url=llm_base_url,
            model=llm_model,
            quiet=True
        )
        return LLMAnswerEvaluator(config)

    def _load_samples(self) -> List[Dict[str, Any]]:
        """加载测试样本"""
        # 从原始 samples.json 加载所有样本
        with open(self.samples_path, "r", encoding="utf-8") as f:
            all_samples = json.load(f)

        # 如果指定了 max_samples，则截断
        if self.max_samples:
            all_samples = all_samples[: self.max_samples]

        # 加载已完成的结果（如果存在）
        completed_results_map = {}
        if self.results_file.exists():
            print(f"从现有结果文件加载: {self.results_file}")
            with open(self.results_file, "r", encoding="utf-8") as f:
                existing_results = json.load(f)
                for res in existing_results:
                    key = (res.get("question"), res.get("doc_id"))
                    completed_results_map[key] = res

        # 合并已完成的结果
        for i, sample in enumerate(all_samples):
            key = (sample.get("question"), sample.get("doc_id"))
            if key in completed_results_map:
                all_samples[i] = completed_results_map[key]

        # 过滤掉没有知识库的样本
        filtered_samples = []
        skipped_count = 0
        for sample in all_samples:
            kb_name = self._get_kb_name_from_doc_id(sample["doc_id"])
            if self._check_kb_exists(kb_name):
                filtered_samples.append(sample)
            else:
                skipped_count += 1
        
        if skipped_count > 0:
            print(f"⚠️  跳过 {skipped_count} 个没有知识库的样本")
        
        all_samples = filtered_samples

        # 从指定索引开始
        if self.start_index > 0 and not self.force_rerun:
            all_samples = all_samples[self.start_index:]

        print(f"加载了 {len(all_samples)} 个测试样本")
        return all_samples

    def _save_results(self):
        """保存结果到 JSON 文件"""
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump(self.samples, f, ensure_ascii=False, indent=2)

    def _get_kb_name_from_doc_id(self, doc_id: str) -> str:
        """从 doc_id 获取知识库名称"""
        import re
        # 移除 .pdf 扩展名
        name = doc_id.replace(".pdf", "")
        # 替换特殊字符为下划线
        name = re.sub(r'[^\w\-_]', '_', name)
        # 移除连续的下划线
        name = re.sub(r'_+', '_', name)
        # 确保以 mmlongbench_ 开头
        if not name.startswith("mmlongbench_"):
            name = f"mmlongbench_{name}"
        return name

    def _check_kb_exists(self, kb_name: str) -> bool:
        """检查知识库是否存在"""
        kb_path = self.kb_base_dir / kb_name
        rag_storage_path = kb_path / "rag_storage"
        metadata_file = kb_path / "metadata.json"
        return rag_storage_path.is_dir() and metadata_file.is_file()

    async def _get_rag_instance(self, kb_name: str) -> RAGAnything:
        """获取或创建 RAG 实例"""
        if kb_name in self.rag_instances:
            return self.rag_instances[kb_name]

        # 创建新的 RAG 实例
        working_dir = str(self.kb_base_dir / kb_name / "rag_storage")
        
        if not Path(working_dir).exists():
            raise ValueError(f"知识库不存在: {working_dir}")

        # 配置
        config = RAGAnythingConfig(
            working_dir=working_dir,
            parser="mineru",
            parse_method="auto",
            enable_image_processing=True,
            enable_table_processing=True,
            enable_equation_processing=True,
        )

        # LLM 配置
        api_key = os.getenv("LLM_BINDING_API_KEY")
        base_url = os.getenv("LLM_BINDING_HOST")
        model = os.getenv("LLM_MODEL", "qwen-plus")

        def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
            return openai_complete_if_cache(
                model,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                api_key=api_key,
                base_url=base_url,
                **kwargs,
            )

        def vision_model_func(
            prompt,
            system_prompt=None,
            history_messages=[],
            image_data=None,
            messages=None,
            **kwargs,
        ):
            if messages:
                return openai_complete_if_cache(
                    model,
                    "",
                    system_prompt=None,
                    history_messages=[],
                    messages=messages,
                    api_key=api_key,
                    base_url=base_url,
                    **kwargs,
                )
            elif image_data:
                return openai_complete_if_cache(
                    model,
                    "",
                    system_prompt=None,
                    history_messages=[],
                    messages=[
                        {"role": "system", "content": system_prompt} if system_prompt else None,
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                                },
                            ],
                        }
                        if image_data
                        else {"role": "user", "content": prompt},
                    ],
                    api_key=api_key,
                    base_url=base_url,
                    **kwargs,
                )
            else:
                return llm_model_func(prompt, system_prompt, history_messages, **kwargs)

        # Embedding 配置
        embedding_dim = int(os.getenv("EMBEDDING_DIM", "1024"))
        embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
        embedding_api_key = os.getenv("EMBEDDING_BINDING_API_KEY")
        embedding_base_url = os.getenv("EMBEDDING_BINDING_HOST")

        embedding_func = EmbeddingFunc(
            embedding_dim=embedding_dim,
            max_token_size=8192,
            func=lambda texts: openai_embed(
                texts,
                model=embedding_model,
                api_key=embedding_api_key,
                base_url=embedding_base_url,
            ),
        )

        # 创建 RAG 实例
        rag = RAGAnything(
            config=config,
            llm_model_func=llm_model_func,
            vision_model_func=vision_model_func,
            embedding_func=embedding_func,
        )

        # 初始化 LightRAG（关键步骤！）
        init_result = await rag._ensure_lightrag_initialized()
        if not init_result.get("success", False):
            raise ValueError(f"Failed to initialize LightRAG: {init_result.get('error', 'Unknown error')}")

        self.rag_instances[kb_name] = rag
        return rag

    async def test_sample(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """测试单个样本"""
        if "score" in sample and not self.force_rerun:
            return sample

        question = sample["question"]
        doc_id = sample["doc_id"]

        print(f"\n处理问题: {question[:80]}...")
        print(f"文档: {doc_id}")

        try:
            kb_name = self._get_kb_name_from_doc_id(doc_id)
            print(f"使用知识库: {kb_name}")

            # 检查知识库是否存在
            if not self._check_kb_exists(kb_name):
                error_msg = f"知识库不存在: {kb_name}"
                print(f"⚠️  {error_msg}")
                sample["response"] = "Knowledge base not found"
                sample["pred"] = "Knowledge base not found"
                sample["score"] = 0.0
                sample["error"] = error_msg
                sample["kb_name"] = kb_name
                return sample

            # 获取 RAG 实例
            if self._first_query:
                print(f"⏳ 首次查询需要初始化知识库，请稍候...")
                self._first_query = False
            
            print(f"🔍 开始 RAG 查询 (hybrid mode)...")
            sys.stdout.flush()
            
            try:
                rag = await asyncio.wait_for(
                    self._get_rag_instance(kb_name),
                    timeout=60.0
                )
                
                # 执行查询
                answer = await asyncio.wait_for(
                    rag.aquery(question, mode="hybrid"),
                    timeout=120.0
                )
                
                print(f"✅ RAG 查询完成")
                
            except asyncio.TimeoutError:
                error_msg = "RAG query timeout"
                print(f"⏱️  {error_msg}")
                sample["response"] = "Timeout"
                sample["pred"] = "Timeout"
                sample["score"] = 0.0
                sample["error"] = error_msg
                sample["kb_name"] = kb_name
                return sample

            # 评估答案
            try:
                eval_result = await self.llm_evaluator.evaluate_single_answer(
                    question=question,
                    expected_answer=str(sample["answer"]),
                    generated_answer=answer,
                    evidence_pages=str(sample.get("evidence_pages", "")),
                    evidence_sources=str(sample.get("evidence_sources", "")),
                    doc_id=sample["doc_id"],
                    evaluation_type="accuracy_only"
                )
                
                # 从评估结果中提取分数
                # eval_result 可能包含 "accuracy" 或 "overall_score" 等字段
                if "scores" in eval_result and "overall_accuracy" in eval_result["scores"]:
                    score = eval_result["scores"]["overall_accuracy"]
                elif "accuracy" in eval_result:
                    score = eval_result["accuracy"] if eval_result["accuracy"] is not None else 0.0
                elif "overall_score" in eval_result:
                    score = eval_result["overall_score"] if eval_result["overall_score"] is not None else 0.0
                else:
                    # 默认值
                    score = 0.0
                
                # 归一化分数到 0-1 范围
                if isinstance(score, (int, float)) and score > 1:
                    score = score / 100.0
                    
                sample["response"] = answer
                sample["pred"] = answer
                sample["score"] = score
                sample["eval_reasoning"] = eval_result.get("reasoning", "")
                sample["kb_name"] = kb_name
                
                # 显示结果
                score_icon = "✅" if score >= 0.5 else "❌"
                print(f"\n{'='*80}")
                print(f"📝 问题: {question}")
                print(f"\n💬 RAG完整输出:")
                print(answer)
                print(f"\n✓  正确答案: {sample['answer']}")
                print(f"{score_icon} 得分: {score}")
                
                # 显示完整的评估推理
                eval_reasoning = eval_result.get("reasoning", "")
                if eval_reasoning:
                    print(f"\n📋 评估推理:")
                    print(eval_reasoning)
                print('='*80)

            except Exception as e:
                print(f"⚠️  评估失败: {e}")
                sample["response"] = answer
                sample["pred"] = answer
                sample["score"] = 0.0
                sample["error"] = f"Evaluation error: {str(e)}"
                sample["kb_name"] = kb_name

        except Exception as e:
            sample["response"] = f"Error: {str(e)}"
            sample["score"] = 0.0
            sample["error"] = str(e)
            print(f"\n❌ 处理失败: {e}")

        return sample

    async def run_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 80)
        print("开始 RAG Native 测试 (使用 RAGAnything 原生 API)")
        print("=" * 80)

        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"📝 总共 {len(self.samples)} 个样本待测试")
        print(f"💾 结果将保存到: {self.results_file}")
        print(f"📂 知识库目录: {self.kb_base_dir}")
        print("\n开始处理样本...\n")

        for i, sample in enumerate(tqdm(self.samples, desc="测试进度", ncols=80, mininterval=0.1)):
            print(f"\n{'='*60}")
            print(f"[{i+1}/{len(self.samples)}] 开始处理样本...")
            sys.stdout.flush()
            
            if "score" in sample and not self.force_rerun:
                completed_samples = [s for s in self.samples if "score" in s]
                if completed_samples and (i % 5 == 0 or i == len(self.samples) - 1):
                    total_score = sum(s.get("score", 0) for s in completed_samples)
                    current_acc = total_score / len(completed_samples)
                    print(f"📊 累计准确率: {current_acc:.2%} ({int(total_score)}/{len(completed_samples)})")
                continue

            try:
                sample = await self.test_sample(sample)
                self._save_results()
                
                # 统计已完成的样本（包括本轮新完成的）
                completed_samples = [s for s in self.samples[:i+1] if "score" in s]
                if completed_samples:
                    total_score = sum(s.get("score", 0) for s in completed_samples)
                    current_acc = total_score / len(completed_samples)
                    print(f"📊 累计准确率: {current_acc:.2%} ({total_score:.1f}/{len(completed_samples)})")

            except KeyboardInterrupt:
                print("\n用户中断测试，保存当前结果...")
                self._save_results()
                break
            except Exception as e:
                print(f"❌ 处理样本时出错: {e}")
                sample["error"] = str(e)
                sample["score"] = 0.0
                self._save_results()
                continue

        print("\n" + "=" * 80)
        print("生成评估报告")
        print("=" * 80)
        self._generate_report()

    def _generate_report(self):
        """生成评估报告"""
        completed_samples = [s for s in self.samples if "score" in s]
        if not completed_samples:
            print("没有完成的样本，跳过报告生成")
            return

        total_score = sum(s.get("score", 0) for s in completed_samples)
        total_count = len(completed_samples)
        accuracy = total_score / total_count if total_count > 0 else 0

        correct = sum(1 for s in completed_samples if s.get("score", 0) >= 0.5)
        incorrect = total_count - correct

        # 按知识库统计
        kb_stats = {}
        for s in completed_samples:
            kb = s.get("kb_name", "unknown")
            if kb not in kb_stats:
                kb_stats[kb] = {"total": 0, "score": 0}
            kb_stats[kb]["total"] += 1
            kb_stats[kb]["score"] += s.get("score", 0)

        report_lines = [
            "\n" + "=" * 80,
            f"RAG Native 测试报告 (使用 RAGAnything 原生 API)",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            f"Overall Accuracy: {accuracy:.4f} | Question Number: {total_count}",
            f"Correct: {correct} | Incorrect: {incorrect}",
            "",
            "按知识库统计:",
        ]

        for kb, stats in sorted(kb_stats.items()):
            kb_acc = stats["score"] / stats["total"] if stats["total"] > 0 else 0
            report_lines.append(f"  {kb}: Accuracy: {kb_acc:.4f} | Questions: {stats['total']}")

        report_text = "\n".join(report_lines)
        print(report_text)

        # 保存报告
        report_file = self.results_file.parent / "report_rag_native.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_text)
        
        print(f"\n报告已保存到: {report_file}")


async def main():
    parser = argparse.ArgumentParser(description="RAG Native 测试 - 使用 RAGAnything 原生 API")
    parser.add_argument(
        "--samples",
        type=str,
        default=str(mmlongbench_root / "data" / "samples.json"),
        help="样本文件路径",
    )
    parser.add_argument(
        "--results",
        type=str,
        default="test_results/results_rag_native.json",
        help="结果文件路径",
    )
    parser.add_argument(
        "--kb_dir",
        type=str,
        default="../../data/knowledge_bases",
        help="知识库基础目录",
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=None,
        help="最大测试样本数",
    )
    parser.add_argument(
        "--start_index",
        type=int,
        default=0,
        help="起始索引",
    )
    parser.add_argument(
        "--force_rerun",
        action="store_true",
        help="强制重新运行所有测试",
    )

    args = parser.parse_args()

    # 转换为绝对路径
    kb_dir = Path(args.kb_dir)
    if not kb_dir.is_absolute():
        kb_dir = Path(__file__).parent / kb_dir
    kb_dir = kb_dir.resolve()

    tester = RAGNativeTester(
        samples_path=args.samples,
        results_file=args.results,
        kb_base_dir=str(kb_dir),
        max_samples=args.max_samples,
        start_index=args.start_index,
        force_rerun=args.force_rerun,
    )

    await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())

