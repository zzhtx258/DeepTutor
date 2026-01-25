#!/usr/bin/env python
"""
测试脚本：使用 DeepTutor solve 模块测试 MMLongBench-Doc 基准

该脚本会：
1. 读取 MMLongBench-Doc 的 samples.json（仅用于提供问题和正确答案数据）
2. 对于每个问题，使用 MainSolver 来解决
3. 使用 LLM-as-a-Judge (GPT-4o-mini) 评估答案准确性
4. 生成评估报告

评估方式：
- 使用 LLMAnswerEvaluator 进行 LLM-as-a-Judge 评估
- 不再依赖 MMLongBench-Doc 的规则评估（ANLS/编辑距离）
- LLM 评估更准确地判断答案语义正确性

注意：
- 所有操作必须在 deeptutor conda 环境中进行
- 运行前请确保：conda activate deeptutor
- Web search 功能在测试时自动禁用（通过设置 config.tools.web_search.enabled = False）
"""

import argparse
import asyncio
import atexit
import json
import os
import re
import shutil
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
# 关闭常见模块的 INFO 日志
for logger_name in ["httpx", "httpcore", "openai", "urllib3", "asyncio", "lightrag", "Solver", "InvestigateAgent", "NoteAgent", "ManagerAgent", "SolveAgent", "ToolAgent", "ResponseAgent", "PrecisionAnswerAgent"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# 存储需要在退出时清理的 RAGAnything 实例
_raganything_instances = []

def _cleanup_raganything():
    """在程序退出前清理 RAGAnything 实例，避免警告"""
    for instance in _raganything_instances:
        try:
            # 尝试同步清理
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(instance.finalize_storages())
            loop.close()
        except Exception:
            pass  # 静默忽略清理错误

atexit.register(_cleanup_raganything)

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# MMLongBench-Doc 数据路径（只用于读取样本数据）
mmlongbench_root = project_root.parent / "MMLongBench-Doc"

from dotenv import load_dotenv
from tqdm import tqdm

# 加载环境变量
load_dotenv(project_root / ".env", override=False)

# 导入 DeepTutor solve 模块
from src.agents.solve.main_solver import MainSolver
from src.knowledge.initializer import KnowledgeBaseInitializer
from src.knowledge.add_documents import DocumentAdder

# 导入 LLM 评估模块
from llm_answer_evaluator import LLMAnswerEvaluator


class LLMEvaluatorConfig:
    """LLM评估器配置"""
    def __init__(self, output_dir: str, api_key: str, base_url: str, model: str = "gpt-4o", quiet: bool = False):
        self.output_dir = output_dir
        self.api_key = api_key
        self.base_url = base_url
        self.model = model  # 评估模型名称
        self.quiet = quiet  # 静默模式，不输出到控制台


class MMLongBenchTester:
    """MMLongBench-Doc 测试器"""

    def __init__(
        self,
        samples_path: str,
        document_path: str,
        output_dir: str,
        kb_name: str = None,  # 已弃用，现在每个文档使用独立知识库
        max_samples: int = None,
        start_index: int = 0,
        force_rerun: bool = False,
    ):
        """
        初始化测试器（使用 LLM-as-a-Judge 评估）

        Args:
            samples_path: samples.json 文件路径
            document_path: PDF 文档目录路径
            output_dir: 输出目录
            kb_name: 知识库名称（已弃用，现在每个文档使用独立知识库）
            max_samples: 最大测试样本数（None 表示全部）
            start_index: 起始索引（用于断点续传）
        """
        self.samples_path = Path(samples_path)
        self.document_path = Path(document_path)
        self.output_dir = Path(output_dir)
        if kb_name:
            print(f"警告: --kb_name 参数已弃用，现在每个文档使用独立知识库")
        self.max_samples = max_samples
        self.start_index = start_index
        self.force_rerun = force_rerun

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_file = self.output_dir / "results.json"
        self.report_file = self.output_dir / "report.txt"
        
        # 如果强制重新运行，删除旧的结果文件
        if self.force_rerun and self.results_file.exists():
            print(f"强制重新运行：删除旧的结果文件 {self.results_file}")
            self.results_file.unlink()

        # 获取 LLM 配置
        import os
        from dotenv import load_dotenv
        project_root = Path(__file__).parent.parent.parent
        load_dotenv(project_root / ".env", override=False)
        
        self.api_key = os.getenv("LLM_BINDING_API_KEY")
        self.base_url = os.getenv("LLM_BINDING_HOST")
        self.model_name = os.getenv("LLM_MODEL", "gpt-4o")
        
        if not self.api_key or not self.base_url:
            raise ValueError(
                "LLM_BINDING_API_KEY 和 LLM_BINDING_HOST 必须设置才能进行 LLM 评估"
            )
        
        # 创建 LLM 评估器
        evaluator_config = LLMEvaluatorConfig(
            output_dir=str(self.output_dir),
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model_name,  # 使用与 solver 相同的模型
            quiet=True  # 静默模式
        )
        self.llm_evaluator = LLMAnswerEvaluator(evaluator_config)

        # 加载样本
        self.samples = self._load_samples()

        # 知识库缓存（每个文档对应一个知识库）
        self.kb_cache = {}  # doc_id -> kb_name
        self.solver_cache = {}  # kb_name -> solver

        # 知识库基础目录
        self.kb_base_dir = Path("./data/knowledge_bases")

    def _load_samples(self) -> List[Dict[str, Any]]:
        """加载测试样本"""
        # 始终从原始 samples.json 加载
        with open(self.samples_path, "r", encoding="utf-8") as f:
            samples = json.load(f)

        # 限制样本数量
        if self.max_samples:
            samples = samples[: self.max_samples]

        # 从指定索引开始
        if self.start_index > 0:
            samples = samples[self.start_index:]

        # 如果结果文件存在，合并已完成的结果（支持断点续传）
        if self.results_file.exists() and not self.force_rerun:
            print(f"从现有结果文件加载已完成的结果: {self.results_file}")
            with open(self.results_file, "r", encoding="utf-8") as f:
                existing_results = json.load(f)
            
            # 创建已完成结果的查找字典（基于 question + doc_id）
            results_dict = {}
            for r in existing_results:
                key = (r.get("question", ""), r.get("doc_id", ""))
                if key:
                    results_dict[key] = r
            
            # 合并已完成的结果到样本中
            merged_count = 0
            for sample in samples:
                key = (sample.get("question", ""), sample.get("doc_id", ""))
                if key in results_dict:
                    # 用已完成的结果更新样本
                    existing = results_dict[key]
                    sample.update(existing)
                    merged_count += 1
            
            if merged_count > 0:
                print(f"  合并了 {merged_count} 个已完成的结果")

        print(f"加载了 {len(samples)} 个测试样本")
        return samples

    def _get_kb_name_from_doc_id(self, doc_id: str) -> str:
        """
        从文档ID生成知识库名称
        
        Args:
            doc_id: 文档ID（如 "PH_2016.06.08_Economy-Final.pdf"）
        
        Returns:
            知识库名称（如 "mmlongbench_PH_2016_06_08_Economy_Final"）
        """
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

    async def _ensure_kb_for_document(self, doc_id: str) -> str:
        """
        确保文档对应的知识库存在，如果不存在则创建并添加文档
        
        Args:
            doc_id: 文档ID
        
        Returns:
            知识库名称
        """
        # 检查缓存
        if doc_id in self.kb_cache:
            return self.kb_cache[doc_id]

        # 生成知识库名称
        kb_name = self._get_kb_name_from_doc_id(doc_id)
        self.kb_cache[doc_id] = kb_name

        # 检查知识库是否存在
        kb_dir = self.kb_base_dir / kb_name
        doc_file = self.document_path / doc_id

        if not doc_file.exists():
            raise FileNotFoundError(f"文档不存在: {doc_file}")

        if not kb_dir.exists():
            print(f"\n为文档 {doc_id} 创建知识库: {kb_name}")
            # 创建知识库
            initializer = KnowledgeBaseInitializer(
                kb_name=kb_name,
                base_dir=str(self.kb_base_dir),
            )
            initializer.create_directory_structure()

            # 添加文档
            adder = DocumentAdder(
                kb_name=kb_name,
                base_dir=str(self.kb_base_dir),
            )
            added_files = adder.add_documents(
                source_files=[str(doc_file)],
                skip_duplicates=True,
            )
            print(f"  已添加文档到知识库: {len(added_files)} 个文件")
            
            # 处理文档（异步）
            if added_files:
                print(f"  正在处理文档（这可能需要一些时间）...")
                await adder.process_new_documents(added_files)
                print(f"  文档处理完成")
        else:
            # 检查知识库是否已处理（检查是否有 rag_storage 内容）
            rag_storage_dir = kb_dir / "rag_storage"
            if not rag_storage_dir.exists() or not any(rag_storage_dir.iterdir()):
                print(f"  知识库存在但未处理，正在处理文档...")
                adder = DocumentAdder(
                    kb_name=kb_name,
                    base_dir=str(self.kb_base_dir),
                )
                # 检查 raw 目录中的文件
                raw_dir = kb_dir / "raw"
                if raw_dir.exists():
                    raw_files = list(raw_dir.glob("*.pdf"))
                    if raw_files:
                        await adder.process_new_documents(raw_files)
                        print(f"  文档处理完成")
            else:
                print(f"  使用现有知识库: {kb_name}")

        return kb_name

    def _get_solver_for_kb(self, kb_name: str) -> MainSolver:
        """
        获取指定知识库的 solver（带缓存）
        
        Args:
            kb_name: 知识库名称
        
        Returns:
            MainSolver 实例
        """
        if kb_name not in self.solver_cache:
            # 设置输出目录
            solver_output_dir = self.output_dir / "solve_outputs" / kb_name
            solver_output_dir.mkdir(parents=True, exist_ok=True)

            solver = MainSolver(
                kb_name=kb_name,
                output_base_dir=str(solver_output_dir),
            )
            
            # 按照官方方法禁用 web search：修改 config.tools.web_search.enabled
            # 参考：config/README.md 和 config/main.yaml
            # InvestigateAgent 会读取 config.get("tools", {}).get("web_search", {}).get("enabled", True)
            if "tools" not in solver.config:
                solver.config["tools"] = {}
            if "web_search" not in solver.config["tools"]:
                solver.config["tools"]["web_search"] = {}
            solver.config["tools"]["web_search"]["enabled"] = False
            
            # 更新已初始化的 InvestigateAgent（agents 在 MainSolver.__init__ 时已初始化）
            # InvestigateAgent 在 __init__ 时读取了 self.enable_web_search
            # 需要更新它以反映新的配置
            if hasattr(solver, "investigate_agent"):
                solver.investigate_agent.enable_web_search = False
            
            self.solver_cache[kb_name] = solver

        return self.solver_cache[kb_name]

    def _extract_concise_answer(self, response: str) -> str:
        """
        从响应中提取 Concise Answer
        
        查找 "## Concise Answer" 或类似标记后的内容
        
        Returns:
            提取的简洁答案，如果未找到则返回空字符串
        """
        import re
        
        # 尝试多种模式提取 Concise Answer
        patterns = [
            # ## Concise Answer\n\nXXX\n\n---
            r"## Concise Answer\s*\n\n(.+?)\n\n---",
            # ## Concise Answer\n\nXXX (到文件末尾)
            r"## Concise Answer\s*\n\n(.+?)(?:\n\n|$)",
            # **Concise Answer:** XXX
            r"\*\*Concise Answer[:\*]*\s*(.+?)(?:\n|$)",
            # Concise Answer: XXX
            r"Concise Answer[:\s]+(.+?)(?:\n|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                # 清理答案：移除多余的空白和换行
                answer = re.sub(r'\s+', ' ', answer).strip()
                if answer:
                    return answer
        
        return ""

    async def test_sample(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试单个样本

        Args:
            sample: 测试样本

        Returns:
            更新后的样本（包含 response, pred, score 等字段）
        """
        # 如果已经有结果，跳过
        if "score" in sample and sample.get("skip", False) is False:
            return sample

        question = sample["question"]
        doc_id = sample["doc_id"]

        print(f"\n处理问题: {question}...")
        print(f"文档: {doc_id}")

        try:
            # 确保文档对应的知识库存在
            kb_name = await self._ensure_kb_for_document(doc_id)
            print(f"使用知识库: {kb_name}")

            # 获取对应的 solver
            solver = self._get_solver_for_kb(kb_name)

            # 使用 solver 解决问题
            result = await solver.solve(question=question, verbose=False)

            # 获取最终答案
            final_answer = result.get("final_answer", "")
            if not final_answer:
                # 如果没有 final_answer，尝试从其他字段获取
                final_answer = result.get("formatted_solution", "")

            # 提取 Concise Answer（如果存在）
            concise_answer = self._extract_concise_answer(final_answer)
            # 用于评估的答案：优先使用 concise_answer
            eval_answer = concise_answer if concise_answer else final_answer

            # 使用 LLM-as-a-Judge 评估答案
            try:
                eval_result = await self.llm_evaluator.evaluate_single_answer(
                    question=question,
                    expected_answer=str(sample["answer"]),
                    generated_answer=eval_answer,
                    evidence_pages=str(sample.get("evidence_pages", "")),
                    evidence_sources=str(sample.get("evidence_sources", "")),
                    doc_id=sample["doc_id"],
                    evaluation_type="accuracy_only"  # 只评估准确性，速度更快
                )
                
                # 提取评估结果
                score = float(eval_result.get("accuracy", 0))
                reasoning = eval_result.get("reasoning", "")
                
            except Exception as e:
                print(f"LLM评估失败: {e}")
                score = 0.0
                reasoning = f"Evaluation error: {str(e)}"

            # 更新样本
            sample["response"] = final_answer
            sample["concise_answer"] = concise_answer  # 记录提取的简洁答案
            sample["eval_answer"] = eval_answer  # 用于评估的答案
            sample["score"] = score
            sample["llm_reasoning"] = reasoning
            output_dir = result.get("output_dir", "")
            sample["output_dir"] = output_dir
            sample["kb_name"] = kb_name  # 记录使用的知识库

            # 简洁输出：原题、答案、得分、日志位置
            score_icon = "✅" if score >= 0.5 else "❌"
            # 截断过长的内容
            q_short = question 
            ans_short = eval_answer[:100] + "..." if len(eval_answer) > 100 else eval_answer
            print(f"\n📝 问题: {q_short}")
            print(f"💬 输出: {ans_short}")
            print(f"✓  正确: {sample['answer']}")
            print(f"{score_icon} 得分: {score} | 日志: {output_dir}")

        except Exception as e:
            sample["response"] = f"Error: {str(e)}"
            sample["pred"] = "Failed"
            sample["score"] = 0.0
            sample["error"] = str(e)
            print(f"\n❌ 处理失败: {e}")

        return sample

    async def run_tests(self):
        """运行所有测试"""
        # 计算已完成的样本数
        completed = sum(1 for s in self.samples if "score" in s)
        print(f"\n🚀 开始测试 | 总样本: {len(self.samples)} | 已完成: {completed} | 输出: {self.output_dir}")

        # 运行测试
        for i, sample in enumerate(tqdm(self.samples, desc="测试进度")):
            # 跳过已完成的样本（除非强制重新运行）
            if not self.force_rerun and "score" in sample:
                continue
            
            try:
                sample = await self.test_sample(sample)
                self.samples[i] = sample

                # 每处理一个样本就保存一次（支持断点续传）
                with open(self.results_file, "w", encoding="utf-8") as f:
                    json.dump(self.samples, f, ensure_ascii=False, indent=2)

                # 计算并显示当前累计准确率
                completed_samples = [s for s in self.samples if "score" in s]
                if completed_samples:
                    total_score = sum(s.get("score", 0) for s in completed_samples)
                    current_acc = total_score / len(completed_samples)
                    print(f"📊 累计准确率: {current_acc:.2%} ({int(total_score)}/{len(completed_samples)})")

            except KeyboardInterrupt:
                print("\n\n⚠️ 测试被用户中断，已保存进度")
                break
            except Exception as e:
                print(f"\n❌ 样本 {i} 出错: {e}")
                continue

        # 生成最终报告
        self._generate_report()

    def _generate_report(self):
        """生成评估报告（使用 LLM-as-a-Judge 结果）"""
        print("\n生成评估报告...")

        # 统计结果
        evaluated_samples = [s for s in self.samples if "score" in s]
        if not evaluated_samples:
            print("没有已评估的样本")
            return
        
        total_samples = len(evaluated_samples)
        correct_samples = sum(1 for s in evaluated_samples if s.get("score", 0) >= 0.5)
        accuracy = correct_samples / total_samples if total_samples > 0 else 0
        
        # 按文档类型统计
        doc_type_stats = {}
        for sample in evaluated_samples:
            doc_type = sample.get("doc_type", "Unknown")
            if doc_type not in doc_type_stats:
                doc_type_stats[doc_type] = {"total": 0, "correct": 0}
            doc_type_stats[doc_type]["total"] += 1
            if sample.get("score", 0) >= 0.5:
                doc_type_stats[doc_type]["correct"] += 1
        
        # 按证据来源统计
        source_stats = {}
        for sample in evaluated_samples:
            sources = sample.get("evidence_sources", "[]")
            if isinstance(sources, str):
                try:
                    sources = eval(sources)
                except:
                    sources = [sources]
            if not isinstance(sources, list):
                sources = [sources]
            
            for source in sources:
                if source not in source_stats:
                    source_stats[source] = {"total": 0, "correct": 0}
                source_stats[source]["total"] += 1
                if sample.get("score", 0) >= 0.5:
                    source_stats[source]["correct"] += 1
        
        # 生成报告内容
        report_lines = [
            f"Overall Accuracy (LLM-as-Judge): {accuracy:.4f} | Question Number: {total_samples}",
            f"Correct Answers: {correct_samples} | Total Evaluated: {total_samples}",
            "-" * 50,
        ]
        
        # 文档类型统计
        report_lines.append("\n按文档类型统计:")
        for doc_type, stats in doc_type_stats.items():
            type_acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            report_lines.append(
                f"  {doc_type}: Accuracy: {type_acc:.4f} | Questions: {stats['total']}"
            )
        
        # 证据来源统计
        report_lines.append("\n按证据来源统计:")
        for source, stats in source_stats.items():
            source_acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            report_lines.append(
                f"  {source}: Accuracy: {source_acc:.4f} | Questions: {stats['total']}"
            )
        
        report_content = "\n".join(report_lines)
        
        # 保存报告
        with open(self.report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        # 打印报告内容
        print("\n" + "=" * 60)
        print("评估报告 (LLM-as-a-Judge)")
        print("=" * 60)
        print(report_content)

        print(f"\n结果已保存到: {self.results_file}")
        print(f"报告已保存到: {self.report_file}")


def main():
    parser = argparse.ArgumentParser(
        description="使用 DeepTutor solve 模块测试 MMLongBench-Doc（必须在 deeptutor conda 环境中运行）"
    )
    parser.add_argument(
        "--samples_path",
        type=str,
        default="../MMLongBench-Doc/data/samples.json",
        help="samples.json 文件路径",
    )
    parser.add_argument(
        "--document_path",
        type=str,
        default="../MMLongBench-Doc/data/documents",
        help="PDF 文档目录路径",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./test_results",
        help="输出目录",
    )
    parser.add_argument(
        "--kb_name",
        type=str,
        default=None,
        help="知识库名称（已弃用：现在每个文档使用独立知识库）",
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=None,
        help="最大测试样本数（用于快速测试）",
    )
    parser.add_argument(
        "--start_index",
        type=int,
        default=0,
        help="起始索引（用于断点续传）",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制重新运行，删除旧的结果文件",
    )

    args = parser.parse_args()
    
    # 检查是否在正确的 conda 环境中
    python_path = sys.executable
    if "deeptutor" not in python_path.lower():
        print("⚠️  警告: 当前可能不在 deeptutor conda 环境中")
        print(f"当前 Python 路径: {python_path}")
        print("建议运行: conda activate deeptutor")
        response = input("是否继续？(y/n): ")
        if response.lower() != 'y':
            print("已取消")
            sys.exit(1)
    
    # 检查必需的环境变量
    import os
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent.parent
    load_dotenv(project_root / ".env", override=False)
    
    required_vars = {
        "LLM_MODEL": os.getenv("LLM_MODEL"),
        "LLM_BINDING_API_KEY": os.getenv("LLM_BINDING_API_KEY"),
        "LLM_BINDING_HOST": os.getenv("LLM_BINDING_HOST"),
        "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL"),
        "EMBEDDING_BINDING_API_KEY": os.getenv("EMBEDDING_BINDING_API_KEY"),
        "EMBEDDING_BINDING_HOST": os.getenv("EMBEDDING_BINDING_HOST"),
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        print("❌ 错误: 缺少必需的环境变量配置")
        print("请在项目根目录的 .env 文件中配置以下变量：")
        for var in missing_vars:
            print(f"  - {var}")
        print("\n示例配置：")
        print("  LLM_MODEL=gpt-4o")
        print("  LLM_BINDING_API_KEY=your_api_key")
        print("  LLM_BINDING_HOST=https://api.openai.com/v1")
        print("  EMBEDDING_MODEL=text-embedding-3-large")
        print("  EMBEDDING_BINDING_API_KEY=your_api_key")
        print("  EMBEDDING_BINDING_HOST=https://api.openai.com/v1")
        sys.exit(1)
    
    # 验证 LLM-as-a-Judge 评估所需的配置
    llm_api_key = os.getenv("LLM_BINDING_API_KEY")
    llm_base_url = os.getenv("LLM_BINDING_HOST")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o")
    if llm_api_key and llm_base_url:
        print(f"ℹ️  LLM-as-a-Judge 评估将使用: {llm_base_url} (模型: {llm_model})")
    else:
        print("⚠️  警告: LLM_BINDING_API_KEY 或 LLM_BINDING_HOST 未设置，LLM评估可能失败")

    # 创建测试器
    tester = MMLongBenchTester(
        samples_path=args.samples_path,
        document_path=args.document_path,
        output_dir=args.output_dir,
        kb_name=args.kb_name,  # 已弃用，保留以兼容旧代码
        max_samples=args.max_samples,
        start_index=args.start_index,
        force_rerun=args.force,
    )

    # 运行测试
    asyncio.run(tester.run_tests())


if __name__ == "__main__":
    main()

