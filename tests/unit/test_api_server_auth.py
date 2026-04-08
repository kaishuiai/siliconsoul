import pytest
from aiohttp.test_utils import TestClient, TestServer

from src.api_server.server import create_app
from src.storage.storage_manager import StorageManager


@pytest.mark.asyncio
async def test_auth_disabled_allows_requests():
    app = create_app(config_path=None)
    app["orchestrator"].storage_manager = StorageManager(storage_type="memory")

    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()
    try:
        resp = await client.get("/api/health")
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "success"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_auth_enabled_requires_token_and_binds_user_id():
    app = create_app(config_path=None)
    orchestrator = app["orchestrator"]
    orchestrator.storage_manager = StorageManager(storage_type="memory")
    orchestrator.config_manager.config.setdefault("auth", {})
    orchestrator.config_manager.config["auth"]["enabled"] = True
    orchestrator.config_manager.config["auth"]["tokens"] = {"t1": "u1"}
    orchestrator.config_manager.config["auth"]["exempt_paths"] = ["/api/health", "/api/me"]

    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()
    try:
        resp = await client.get("/api/experts")
        assert resp.status == 401

        resp = await client.get("/api/me", headers={"Authorization": "Bearer t1"})
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "success"
        assert data["data"]["user_id"] == "u1"

        resp = await client.get("/api/portfolio/u2", headers={"Authorization": "Bearer t1"})
        assert resp.status == 403
    finally:
        await client.close()
