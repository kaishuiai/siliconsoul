import pytest

from src.core.tools.registry import ToolRegistry, ToolSpec
from src.core.tools.runner import ToolRunner
from src.experts.cfo_subagents.computation_agent import CFOComputationAgent
from src.experts.cfo_subagents.knowledge_qa_agent import CFOKnowledgeQAAgent
from src.experts.cfo_subagents.simple_retrieval import chunk_text, rank_chunks_by_keyword_overlap
from src.experts.cfo_subagents.text_analysis_agent import CFOTextAnalysisAgent
from src.finance import (
    amortization_schedule,
    break_even_quantity,
    cagr,
    fv,
    growth_rate,
    irr,
    npv,
    pv,
    solve_linear,
    solve_quadratic,
)
from src.llm.client import LLMClient


def _make_tool_runner() -> ToolRunner:
    reg = ToolRegistry()
    reg.register(ToolSpec(name="finance.growth_rate", fn=growth_rate))
    reg.register(ToolSpec(name="finance.cagr", fn=cagr))
    reg.register(ToolSpec(name="finance.npv", fn=npv))
    reg.register(ToolSpec(name="finance.irr", fn=irr))
    reg.register(ToolSpec(name="finance.pv", fn=pv))
    reg.register(ToolSpec(name="finance.fv", fn=fv))
    reg.register(ToolSpec(name="finance.amortization", fn=amortization_schedule))
    reg.register(ToolSpec(name="finance.break_even", fn=break_even_quantity))
    reg.register(ToolSpec(name="math.solve_linear", fn=solve_linear))
    reg.register(ToolSpec(name="math.solve_quadratic", fn=solve_quadratic))
    return ToolRunner(reg)


@pytest.mark.asyncio
async def test_computation_agent_rule_based_npv():
    runner = _make_tool_runner()
    agent = CFOComputationAgent()
    out = await agent.run(query="NPV 折现率 10% 现金流 -1000, 400, 400, 400", tool_runner=runner, llm=None)
    assert out.capability == "cfo_finance_computation"
    assert "CFO 财务计算结果" in out.answer_markdown
    assert out.confidence > 0.6


@pytest.mark.asyncio
async def test_computation_agent_explicit_spec():
    runner = _make_tool_runner()
    agent = CFOComputationAgent()
    out = await agent.run(
        query="",
        tool_runner=runner,
        llm=None,
        extra_params={"finance_calc": {"tool": "finance.break_even", "args": {"fixed_cost": 1000, "price": 10, "variable_cost": 6}}},
    )
    assert out.structured["value"] == 250.0


def test_simple_retrieval_ranker():
    chunks = chunk_text("第一段：营业收入增长。\n\n第二段：经营现金流下降。", max_chars=200, overlap=0)
    ranked = rank_chunks_by_keyword_overlap("现金流", chunks, top_k=3)
    assert ranked
    assert any("现金流" in c.content for c in ranked)


@pytest.mark.asyncio
async def test_text_analysis_agent_without_llm_fallback():
    agent = CFOTextAnalysisAgent()
    parsed_data = {"text": "公司营业收入为 100，净利润为 10。", "tables": []}
    out = await agent.run(query="请解读", parsed_data=parsed_data, llm=None)
    assert out.capability == "cfo_finance_text_analysis"
    assert "CFO 报表解读" in out.answer_markdown


@pytest.mark.asyncio
async def test_knowledge_qa_agent_without_llm_returns_evidence():
    agent = CFOKnowledgeQAAgent()
    parsed_data = {"text": "本期经营活动产生的现金流量净额下降，主要由于应收账款增加。", "tables": []}
    out = await agent.run(query="现金流为何下降？", parsed_data=parsed_data, llm=None, user_id="u1")
    assert out.capability == "cfo_finance_knowledge_qa"
    assert "资料检索问答" in out.answer_markdown


def test_llm_client_availability(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    llm = LLMClient()
    assert llm.is_available() is False
