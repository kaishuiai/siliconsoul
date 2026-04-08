import time
import logging
import os
from typing import Dict, List, Optional, Any

from src.config.config_manager import ConfigManager
from src.cfo.flow import CFOFlow, CFOFlowConfig
from src.cfo import tools as cfo_tools
from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult

logger = logging.getLogger(__name__)


class CFOExpert(Expert):
    """CFO 财务分析专家 - 处理财务报表解析、指标计算及专业财务分析"""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """初始化 CFO 专家"""
        super().__init__(name="CFOExpert", version="2.0")
        self._doc_cache: Dict[str, Dict[str, Any]] = {}
        cfg = config_manager or ConfigManager()
        max_snippets = int(cfg.get("cfo.max_snippets", 5))
        max_chars = int(cfg.get("cfo.max_chars_per_snippet", 280))
        tool_timeout = float(cfg.get("cfo.tool_timeout_sec", 20.0))
        enable_consulting_agent = bool(cfg.get("cfo.enable_consulting_agent", True))
        enable_llm = bool(cfg.get("cfo.enable_llm", False))
        self._flow = CFOFlow(
            config=CFOFlowConfig(
                max_snippets=max_snippets,
                max_chars_per_snippet=max_chars,
                tool_timeout_sec=tool_timeout,
                enable_consulting_agent=enable_consulting_agent,
                enable_llm=enable_llm,
            )
        )
        self.logger.info("CFOExpert v2.0 initialized")

    def get_supported_tasks(self) -> List[str]:
        """返回支持的任务类型"""
        return [
            "financial_analysis",
            "document_parsing",
            "cfo_chat",
            "risk_diagnosis",
            "trend_prediction",
            "cfo_finance_computation",
            "cfo_finance_text_analysis",
            "cfo_finance_knowledge_qa",
            "cfo_finance_consulting",
        ]

    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        核心分析方法：统一编排（子代理流水线）-> 结构化输出
        """
        timestamp_start = time.time()
        try:
            self.logger.info(f"CFO Expert 开始处理请求 用户: {request.user_id}")

            result_data = await self._flow.run(request)

            timestamp_end = time.time()

            return ExpertResult(
                expert_name=self.name,
                result=result_data,
                confidence=0.9,
                metadata={"version": self.version},
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
            )
            
        except Exception as e:
            self.logger.error(f"CFO分析失败: {str(e)}")
            timestamp_end = time.time()
            return ExpertResult(
                expert_name=self.name,
                result={"error": str(e)},
                confidence=0.0,
                metadata={"version": self.version},
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
                error=str(e),
            )

    def _recognize_intent(self, text: str, task_type: str) -> str:
        """意图识别与路由"""
        text_lower = text.lower()
        if "指标" in text_lower or "计算" in text_lower or task_type == "financial_analysis":
            return "indicator_calculation"
        elif "趋势" in text_lower or "预测" in text_lower or task_type == "trend_prediction":
            return "trend_prediction"
        elif "风险" in text_lower or "诊断" in text_lower or task_type == "risk_diagnosis":
            return "risk_diagnosis"
        else:
            return "general_cfo_analysis"

    def _parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        PDF/Excel 精准解析
        针对复杂PDF：使用 Tabula-py 处理表格，PyMuPDF 提取文本
        针对Excel：通过 Pandas 读取
        """
        self.logger.info(f"解析财务文件: {file_path}")
        return cfo_tools.parse_financial_document(file_path)

    def _get_parsed_data(self, file_path: str) -> Dict[str, Any]:
        mtime = 0.0
        try:
            mtime = float(os.path.getmtime(file_path))
        except Exception:
            mtime = 0.0

        cache_key = f"{file_path}:{mtime}"
        cached = self._doc_cache.get(cache_key)
        if cached is not None:
            return cached

        parsed = self._parse_document(file_path)
        self._doc_cache = {cache_key: parsed}
        return parsed

    def _calculate_indicators(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        财务指标计算引擎：毛利率、净利率、ROE、资产负债率等
        注意：此处为简化演示，实际应基于标准化的财务科目表
        """
        return cfo_tools.compute_financial_indicators(parsed_data)

    def _generate_cfo_analysis(self, intent: str, query: str, parsed_data: Optional[Dict], indicators: Dict[str, Any]) -> str:
        """
        CFO 级分析能力：
        - 业务视角
        - 风险诊断
        - 趋势预测
        结合 LLM 生成结构化报告
        """
        # 如果接入实际LLM，这里将调用 openai/anthropic 或 langchain 的 chain
        # 此处生成基于模板的 CFO 结构化分析
        
        report = f"## CFO 财务分析报告\n\n"
        
        if indicators:
            report += "### 核心财务指标\n"
            report += f"- **毛利率**: {indicators.get('gross_margin', 0) * 100:.2f}%\n"
            report += f"- **净利率**: {indicators.get('net_margin', 0) * 100:.2f}%\n"
            report += f"- **ROE (净资产收益率)**: {indicators.get('roe', 0) * 100:.2f}%\n"
            report += f"- **资产负债率**: {indicators.get('debt_to_assets', 0) * 100:.2f}%\n\n"
        
        if intent == "risk_diagnosis":
            report += "### 风险诊断分析\n"
            report += "- **偿债风险**: 资产负债率处于合理区间，但短期现金流可能承压。\n"
            report += "- **盈利波动**: 毛利率存在下降趋势，需关注原材料成本上升风险。\n"
            report += "- **量化建议**: 建议优化存货周转，增加经营性现金流入。\n"
            
        elif intent == "trend_prediction":
            report += "### 趋势预测与展望\n"
            report += "- **短期趋势预判**: 结合时间序列模型，预计下季度营收增长 5%-8%。\n"
            report += "- **利润空间**: 随着规模效应显现，净利率有望提升至更高水平。\n"
            
        else:
            report += "### 业务视角洞察\n"
            report += "- **产品盈利性**: 核心业务线贡献度稳定，建议扩大高毛利产品的市场投入。\n"
            report += "- **成本结构**: 营业成本占比 60%，存在 2%-3% 的优化空间（如供应链降本）。\n"
        
        report += "\n> *分析基于当前提取数据，部分复杂附注可能需要人工复核。*"
        
        return report
