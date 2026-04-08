import pytest

from src.api_gateway.gateway import APIGateway
from src.api_gateway.routes import create_routes
from src.config.config_manager import ConfigManager
from src.monitoring.monitor import SystemMonitor


class _DummyExpert:
    def __init__(self, name: str):
        self.name = name
        self.version = "1.0"
        self.supported_tasks = ["demo"]


class _DummyOrchestrator:
    def __init__(self):
        self.experts = {"DemoExpert": _DummyExpert("DemoExpert")}
        self.request_count = 0
        self.monitor = SystemMonitor()
        self.config_manager = ConfigManager()

    async def process(self, text, task_type=None, context=None, **kwargs):
        self.request_count += 1
        return {"echo": text, "task_type": task_type, "context": context or {}, "ok": True}

    async def batch_process(self, requests, **kwargs):
        results = []
        for r in requests:
            results.append(await self.process(r.get("text", ""), r.get("task_type"), r.get("context", {})))
        return results


@pytest.mark.asyncio
async def test_gateway_supports_path_params_and_value_error_to_400():
    gateway = APIGateway()
    orchestrator = _DummyOrchestrator()
    create_routes(gateway, orchestrator)

    resp = await gateway.handle_request("GET", "/api/experts/DemoExpert", None)
    assert resp["status"] == "success"
    assert resp["data"]["name"] == "DemoExpert"

    resp = await gateway.handle_request("GET", "/api/experts/NoSuchExpert", None)
    assert resp["status"] == "error"
    assert resp["code"] == 400


@pytest.mark.asyncio
async def test_gateway_process_and_batch_and_config():
    gateway = APIGateway()
    orchestrator = _DummyOrchestrator()
    create_routes(gateway, orchestrator)

    resp = await gateway.handle_request("POST", "/api/process", {"text": "hi", "task_type": "demo", "context": {"a": 1}})
    assert resp["status"] == "success"
    assert resp["data"]["results"]["echo"] == "hi"

    resp = await gateway.handle_request("POST", "/api/batch", {"requests": [{"text": "a"}, {"text": "b"}]})
    assert resp["status"] == "success"
    assert len(resp["data"]["results"]) == 2
    assert "echo" in resp["data"]["results"][0]

    resp = await gateway.handle_request("GET", "/api/config", None)
    assert resp["status"] == "success"
    assert "moe" in resp["data"]
