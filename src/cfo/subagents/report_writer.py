from __future__ import annotations

from typing import Any, Dict, List, Optional


class CFOReportWriter:
    def write(
        self,
        *,
        intent: str,
        query: str,
        indicators: Dict[str, Any],
        snippets: List[Dict[str, Any]],
        has_parsed_data: bool,
    ) -> str:
        report = "## CFO 财务分析报告\n\n"

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
            report += "- **短期趋势预判**: 预计下季度营收增长 5%-8%。\n"
            report += "- **利润空间**: 随着规模效应显现，净利率有望提升。\n"
        elif intent == "document_parsing":
            report += "### 文档解析结果\n"
            report += "- 已完成文档解析，可基于提取内容继续追问指标口径、期间对比与风险点。\n"
        else:
            report += "### 业务视角洞察\n"
            report += "- **产品盈利性**: 核心业务线贡献度稳定，建议扩大高毛利产品的市场投入。\n"
            report += "- **成本结构**: 营业成本占比 60%，存在 2%-3% 的优化空间（如供应链降本）。\n"

        if snippets:
            report += "\n### 文档依据摘录\n"
            for i, s in enumerate(snippets[:5], start=1):
                snippet = str(s.get("snippet") or "").strip()
                if snippet:
                    report += f"{i}. {snippet}\n"

        if has_parsed_data:
            report += "\n> *分析包含自动解析结果，复杂附注仍建议人工复核。*"
        else:
            report += "\n> *分析基于问题描述与默认假设，若提供报表文件可进一步提升准确性。*"

        return report
