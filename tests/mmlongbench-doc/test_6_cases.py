#!/usr/bin/env python3
"""
测试6个"过早放弃"的代表性案例
验证prompt改进后的效果
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 切换工作目录到项目根目录（确保相对路径正确解析）
os.chdir(project_root)

from src.agents.solve.main_solver import MainSolver
from src.knowledge.initializer import KnowledgeBaseInitializer
from llm_answer_evaluator import LLMAnswerEvaluator

# 简单的评估器配置类
class SimplEvaluatorConfig:
    def __init__(self, output_dir: str, api_key: str, base_url: str, model: str = "gpt-4o-mini", quiet: bool = False):
        self.output_dir = output_dir
        self.api_key = api_key if api_key else os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url if base_url else "https://api.openai.com/v1"
        self.model = model
        self.quiet = quiet

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 6个代表性案例
TEST_CASES = [
    {
        "case_id": 1,
        "doc_id": "Independents-Report.pdf",
        "question": "What's the percentage of people who are democrats and voted in the last election compared to the entire population in 2018?",
        "expected_answer": "18.29%",
        "error_type": "calculation - needs decomposition"
    },
    {
        "case_id": 2,
        "doc_id": "earlybird-110722143746-phpapp02_95.pdf",
        "question": "Which two magazines' opinions are selected to illustrate the situation of German venture capital?",
        "expected_answer": "['The Economist', 'TIME']",
        "error_type": "visual/text - needs diverse queries"
    },
    {
        "case_id": 3,
        "doc_id": "reportq32015-151009093138-lva1-app6891_95.pdf",
        "question": "Which APP on APPOTA platform is top 10 Vietnam Android App, but not top 10 Vietnam iOS App?",
        "expected_answer": "UC Browser Tiếng Việt",
        "error_type": "set comparison - needs list operation"
    },
    {
        "case_id": 4,
        "doc_id": "0e94b4197b10096b1f4c699701570fbf.pdf",
        "question": "Which continent has the most number of registered participant for advanced science course in CTBTO?",
        "expected_answer": "Europe",
        "error_type": "visual data - clue tracking failure"
    },
    {
        "case_id": 5,
        "doc_id": "reportq32015-151009093138-lva1-app6891_95.pdf",
        "question": "Between Java and WP, how large is the difference in percentage of their global developers mindshare?",
        "expected_answer": "17.5",
        "error_type": "calculation - synonym query needed"
    },
    {
        "case_id": 6,
        "doc_id": "reportq32015-151009093138-lva1-app6891_95.pdf",
        "question": "Which news appear in both Vietnam mobile news and APPOTA news?",
        "expected_answer": "Bluebird Award",
        "error_type": "semantic understanding - question misinterpretation"
    }
]


class SixCaseTester:
    def __init__(
        self,
        kb_base_dir: Path,
        output_dir: Path
    ):
        self.kb_base_dir = kb_base_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化评估器
        eval_config = SimplEvaluatorConfig(
            output_dir=str(output_dir),
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1",
            model="gpt-4o-mini",
            quiet=False
        )
        self.evaluator = LLMAnswerEvaluator(eval_config)
        
        self.results = []
        
    def _get_kb_name_from_doc_id(self, doc_id: str) -> str:
        """从doc_id生成知识库名称 - 保持原始命名方式"""
        # 移除 .pdf 后缀
        base_name = doc_id.replace('.pdf', '')
        # 只替换点号，保留横线（与之前测试一致）
        kb_name = base_name.replace('.', '_')
        return f"mmlongbench_{kb_name}"
    
    def _check_kb_exists(self, kb_name: str) -> bool:
        """检查知识库是否存在"""
        kb_path = self.kb_base_dir / kb_name
        
        # 检查 rag_storage 目录和 metadata.json
        rag_storage = kb_path / "rag_storage"
        metadata_file = kb_path / "metadata.json"
        
        exists = rag_storage.exists() and metadata_file.exists()
        
        if not exists:
            logger.warning(f"知识库不存在: {kb_path}")
            logger.warning(f"  - rag_storage存在: {rag_storage.exists()}")
            logger.warning(f"  - metadata.json存在: {metadata_file.exists()}")
        
        return exists
    
    async def test_single_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """测试单个案例"""
        case_id = case['case_id']
        doc_id = case['doc_id']
        question = case['question']
        expected_answer = case['expected_answer']
        error_type = case['error_type']
        
        kb_name = self._get_kb_name_from_doc_id(doc_id)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"案例 {case_id}/{len(TEST_CASES)}: {error_type}")
        logger.info(f"文档: {doc_id}")
        logger.info(f"知识库: {kb_name}")
        logger.info(f"问题: {question[:100]}...")
        logger.info(f"正确答案: {expected_answer}")
        logger.info(f"{'='*80}\n")
        
        # 检查知识库
        if not self._check_kb_exists(kb_name):
            logger.error(f"❌ 知识库不存在，跳过此案例")
            return {
                'case_id': case_id,
                'doc_id': doc_id,
                'question': question,
                'expected_answer': expected_answer,
                'error_type': error_type,
                'status': 'skipped',
                'reason': 'Knowledge base not found'
            }
        
        try:
            # 创建输出目录
            solver_output_dir = self.output_dir / f"case_{case_id}_outputs"
            solver_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建 Main Solver
            solver = MainSolver(
                kb_name=kb_name,
                output_base_dir=str(solver_output_dir),
            )
            
            # 运行 solver
            logger.info(f"开始运行 Solver...")
            start_time = datetime.now()
            
            result = await solver.solve(question=question)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"✓ Solver 完成 (耗时: {elapsed:.1f}秒)")
            
            # 提取答案
            concise_answer = result.get('concise_answer', '')
            response = result.get('response', '')
            
            logger.info(f"\n系统输出: {concise_answer}")
            
            # 评估答案
            logger.info(f"开始评估答案...")
            eval_result = await self.evaluator.evaluate_answer(
                question=question,
                generated_answer=concise_answer,
                expected_answer=expected_answer,
                full_response=response
            )
            
            score = eval_result.get('accuracy', 0.0)
            reasoning = eval_result.get('reasoning', '')
            
            logger.info(f"{'='*80}")
            if score >= 0.5:
                logger.info(f"✅ 案例 {case_id} - 正确！ (得分: {score})")
            else:
                logger.info(f"❌ 案例 {case_id} - 错误 (得分: {score})")
            logger.info(f"评估理由: {reasoning[:200]}...")
            logger.info(f"{'='*80}\n")
            
            # 保存结果
            case_result = {
                'case_id': case_id,
                'doc_id': doc_id,
                'kb_name': kb_name,
                'question': question,
                'expected_answer': expected_answer,
                'error_type': error_type,
                'concise_answer': concise_answer,
                'full_response': response,
                'score': score,
                'eval_reasoning': reasoning,
                'elapsed_seconds': elapsed,
                'status': 'completed'
            }
            
            return case_result
            
        except Exception as e:
            logger.error(f"❌ 案例 {case_id} 执行失败: {e}", exc_info=True)
            return {
                'case_id': case_id,
                'doc_id': doc_id,
                'question': question,
                'expected_answer': expected_answer,
                'error_type': error_type,
                'status': 'failed',
                'error': str(e)
            }
    
    async def run_all_tests(self):
        """运行所有测试案例"""
        logger.info(f"\n🚀 开始测试 6 个代表性案例")
        logger.info(f"知识库目录: {self.kb_base_dir}")
        logger.info(f"输出目录: {self.output_dir}\n")
        
        for case in TEST_CASES:
            result = await self.test_single_case(case)
            self.results.append(result)
        
        # 生成报告
        self._generate_report()
    
    def _generate_report(self):
        """生成测试报告"""
        logger.info(f"\n{'='*80}")
        logger.info("测试总结")
        logger.info(f"{'='*80}\n")
        
        completed = [r for r in self.results if r['status'] == 'completed']
        skipped = [r for r in self.results if r['status'] == 'skipped']
        failed = [r for r in self.results if r['status'] == 'failed']
        
        if completed:
            correct = [r for r in completed if r['score'] >= 0.5]
            incorrect = [r for r in completed if r['score'] < 0.5]
            
            accuracy = len(correct) / len(completed) * 100 if completed else 0
            
            logger.info(f"总测试: {len(TEST_CASES)} 个案例")
            logger.info(f"完成: {len(completed)} 个")
            logger.info(f"跳过: {len(skipped)} 个")
            logger.info(f"失败: {len(failed)} 个")
            logger.info(f"\n✓ 正确: {len(correct)} 个")
            logger.info(f"✗ 错误: {len(incorrect)} 个")
            logger.info(f"\n准确率: {accuracy:.1f}% ({len(correct)}/{len(completed)})")
            
            # 详细结果
            logger.info(f"\n详细结果:")
            for r in completed:
                status_icon = "✅" if r['score'] >= 0.5 else "❌"
                logger.info(f"{status_icon} 案例 {r['case_id']}: {r['error_type']}")
                logger.info(f"   问题: {r['question'][:80]}...")
                logger.info(f"   正确: {r['expected_answer']}")
                logger.info(f"   输出: {r.get('concise_answer', 'N/A')}")
                logger.info(f"   得分: {r['score']}")
                logger.info("")
            
            # 对比基线
            logger.info(f"\n{'='*80}")
            logger.info("对比基线 (改进前这6个案例全错)")
            logger.info(f"{'='*80}")
            logger.info(f"改进前: 0/6 = 0%")
            logger.info(f"改进后: {len(correct)}/{len(completed)} = {accuracy:.1f}%")
            improvement = len(correct)
            logger.info(f"提升: +{improvement} 个正确答案 (+{improvement/6*100:.0f}%)")
        
        # 保存 JSON 结果
        result_file = self.output_dir / "6_cases_results.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n结果已保存至: {result_file}")


async def main():
    """主函数"""
    # 配置路径
    kb_base_dir = Path("/Users/howard/Documents/forks/DeepTutor/data/knowledge_bases")
    output_dir = Path(__file__).parent / "test_results" / "6_cases"
    
    # 创建测试器
    tester = SixCaseTester(
        kb_base_dir=kb_base_dir,
        output_dir=output_dir
    )
    
    # 运行测试
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
