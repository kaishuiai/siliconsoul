import pytest
import asyncio
from src.experts.cfo_expert import CFOExpert
from src.models.request_response import ExpertRequest

@pytest.mark.asyncio
async def test_cfo_expert_analyze_basic():
    expert = CFOExpert()
    
    # 测试基础对话意图
    request = ExpertRequest(
        text="帮我分析一下毛利率趋势",
        user_id="test_user",
        task_type="cfo_chat",
        extra_params={}
    )
    
    result = await expert.analyze(request)
    
    assert result.expert_name == "CFOExpert"
    assert result.error is None
    assert "analysis_report" in result.result
    assert "intent" in result.result

@pytest.mark.asyncio
async def test_cfo_expert_indicator_calculation():
    expert = CFOExpert()
    
    # 测试指标计算
    parsed_data = {"dummy": "data"} # Mock parsed data
    indicators = expert._calculate_indicators(parsed_data)
    
    assert "gross_margin" in indicators
    assert "net_margin" in indicators
    assert "roe" in indicators
    assert indicators["gross_margin"] == 0.4000  # (10000 - 6000) / 10000
    assert indicators["roe"] == 0.0750  # 1500 / 20000
