import pytest

from src.api_gateway.gateway import APIGateway
from src.api_gateway.routes import create_routes
from src.portfolio.portfolio_manager import PortfolioManager


class _DummyOrchestrator:
    def __init__(self):
        self.request_count = 0
        self.experts = {}
        self.monitor = None
        self.config_manager = None
        self.portfolio_manager = PortfolioManager(storage_type="memory")


@pytest.mark.asyncio
async def test_portfolio_crud_and_stats():
    gateway = APIGateway()
    orchestrator = _DummyOrchestrator()
    create_routes(gateway, orchestrator)

    resp = await gateway.handle_request("GET", "/api/portfolio/u1", None)
    assert resp["status"] == "success"
    assert resp["data"]["user_id"] == "u1"
    assert resp["data"]["positions"] == []

    resp = await gateway.handle_request(
        "POST", "/api/portfolio/u1/positions", {"symbol": "600000.SH", "quantity": 100}
    )
    assert resp["status"] == "success"
    assert resp["data"]["symbol"] == "600000.SH"
    assert resp["data"]["quantity"] == 100

    resp = await gateway.handle_request("GET", "/api/portfolio/u1", None)
    assert resp["status"] == "success"
    assert len(resp["data"]["positions"]) == 1

    resp = await gateway.handle_request("GET", "/api/portfolio/u1/stats", None)
    assert resp["status"] == "success"
    assert resp["data"]["positions_count"] == 1
    assert resp["data"]["total_quantity"] == 100

    resp = await gateway.handle_request(
        "POST", "/api/portfolio/u1/positions", {"symbol": "600000.SH", "quantity": 0}
    )
    assert resp["status"] == "success"

    resp = await gateway.handle_request("GET", "/api/portfolio/u1/stats", None)
    assert resp["status"] == "success"
    assert resp["data"]["positions_count"] == 0
