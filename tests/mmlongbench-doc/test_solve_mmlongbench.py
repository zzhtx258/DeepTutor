#!/usr/bin/env python
"""
测试脚本：使用 DeepTutor solve 模块测试 MMLongBench-Doc 基准

该脚本会：
1. 读取 MMLongBench-Doc 的 samples.json
2. 对于每个问题，使用 MainSolver 来解决
3. 从答案中提取结果并评估
4. 生成评估报告

注意：
- 所有操作必须在 deeptutor conda 环境中进行
- 运行前请确保：conda activate deeptutor
- Web search 功能在测试时自动禁用（通过设置 config.tools.web_search.enabled = False）
"""

import argparse
import asyncio
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加 MMLongBench-Doc 评估模块到路径
mmlongbench_root = project_root.parent / "MMLongBench-Doc"
if mmlongbench_root.exists():
    sys.path.insert(0, str(mmlongbench_root))

from dotenv import load_dotenv
from tqdm import tqdm

# 加载环境变量
load_dotenv(project_root / ".env", override=False)

# 导入 DeepTutor solve 模块
from src.agents.solve.main_solver import MainSolver
from src.knowledge.initializer import KnowledgeBaseInitializer
from src.knowledge.add_documents import DocumentAdder

# 导入 MMLongBench-Doc 评估模块（延迟导入，避免 OpenAI 客户端初始化问题）
def _import_eval_modules():
    """延迟导入评估模块"""
    try:
        # 先导入 eval_score（不依赖 OpenAI）
        from eval.eval_score import eval_score, eval_acc_and_f1, show_results
        
        # 延迟导入 extract_answer（需要 OpenAI API key）
        def extract_answer_lazy(question, output, prompt, model_name="gpt-4o"):
            """延迟导入 extract_answer"""
            from eval.extract_answer import extract_answer
            return extract_answer(question, output, prompt, model_name)
        
        return {
            "eval_score": eval_score,
            "eval_acc_and_f1": eval_acc_and_f1,
            "show_results": show_results,
            "extract_answer": extract_answer_lazy,
        }
    except ImportError as e:
        print(f"警告: 无法导入 MMLongBench-Doc 评估模块: {e}")
        print(f"预期路径: {mmlongbench_root}")
        return None


def _create_extract_answer_function(api_key: str, base_url: str, model_name: str = None):
    """
    创建支持自定义 base_url 的 extract_answer 函数
    
    Args:
        api_key: API 密钥
        base_url: API 端点地址
        model_name: 模型名称（如果为 None，会从环境变量或默认值获取）
    
    Returns:
        包装后的 extract_answer 函数
    """
    from openai import OpenAI
    
    # 创建支持自定义 base_url 的客户端
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 如果未指定模型，使用环境变量或默认值
    if model_name is None:
        import os
        model_name = os.getenv("LLM_MODEL", "gpt-4o")
    
    def extract_answer(question, output, prompt, model_name_override=None):
        """
        从响应中提取答案（支持自定义 base_url）
        
        Args:
            question: 问题
            output: 模型输出
            prompt: 提取提示
            model_name_override: 模型名称覆盖（可选）
        
        Returns:
            提取的答案
        """
        try:
            use_model = model_name_override or model_name
            response = client.chat.completions.create(
                model=use_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                    {
                        "role": "assistant",
                        "content": "\n\nQuestion:{}\nAnalysis:{}\n".format(question, output)
                    }
                ],
                temperature=0.0,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            response = response.choices[0].message.content
        except Exception as e:
            print(f"答案提取 API 调用失败: {e}")
            response = "Failed"
        
        return response
    
    return extract_answer


