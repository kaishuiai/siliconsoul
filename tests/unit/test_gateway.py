"""
Unit tests for API gateway
"""

import pytest
from src.api_gateway.gateway import APIGateway


class TestAPIGateway:
    """Tests for API gateway"""

    def test_gateway_creation(self):
        """Test creating gateway"""
        gateway = APIGateway(host="localhost", port=8000)
        assert gateway.host == "localhost"
        assert gateway.port == 8000

    def test_register_route(self):
        """Test registering a route"""
        gateway = APIGateway()

        @gateway.route("/test", methods=["GET"])
        async def test_handler(body):
            return {"message": "test"}

        assert "/test" in gateway.routes
        assert "GET" in gateway.routes["/test"]

    def test_add_middleware(self):
        """Test adding middleware"""
        gateway = APIGateway()

        def test_middleware(method, path, body):
            pass

        gateway.add_middleware(test_middleware)
        assert len(gateway.middleware) == 1

    def test_gateway_stats(self):
        """Test gateway statistics"""
        gateway = APIGateway()
        stats = gateway.get_stats()

        assert stats["host"] == "0.0.0.0"
        assert stats["port"] == 8000
        assert stats["request_count"] == 0
        assert stats["error_count"] == 0
