"""
API Gateway Module

Provides REST API gateway for SiliconSoul system.
"""

from src.api_gateway.gateway import APIGateway
from src.api_gateway.routes import create_routes

__all__ = ["APIGateway", "create_routes"]
