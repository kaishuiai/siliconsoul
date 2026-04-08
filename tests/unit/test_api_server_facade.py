import pytest

from src.api_server.facade import OrchestratorFacade
from src.models.request_response import AggregatedResult
from src.storage.storage_manager import StorageManager


class _DummyExpert:
    def __init__(self, tasks):
        self.supported_tasks = tasks
        self.name = "Dummy"
        self.version = "1.0"


@pytest.mark.asyncio
async def test_facade_selects_experts_by_task_type(monkeypatch):
    facade = OrchestratorFacade()
    facade.storage_manager = StorageManager(storage_type="memory")
    facade.moe.experts = {
        "A": _DummyExpert(["stock_analysis"]),
        "B": _DummyExpert(["knowledge_query"]),
    }

    captured = {}

    async def fake_process_request(request, expert_names=None, timeout_sec=None):
        captured["expert_names"] = expert_names
        return AggregatedResult(
            final_result={},
            expert_results=[],
            overall_confidence=0.0,
            num_experts=0,
            consensus_level="none",
            duration_ms=0.0,
        )

    monkeypatch.setattr(facade.moe, "process_request", fake_process_request)

    await facade.process("hi", "stock_analysis", {})
    assert captured["expert_names"] == ["A"]
    assert "request_id" in (await facade.process("hi", "stock_analysis", {}))


@pytest.mark.asyncio
async def test_facade_falls_back_to_all_when_no_match(monkeypatch):
    facade = OrchestratorFacade()
    facade.storage_manager = StorageManager(storage_type="memory")
    facade.moe.experts = {"A": _DummyExpert(["other_task"])}

    captured = {}

    async def fake_process_request(request, expert_names=None, timeout_sec=None):
        captured["expert_names"] = expert_names
        return AggregatedResult(
            final_result={},
            expert_results=[],
            overall_confidence=0.0,
            num_experts=0,
            consensus_level="none",
            duration_ms=0.0,
        )

    monkeypatch.setattr(facade.moe, "process_request", fake_process_request)

    await facade.process("hi", "stock_analysis", {})
    assert captured["expert_names"] is None


@pytest.mark.asyncio
async def test_facade_batch_process_has_individual_request_ids(monkeypatch):
    facade = OrchestratorFacade()
    facade.storage_manager = StorageManager(storage_type="memory")

    async def fake_process_request(request, expert_names=None, timeout_sec=None):
        return AggregatedResult(
            final_result={"ok": True},
            expert_results=[],
            overall_confidence=0.0,
            num_experts=0,
            consensus_level="none",
            duration_ms=0.0,
        )

    monkeypatch.setattr(facade.moe, "process_request", fake_process_request)

    out = await facade.batch_process([{"text": "a"}, {"text": "b"}], user_id="u1")
    assert out["summary"]["total"] == 2
    assert out["summary"]["success"] == 2
    assert out["summary"]["failed"] == 0
    assert len(out["items"]) == 2
    assert out["items"][0]["data"]["request_id"] != out["items"][1]["data"]["request_id"]


@pytest.mark.asyncio
async def test_facade_batch_process_partial_failure_isolated(monkeypatch):
    facade = OrchestratorFacade()
    facade.storage_manager = StorageManager(storage_type="memory")

    async def fake_process_request(request, expert_names=None, timeout_sec=None):
        if request.text == "bad":
            raise ValueError("bad request")
        return AggregatedResult(
            final_result={"ok": True},
            expert_results=[],
            overall_confidence=0.0,
            num_experts=0,
            consensus_level="none",
            duration_ms=0.0,
        )

    monkeypatch.setattr(facade.moe, "process_request", fake_process_request)

    out = await facade.batch_process([{"text": "a"}, {"text": "bad"}, {"text": "c"}], user_id="u1")
    assert out["summary"]["total"] == 3
    assert out["summary"]["success"] == 2
    assert out["summary"]["failed"] == 1
    assert out["items"][1]["success"] is False
