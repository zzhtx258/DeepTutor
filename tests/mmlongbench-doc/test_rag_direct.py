#!/usr/bin/env python
"""
测试脚本：直接使用 RAGAnything (hybrid mode) 回答 MMLongBench-Doc 问题

功能：
1. 读取 MMLongBench-Doc 的 samples.json
2. 对于每个问题，直接使用 RAG hybrid 搜索获取答案
3. 使用 LLM-as-a-Judge 评估答案准确性
4. 生成评估报告

与 test_solve_mmlongbench.py 的区别：
- 不使用完整的 solver pipeline
- 直接调用 RAG hybrid 搜索
- 更快速，用于测试 RAG 的基础检索能力
"""

import argparse
import asyncio
import json
import os
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

# 抑制常见的异步相关警告
warnings.filterwarnings("ignore", message=".*no current event loop.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="asyncio")

# 设置日志级别为 WARNING，关闭 INFO 日志
import logging
logging.getLogger().setLevel(logging.WARNING)
for logger_name in ["httpx", "httpcore", "openai", "urllib3", "asyncio", "lightrag", "raganything"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# 特别抑制 LightRAG 的详细日志
logging.getLogger("lightrag").setLevel(logging.ERROR)
logging.getLogger("raganything").setLevel(logging.ERROR)

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# MMLongBench-Doc 数据路径
mmlongbench_root = project_root.parent / "MMLongBench-Doc"

from dotenv import load_dotenv
from tqdm import tqdm

# 加载环境变量
load_dotenv(project_root / ".env", override=False)

# 导入 RAG 工具
from src.tools.rag_tool import rag_search

# 导入 LLM 评估模块
from llm_answer_evaluator import LLMAnswerEvaluator


class LLMEvaluatorConfig:
    """LLM评估器配置"""
    def __init__(self, output_dir: str, api_key: str, base_url: str, model: str = "gpt-4o", quiet: bool = False):
        self.output_dir = output_dir
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.quiet = quiet


class RAGDirectTester:
    """RAG 直接测试器"""

    def __init__(
        self,
        samples_path: str,
        results_file: str,
        kb_base_dir: str,
        max_samples: int = None,
        start_index: int = 0,
        force_rerun: bool = False,
        skip_missing_kb: bool = True,
    ):
        """
        初始化测试器

        Args:
            samples_path: 样本文件路径
            results_file: 结果文件路径
            kb_base_dir: 知识库基础目录
            max_samples: 最大测试样本数
            start_index: 起始索引
            force_rerun: 是否强制重新运行
            skip_missing_kb: 是否跳过没有知识库的样本
        """
        self.samples_path = Path(samples_path)
        self.results_file = Path(results_file)
        self.kb_base_dir = Path(kb_base_dir)
        self.max_samples = max_samples
        self.start_index = start_index
        self.force_rerun = force_rerun
        self.skip_missing_kb = skip_missing_kb
        
        # 用于跟踪是否已经提示过初始化
        self._first_query = True

        # 加载样本
        self.samples = self._load_samples()

        # 初始化 LLM 评估器
        llm_api_key = os.getenv("LLM_API_KEY")
        llm_base_url = os.getenv("LLM_BASE_URL")
        llm_model = os.getenv("LLM_MODEL", "gpt-4o")
        
        evaluator_config = LLMEvaluatorConfig(
            output_dir=str(self.results_file.parent / "evaluations"),
            api_key=llm_api_key,
            base_url=llm_base_url,
            model=llm_model,
            quiet=True
        )
        self.llm_evaluator = LLMAnswerEvaluator(evaluator_config)

        # 文档ID到知识库名称的映射
        self.kb_cache = {}

    def _load_samples(self) -> List[Dict[str, Any]]:
        """加载测试样本"""
        # 加载所有样本
        with open(self.samples_path, "r", encoding="utf-8") as f:
            all_samples = json.load(f)

        # 如果指定了 max_samples，则截断
        if self.max_samples:
            all_samples = all_samples[: self.max_samples]

        # 加载已完成的结果（如果存在）
        if self.results_file.exists() and not self.force_rerun:
            print(f"从现有结果文件加载: {self.results_file}")
            with open(self.results_file, "r", encoding="utf-8") as f:
                existing_results = json.load(f)
            
            # 创建结果字典
            results_dict = {}
            for result in existing_results:
                key = (result.get("question", ""), result.get("doc_id", ""))
                results_dict[key] = result
            
            # 合并已完成的结果到样本中
            merged_count = 0
            for sample in all_samples:
                key = (sample.get("question", ""), sample.get("doc_id", ""))
                if key in results_dict:
                    existing = results_dict[key]
                    sample.update(existing)
                    merged_count += 1
            
            if merged_count > 0:
                print(f"  合并了 {merged_count} 个已完成的结果")

        # 从指定索引开始
        if self.start_index > 0:
            all_samples = all_samples[self.start_index:]

        # 如果设置了 skip_missing_kb，过滤掉没有知识库的样本
        if self.skip_missing_kb:
            filtered_samples = []
            for sample in all_samples:
                kb_name = self._get_kb_name_from_doc_id(sample.get("doc_id", ""))
                if self._check_kb_exists(kb_name):
                    filtered_samples.append(sample)
            
            skipped_count = len(all_samples) - len(filtered_samples)
            if skipped_count > 0:
                print(f"⚠️  跳过 {skipped_count} 个没有知识库的样本")
            all_samples = filtered_samples

        print(f"加载了 {len(all_samples)} 个测试样本")
        return all_samples

    def _get_kb_name_from_doc_id(self, doc_id: str) -> str:
        """从文档ID生成知识库名称"""
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
        kb_dir = self.kb_base_dir / kb_name
        # DeepTutor 知识库的标志：存在 rag_storage 目录和 metadata.json 文件
        return kb_dir.exists() and (kb_dir / "rag_storage").exists() and (kb_dir / "metadata.json").exists()

    def _extract_answer_from_rag(self, rag_result: Dict[str, Any]) -> str:
        """从 RAG 结果中提取答案"""
        # RAG 返回的结果结构：{"answer": "...", "sources": [...]}
        answer = rag_result.get("answer", "")
        if not answer:
            return "Not answerable"
        return answer.strip()

    async def test_sample(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试单个样本

        Args:
            sample: 测试样本

        Returns:
            更新后的样本
        """
        # 如果已经有结果且不是强制重新运行，跳过
        if "score" in sample and not self.force_rerun:
            return sample

        question = sample["question"]
        doc_id = sample["doc_id"]

        print(f"\n处理问题: {question[:80]}...")
        print(f"文档: {doc_id}")

        try:
            # 获取知识库名称
            kb_name = self._get_kb_name_from_doc_id(doc_id)
            self.kb_cache[doc_id] = kb_name

            # 检查知识库是否存在
            if not self._check_kb_exists(kb_name):
                # 如果 skip_missing_kb 为 True，这种情况不应该发生（已在加载时过滤）
                # 但为了安全，仍然处理这种情况
                print(f"⚠️  知识库不存在: {kb_name}")
                sample["response"] = "Knowledge base not found"
                sample["score"] = 0.0
                sample["error"] = f"Knowledge base {kb_name} does not exist"
                sample["kb_name"] = kb_name
                return sample

            print(f"使用知识库: {kb_name}")

            # 直接调用 RAG hybrid 搜索
            if self._first_query:
                print(f"⏳ 首次查询需要初始化知识库，请稍候...")
                self._first_query = False
            print(f"🔍 开始 RAG 查询 (hybrid mode)... (问题: {question[:50]}...)")
            sys.stdout.flush()
            try:
                rag_result = await asyncio.wait_for(
                    rag_search(
                        query=question,
                        kb_name=kb_name,
                        mode="hybrid",
                        kb_base_dir=str(self.kb_base_dir)  # 传递知识库基础目录
                    ),
                    timeout=120.0  # 120秒超时
                )
                print(f"✅ RAG 查询完成")
            except asyncio.TimeoutError:
                error_msg = "RAG query timeout (120s)"
                print(f"⏱️  {error_msg}")
                sample["response"] = "Timeout"
                sample["pred"] = "Timeout"
                sample["score"] = 0.0
                sample["error"] = error_msg
                sample["kb_name"] = kb_name
                return sample

            # 提取答案
            generated_answer = self._extract_answer_from_rag(rag_result)

            # 使用 LLM-as-a-Judge 评估答案
            try:
                eval_result = await self.llm_evaluator.evaluate_single_answer(
                    question=question,
                    expected_answer=str(sample["answer"]),
                    generated_answer=generated_answer,
                    evidence_pages=str(sample.get("evidence_pages", "")),
                    evidence_sources=str(sample.get("evidence_sources", "")),
                    doc_id=sample["doc_id"],
                    evaluation_type="accuracy_only"
                )
                
                score = float(eval_result.get("accuracy", 0))
                reasoning = eval_result.get("reasoning", "")
                
            except Exception as e:
                print(f"LLM评估失败: {e}")
                score = 0.0
                reasoning = f"Evaluation error: {str(e)}"

            # 更新样本
            sample["response"] = generated_answer
            sample["score"] = score
            sample["llm_reasoning"] = reasoning
            sample["kb_name"] = kb_name
            sample["rag_sources"] = rag_result.get("sources", [])

            # 简洁输出
            score_icon = "✅" if score >= 0.5 else "❌"
            print(f"\n📝 问题: {question}")
            print(f"💬 RAG输出: {generated_answer}")
            print(f"参考答案: {sample['answer']}")
            print(f"{score_icon} 得分: {score}")

        except Exception as e:
            sample["response"] = f"Error: {str(e)}"
            sample["score"] = 0.0
            sample["error"] = str(e)
            print(f"\n❌ 处理失败: {e}")

        return sample

    async def run_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 80)
        print("开始 RAG Direct 测试")
        print("=" * 80)

        # 确保输出目录存在
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"📝 总共 {len(self.samples)} 个样本待测试")
        print(f"💾 结果将保存到: {self.results_file}")
        print(f"🔄 强制重新运行: {self.force_rerun}")
        print(f"📂 知识库目录: {self.kb_base_dir}")
        print("\n开始处理样本...\n")

        # 运行测试
        for i, sample in enumerate(tqdm(self.samples, desc="测试进度", ncols=80, mininterval=0.1)):
            print(f"\n{'='*60}")
            print(f"[{i+1}/{len(self.samples)}] 开始处理样本...")
            sys.stdout.flush()  # 强制刷新输出缓冲区
            
            # 跳过已完成的样本，除非强制重新运行
            if "score" in sample and not self.force_rerun:
                completed_samples = [s for s in self.samples if "score" in s]
                if completed_samples:
                    total_score = sum(s.get("score", 0) for s in completed_samples)
                    current_acc = total_score / len(completed_samples)
                    if i % 5 == 0 or i == len(self.samples) - 1:
                        print(f"📊 累计准确率: {current_acc:.2%} ({int(total_score)}/{len(completed_samples)})")
                continue

            try:
                sample = await self.test_sample(sample)
                
                # 实时保存结果
                self._save_results()
                
                # 显示累计准确率
                completed_samples = [s for s in self.samples if "score" in s]
                if completed_samples:
                    total_score = sum(s.get("score", 0) for s in completed_samples)
                    current_acc = total_score / len(completed_samples)
                    print(f"📊 累计准确率: {current_acc:.2%} ({int(total_score)}/{len(completed_samples)})")

            except KeyboardInterrupt:
                print("\n用户中断测试，保存当前结果...")
                self._save_results()
                raise
            except Exception as e:
                print(f"测试样本时出错: {e}")
                continue

        # 生成最终报告
        self._generate_report()

    def _save_results(self):
        """保存结果到文件"""
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump(self.samples, f, ensure_ascii=False, indent=2)

    def _generate_report(self):
        """生成评估报告"""
        print("\n" + "=" * 80)
        print("生成评估报告")
        print("=" * 80)

        # 统计结果
        evaluated_samples = [s for s in self.samples if "score" in s]
        total_samples = len(evaluated_samples)
        
        if total_samples == 0:
            print("没有评估结果")
            return

        correct_samples = sum(1 for s in evaluated_samples if s.get("score", 0) >= 0.5)
        accuracy = correct_samples / total_samples if total_samples > 0 else 0

        # 按文档类型统计
        doc_type_stats = {}
        for sample in evaluated_samples:
            doc_id = sample.get("doc_id", "unknown")
            kb_name = sample.get("kb_name", "unknown")
            if kb_name not in doc_type_stats:
                doc_type_stats[kb_name] = {"total": 0, "correct": 0}
            doc_type_stats[kb_name]["total"] += 1
            if sample.get("score", 0) >= 0.5:
                doc_type_stats[kb_name]["correct"] += 1

        # 打印报告
        report_lines = [
            "\n" + "=" * 80,
            f"RAG Direct 测试报告 (Hybrid Mode)",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            f"Overall Accuracy: {accuracy:.4f} | Question Number: {total_samples}",
            f"Correct: {correct_samples} | Incorrect: {total_samples - correct_samples}",
            "\n按知识库统计:",
        ]

        for kb_name, stats in sorted(doc_type_stats.items()):
            kb_acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            report_lines.append(
                f"  {kb_name}: Accuracy: {kb_acc:.4f} | Questions: {stats['total']}"
            )

        report = "\n".join(report_lines)
        print(report)

        # 保存报告到文件
        report_file = self.results_file.parent / "report_rag_direct.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n报告已保存到: {report_file}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="RAG Direct 测试")
    parser.add_argument(
        "--samples",
        type=str,
        default=str(mmlongbench_root / "data" / "samples.json"),
        help="样本文件路径",
    )
    parser.add_argument(
        "--results",
        type=str,
        default="test_results/results_rag_direct.json",
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
    parser.add_argument(
        "--include_missing_kb",
        action="store_true",
        help="包含没有知识库的样本（默认跳过）",
    )

    args = parser.parse_args()

    # 转换为绝对路径
    kb_dir = Path(args.kb_dir)
    if not kb_dir.is_absolute():
        kb_dir = Path(__file__).parent / kb_dir
    kb_dir = kb_dir.resolve()

    # 创建测试器
    tester = RAGDirectTester(
        samples_path=args.samples,
        results_file=args.results,
        kb_base_dir=str(kb_dir),
        max_samples=args.max_samples,
        start_index=args.start_index,
        force_rerun=args.force_rerun,
        skip_missing_kb=not args.include_missing_kb,  # 默认跳过没有知识库的样本
    )

    # 运行测试
    await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())