class MMLongBenchTester:
    """MMLongBench-Doc 测试器"""

    def __init__(
        self,
        samples_path: str,
        document_path: str,
        output_dir: str,
        kb_name: str = None,  # 已弃用，现在每个文档使用独立知识库
        extractor_prompt_path: str = None,
        max_samples: int = None,
        start_index: int = 0,
        force_rerun: bool = False,
    ):
        """
        初始化测试器

        Args:
            samples_path: samples.json 文件路径
            document_path: PDF 文档目录路径
            output_dir: 输出目录
            kb_name: 知识库名称（已弃用，现在每个文档使用独立知识库）
            extractor_prompt_path: 答案提取提示文件路径
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

        # 加载答案提取提示
        if extractor_prompt_path:
            self.extractor_prompt_path = Path(extractor_prompt_path)
        else:
            # 默认使用 MMLongBench-Doc 的提示文件
            default_prompt = mmlongbench_root / "eval" / "prompt_for_answer_extraction.md"
            if default_prompt.exists():
                self.extractor_prompt_path = default_prompt
            else:
                raise FileNotFoundError(
                    f"找不到答案提取提示文件: {default_prompt}"
                )

        with open(self.extractor_prompt_path, "r", encoding="utf-8") as f:
            self.extractor_prompt = f.read()

        # 导入评估模块
        self.eval_modules = _import_eval_modules()
        if self.eval_modules is None:
            raise ImportError("无法导入 MMLongBench-Doc 评估模块")
        
        # 创建支持自定义 base_url 的 extract_answer 函数
        import os
        from dotenv import load_dotenv
        project_root = Path(__file__).parent.parent.parent
        load_dotenv(project_root / ".env", override=False)
        
        # 获取 LLM 配置
        api_key = os.getenv("LLM_BINDING_API_KEY")
        base_url = os.getenv("LLM_BINDING_HOST")
        model_name = os.getenv("LLM_MODEL", "gpt-4o")
        
        if not api_key or not base_url:
            raise ValueError(
                "LLM_BINDING_API_KEY 和 LLM_BINDING_HOST 必须设置才能进行答案提取"
            )
        
        # 创建支持自定义供应商的 extract_answer 函数
        self.extract_answer_func = _create_extract_answer_function(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name
        )

        # 加载样本
        self.samples = self._load_samples()

        # 知识库缓存（每个文档对应一个知识库）
        self.kb_cache = {}  # doc_id -> kb_name
        self.solver_cache = {}  # kb_name -> solver

        # 知识库基础目录
        self.kb_base_dir = Path("./data/knowledge_bases")

    def _load_samples(self) -> List[Dict[str, Any]]:
        """加载测试样本"""
        if self.results_file.exists():
            # 如果结果文件存在，从中加载（支持断点续传）
            print(f"从现有结果文件加载: {self.results_file}")
            with open(self.results_file, "r", encoding="utf-8") as f:
                samples = json.load(f)
        else:
            # 从原始 samples.json 加载
            with open(self.samples_path, "r", encoding="utf-8") as f:
                samples = json.load(f)

        # 限制样本数量
        if self.max_samples:
            samples = samples[: self.max_samples]

        # 从指定索引开始
        if self.start_index > 0:
            samples = samples[self.start_index:]

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

    def _extract_answer_from_response(
        self, question: str, response: str
    ) -> tuple[str, str]:
        """
        从响应中提取答案（支持自定义供应商和 base_url）

        Returns:
            (predicted_answer, extracted_result)
        """
        try:
            # 使用支持自定义 base_url 的 extract_answer 函数
            extracted_res = self.extract_answer_func(
                question, response, self.extractor_prompt
            )
            # 尝试从提取结果中解析答案
            if "Extracted answer:" in extracted_res:
                pred_ans = (
                    extracted_res.split("Answer format:")[0]
                    .split("Extracted answer:")[1]
                    .strip()
                )
            else:
                # 如果提取失败，尝试直接从响应中提取
                pred_ans = response.strip()[:200]  # 截取前200字符作为备选
                extracted_res = f"Failed to extract properly. Raw response: {response[:500]}"

            return pred_ans, extracted_res
        except Exception as e:
            print(f"答案提取失败: {e}")
            return "Failed to extract", f"Extraction error: {str(e)}"

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

        print(f"\n处理问题: {question[:80]}...")
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

            # 提取答案
            pred_ans, extracted_res = self._extract_answer_from_response(
                question, final_answer
            )

            # 评估答案
            try:
                score = self.eval_modules["eval_score"](
                    sample["answer"], pred_ans, sample["answer_format"]
                )
            except Exception as e:
                print(f"评估失败: {e}")
                score = 0.0

            # 更新样本
            sample["response"] = final_answer
            sample["extracted_res"] = extracted_res
            sample["pred"] = pred_ans
            sample["score"] = score
            sample["output_dir"] = result.get("output_dir", "")
            sample["kb_name"] = kb_name  # 记录使用的知识库

            print(f"预测答案: {pred_ans}")
            print(f"正确答案: {sample['answer']}")
            print(f"得分: {score}")

        except Exception as e:
            print(f"处理失败: {e}")
            import traceback

            traceback.print_exc()
            sample["response"] = f"Error: {str(e)}"
            sample["pred"] = "Failed"
            sample["score"] = 0.0
            sample["error"] = str(e)

        return sample

    async def run_tests(self):
        """运行所有测试"""
        print(f"\n开始测试，共 {len(self.samples)} 个样本")
        print(f"输出目录: {self.output_dir}")

        # 计算已完成的样本数
        completed = sum(1 for s in self.samples if "score" in s)
        print(f"已完成: {completed}/{len(self.samples)}")

        # 运行测试
        for i, sample in enumerate(tqdm(self.samples, desc="测试进度")):
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
                print("\n\n测试被用户中断")
                print("已保存当前进度，可以使用 --start_index 参数继续")
                break
            except Exception as e:
                print(f"\n处理样本 {i} 时出错: {e}")
                import traceback

                traceback.print_exc()
                continue

        # 生成最终报告
        self._generate_report()

    def _generate_report(self):
        """生成评估报告"""
        print("\n生成评估报告...")

        # MMLongBench-Doc 的 show_results 函数期望 evidence_pages 和 evidence_sources 是字符串格式
        # 如果它们已经是列表，需要转换回字符串表示
        for sample in self.samples:
            # 处理 evidence_pages
            evidence_pages = sample.get("evidence_pages")
            if evidence_pages is not None:
                if isinstance(evidence_pages, list):
                    # 如果已经是列表，转换为字符串表示（供 eval 使用）
                    sample["evidence_pages"] = repr(evidence_pages)
                elif not isinstance(evidence_pages, str):
                    # 如果不是列表也不是字符串，转换为列表再转为字符串
                    sample["evidence_pages"] = repr([evidence_pages])
                # 如果是字符串，保持不变（让 show_results 中的 eval 处理）
            
            # 处理 evidence_sources
            evidence_sources = sample.get("evidence_sources")
            if evidence_sources is not None:
                if isinstance(evidence_sources, list):
                    # 如果已经是列表，转换为字符串表示（供 eval 使用）
                    sample["evidence_sources"] = repr(evidence_sources)
                elif not isinstance(evidence_sources, str):
                    # 如果不是列表也不是字符串，转换为列表再转为字符串
                    sample["evidence_sources"] = repr([evidence_sources])
                # 如果是字符串，保持不变（让 show_results 中的 eval 处理）

        # 生成报告
        self.eval_modules["show_results"](self.samples, show_path=str(self.report_file))

        # 打印报告内容
        print("\n" + "=" * 60)
        print("评估报告")
        print("=" * 60)
        with open(self.report_file, "r", encoding="utf-8") as f:
            print(f.read())

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
        "--extractor_prompt_path",
        type=str,
        default=None,
        help="答案提取提示文件路径（默认使用 MMLongBench-Doc 的提示文件）",
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
    
    # 验证答案提取所需的配置
    # 现在答案提取使用 LLM_BINDING_API_KEY 和 LLM_BINDING_HOST，支持任何兼容 OpenAI API 的供应商
    llm_api_key = os.getenv("LLM_BINDING_API_KEY")
    llm_base_url = os.getenv("LLM_BINDING_HOST")
    if llm_api_key and llm_base_url:
        print(f"ℹ️  答案提取将使用: {llm_base_url} (模型: {os.getenv('LLM_MODEL', 'gpt-4o')})")
    else:
        print("⚠️  警告: LLM_BINDING_API_KEY 或 LLM_BINDING_HOST 未设置，答案提取可能失败")

    # 创建测试器
    tester = MMLongBenchTester(
        samples_path=args.samples_path,
        document_path=args.document_path,
        output_dir=args.output_dir,
        kb_name=args.kb_name,  # 已弃用，保留以兼容旧代码
        extractor_prompt_path=args.extractor_prompt_path,
        max_samples=args.max_samples,
        start_index=args.start_index,
        force_rerun=args.force,
    )

    # 运行测试
    asyncio.run(tester.run_tests())


if __name__ == "__main__":
    main()

