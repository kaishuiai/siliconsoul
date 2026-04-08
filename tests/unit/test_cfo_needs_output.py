import pytest

from src.experts.cfo_expert import CFOExpert
from src.models.request_response import ExpertRequest


@pytest.mark.asyncio
async def test_cfo_flow_returns_needs_when_data_insufficient():
    expert = CFOExpert()
    req = ExpertRequest(text="请对某子业务做单独财务分析", user_id="u1", task_type="cfo_chat", extra_params={})
    res = await expert.analyze(req)
    assert res.error is None
    out = res.result or {}
    needs = out.get("needs")
    assert isinstance(needs, list)
    assert len(needs) > 0
