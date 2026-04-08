import pytest
import os

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
    assert resp["success"] is True
    assert resp["data"]["name"] == "DemoExpert"

    resp = await gateway.handle_request("GET", "/api/experts/NoSuchExpert", None)
    assert resp["status"] == "error"
    assert resp["success"] is False
    assert resp["code"] == 400
    assert isinstance(resp.get("error"), dict)


@pytest.mark.asyncio
async def test_gateway_process_and_batch_and_config():
    gateway = APIGateway()
    orchestrator = _DummyOrchestrator()
    create_routes(gateway, orchestrator)

    resp = await gateway.handle_request("POST", "/api/process", {"text": "hi", "task_type": "demo", "context": {"a": 1}})
    assert resp["status"] == "success"
    assert resp["data"]["final_result"]["echo"] == "hi"
    assert "expert_results" in resp["data"]

    resp = await gateway.handle_request("POST", "/api/batch", {"requests": [{"text": "a"}, {"text": "b"}]})
    assert resp["status"] == "success"
    assert len(resp["data"]["results"]) == 2
    assert "final_result" in resp["data"]["results"][0]
    assert len(resp["data"]["items"]) == 2
    assert resp["data"]["summary"]["total"] == 2

    resp = await gateway.handle_request("GET", "/api/config", None)
    assert resp["status"] == "success"
    assert "moe" in resp["data"]


@pytest.mark.asyncio
async def test_gateway_health_and_monitor_contract():
    gateway = APIGateway()
    orchestrator = _DummyOrchestrator()
    create_routes(gateway, orchestrator)

    health = await gateway.handle_request("GET", "/api/health", None)
    assert health["status"] == "success"
    assert "version" in health["data"]
    assert "uptime" in health["data"]
    assert "request_count" in health["data"]

    m_status = await gateway.handle_request("GET", "/api/monitor/status", None)
    assert m_status["status"] == "success"
    assert "total_requests" in m_status["data"]

    m_metrics = await gateway.handle_request("GET", "/api/monitor/metrics", None)
    assert m_metrics["status"] == "success"
    assert isinstance(m_metrics["data"], dict)


@pytest.mark.asyncio
async def test_gateway_llm_settings_runtime_update():
    gateway = APIGateway()
    orchestrator = _DummyOrchestrator()
    create_routes(gateway, orchestrator)

    os.environ.pop("LLM_PROVIDER", None)
    os.environ.pop("LLM_API_BASE", None)
    os.environ.pop("LLM_MODEL", None)
    os.environ.pop("OPENAI_API_KEY", None)

    resp = await gateway.handle_request(
        "POST",
        "/api/llm/settings",
        {"provider": "zenmux", "api_key": "k-test", "api_base": "https://example.com/v1", "model": "m1"},
    )
    assert resp["status"] == "success"
    assert resp["data"]["provider"] == "openai_compatible"
    assert resp["data"]["has_api_key"] is True

    resp = await gateway.handle_request("GET", "/api/llm/settings", None)
    assert resp["status"] == "success"
    assert resp["data"]["provider"] == "openai_compatible"
    assert resp["data"]["api_base"] == "https://example.com/v1"
    assert resp["data"]["model"] == "m1"
