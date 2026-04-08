import pytest

from src.api_gateway.gateway import APIGateway
from src.api_gateway.routes import create_routes
from src.config.config_manager import ConfigManager
from src.storage.storage_manager import StorageManager


class _DummyOrchestrator:
    def __init__(self):
        self.request_count = 0
        self.experts = {}
        self.monitor = None
        self.config_manager = ConfigManager()
        self.storage_manager = StorageManager(storage_type="memory")


@pytest.mark.asyncio
async def test_me_and_history_endpoints():
    gateway = APIGateway()
    orchestrator = _DummyOrchestrator()
    create_routes(gateway, orchestrator)

    resp = await gateway.handle_request("GET", "/api/me", {"user_id": "u1"})
    assert resp["status"] == "success"
    assert resp["data"]["user_id"] == "u1"

    request_id = orchestrator.storage_manager.add_request("u1", "hello world", context={"_meta": {"task_type": "cfo_chat"}})
    request_id_2 = orchestrator.storage_manager.add_request("u1", "another request", context={"_meta": {"task_type": "stock_analysis"}})
    orchestrator.storage_manager.add_result(
        request_id=request_id,
        expert_name="DemoExpert",
        result={"ok": True},
        confidence=0.5,
        duration_ms=1.0,
        error="boom",
    )
    orchestrator.storage_manager.add_aggregated(
        request_id=request_id,
        aggregated={"final_result": {"ok": True}, "overall_confidence": 0.6, "consensus_level": "high", "num_experts": 1},
        confidence=0.6,
        duration_ms=2.0,
    )
    orchestrator.storage_manager.add_result(
        request_id=request_id_2,
        expert_name="DemoExpert",
        result={"ok": True},
        confidence=0.5,
        duration_ms=1.0,
        error=None,
    )
    orchestrator.storage_manager.add_aggregated(
        request_id=request_id_2,
        aggregated={"final_result": {"ok": True}, "overall_confidence": 0.2, "consensus_level": "low", "num_experts": 1},
        confidence=0.2,
        duration_ms=2.0,
    )

    resp = await gateway.handle_request("GET", "/api/history/u1", {"limit": 10, "offset": 0})
    assert resp["status"] == "success"
    assert len(resp["data"]["items"]) == 2
    assert any(it.get("task_type") == "cfo_chat" for it in resp["data"]["items"])

    resp = await gateway.handle_request("GET", "/api/history/u1", {"limit": 10, "offset": 0, "expert_name": "DemoExpert"})
    assert resp["status"] == "success"
    assert len(resp["data"]["items"]) == 2

    resp = await gateway.handle_request("GET", "/api/history/u1", {"limit": 10, "offset": 0, "expert_name": "NoSuchExpert"})
    assert resp["status"] == "success"
    assert len(resp["data"]["items"]) == 0

    resp = await gateway.handle_request("GET", "/api/history/u1", {"limit": 10, "offset": 0, "consensus_level": "high"})
    assert resp["status"] == "success"
    assert len(resp["data"]["items"]) == 1

    resp = await gateway.handle_request("GET", "/api/history/u1", {"limit": 10, "offset": 0, "consensus_level": "low"})
    assert resp["status"] == "success"
    assert len(resp["data"]["items"]) == 1

    resp = await gateway.handle_request("GET", "/api/history/u1", {"limit": 10, "offset": 0, "only_errors": "true"})
    assert resp["status"] == "success"
    assert len(resp["data"]["items"]) == 1

    resp = await gateway.handle_request("GET", "/api/history/u1", {"limit": 10, "offset": 0, "task_type": "cfo_chat"})
    assert resp["status"] == "success"
    assert len(resp["data"]["items"]) == 1

    resp = await gateway.handle_request("GET", f"/api/history/u1/{request_id}", None)
    assert resp["status"] == "success"
    assert resp["data"]["request"]["request_id"] == request_id
    assert len(resp["data"]["results"]) == 2


@pytest.mark.asyncio
async def test_history_replay_endpoint(monkeypatch):
    gateway = APIGateway()
    orchestrator = _DummyOrchestrator()
    create_routes(gateway, orchestrator)

    request_id = orchestrator.storage_manager.add_request("u1", "hello", context={"a": 1})

    async def fake_process(text, task_type=None, context=None, **kwargs):
        return {
            "request_id": "new_req",
            "echo": text,
            "task_type": task_type,
            "context": context,
            "expert_names": kwargs.get("expert_names"),
            "extra": kwargs.get("extra_params"),
        }

    monkeypatch.setattr(orchestrator, "process", fake_process, raising=False)

    resp = await gateway.handle_request(
        "POST",
        f"/api/history/u1/{request_id}/replay",
        {"task_type": "stock_analysis", "expert_names": ["DemoExpert"]},
    )
    assert resp["status"] == "success"
    assert resp["data"]["request_id"] == "new_req"
    assert resp["data"]["echo"] == "hello"
    assert resp["data"]["task_type"] == "stock_analysis"
    assert resp["data"]["context"] == {"a": 1}
    assert resp["data"]["expert_names"] == ["DemoExpert"]
