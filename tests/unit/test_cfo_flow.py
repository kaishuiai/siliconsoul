import pytest

from src.cfo.flow import CFOFlow
from src.cfo.tools import retrieve_document_snippets
from src.models.request_response import ExpertRequest


@pytest.mark.asyncio
async def test_cfo_flow_runs_without_file():
    flow = CFOFlow()
    req = ExpertRequest(text="分析毛利率趋势", user_id="u1", task_type="cfo_chat", extra_params={})
    out = await flow.run(req)
    assert "analysis_report" in out
    assert "intent" in out
    assert "indicators" in out
    assert out["has_parsed_data"] is False


@pytest.mark.asyncio
async def test_cfo_flow_financial_analysis_includes_valuation_and_forecast():
    flow = CFOFlow()
    req = ExpertRequest(
        text="请给出 3 年预测并做 DCF 估值与同业对比",
        user_id="u1",
        task_type="financial_analysis",
        extra_params={
            "company_name": "DemoCo",
            "financials": {
                "revenue": 1000,
                "net_income": 80,
                "total_assets": 1200,
                "total_liabilities": 500,
                "total_equity": 700,
            },
            "forecast": {"years": 3, "revenue_growth_rate": 0.1},
            "valuation": {"fcf0": 90, "fcf_growth_rate": 0.06, "discount_rate": 0.12, "terminal_growth_rate": 0.03, "years": 5},
            "peers": [
                {"name": "PeerA", "gross_margin": 0.35, "net_margin": 0.08, "roe": 0.12, "debt_to_assets": 0.55},
                {"name": "PeerB", "gross_margin": 0.42, "net_margin": 0.09, "roe": 0.14, "debt_to_assets": 0.40},
            ],
        },
    )
    out = await flow.run(req)
    assert out["intent"] in ["indicator_calculation", "finance_consulting", "general_cfo_analysis"]
    assert "sections" in out
    sections = out["sections"]
    assert "forecasting" in sections
    assert "valuation_overview" in sections
    assert "peer_comparison" in sections
    assert "sensitivity_analysis" in sections
    grid = sections["sensitivity_analysis"].get("structured", {}).get("grid", [])
    assert isinstance(grid, list)
    assert len(grid) == 9


def test_cfo_retrieve_document_snippets_basic():
    text = "第一段：本期毛利率较上期下降。\n\n第二段：存货周转加快，现金流改善。"
    snippets = retrieve_document_snippets(query="毛利率 下降", document_text=text, max_snippets=3)
    assert len(snippets) >= 1
    assert any("毛利率" in s["snippet"] for s in snippets)
