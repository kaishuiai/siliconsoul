import pytest

from src.experts.cfo_expert import CFOExpert
from src.models.request_response import ExpertRequest


@pytest.mark.asyncio
async def test_cfo_finance_computation_via_finance_calc():
    expert = CFOExpert()
    request = ExpertRequest(
        text="帮我算一下 NPV",
        user_id="test_user",
        task_type="cfo_finance_computation",
        extra_params={
            "finance_calc": {"tool": "finance.npv", "args": {"rate": 0.1, "cashflows": [-1000, 400, 400, 400]}},
        },
    )
    result = await expert.analyze(request)
    assert result.error is None
    assert result.result.get("intent") == "finance_computation"
    assert "analysis_report" in result.result
    assert result.result.get("capability_output") is not None
    assert result.result["capability_output"]["capability"] == "cfo_finance_computation"


@pytest.mark.asyncio
async def test_cfo_finance_text_analysis_requires_file():
    expert = CFOExpert()
    request = ExpertRequest(
        text="请解读这份财报",
        user_id="test_user",
        task_type="cfo_finance_text_analysis",
        extra_params={},
    )
    result = await expert.analyze(request)
    assert result.error is None
    assert result.result.get("intent") == "finance_text_analysis"
    cap = result.result.get("capability_output") or {}
    assert cap.get("needs_followup") is True
