import pytest

from src.cfo.subagents.section_orchestrator import CFOSectionOrchestrator


def test_section_orchestrator_valuation_invalid_rates():
    orch = CFOSectionOrchestrator()
    sections = orch.build_sections(
        query="做 DCF 估值",
        task_type="financial_analysis",
        intent="finance_consulting",
        indicators={"values": {"revenue": 1000, "net_income": 80}},
        snippets=[],
        has_parsed_data=False,
        extra_params={
            "valuation": {"fcf0": 100, "fcf_growth_rate": 0.05, "discount_rate": 0.03, "terminal_growth_rate": 0.03, "years": 5},
            "forecast": {"years": 3, "revenue_growth_rate": 0.1},
        },
    )
    assert "valuation_overview" in sections
    assert "折现率必须大于永续增长率" in sections["valuation_overview"]["markdown"]
    assert "sensitivity_analysis" in sections
    assert "无法做敏感性分析" in sections["sensitivity_analysis"]["markdown"]


def test_section_orchestrator_forecast_missing_revenue():
    orch = CFOSectionOrchestrator()
    sections = orch.build_sections(
        query="做 3 年收入预测",
        task_type="financial_analysis",
        intent="finance_consulting",
        indicators={},
        snippets=[],
        has_parsed_data=False,
        extra_params={"forecast": {"years": 3, "revenue_growth_rate": 0.1}},
    )
    assert "forecasting" in sections
    assert "缺少可用的收入/利润基数" in sections["forecasting"]["markdown"]

