"""
API Gateway

Core API gateway for SiliconSoul.
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from src.logging.logger import get_logger

logger = get_logger("api_gateway")


class APIGateway:
    """REST API Gateway for SiliconSoul"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Initialize API gateway.

        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        self.routes: Dict[str, Dict[str, Callable]] = {}
        self.middleware: List[Callable] = []
        self.request_count = 0
        self.error_count = 0

    def route(self, path: str, methods: List[str] = None):
        """
        Register a route.

        Args:
            path: Route path
            methods: HTTP methods

        Returns:
            Decorator function
        """
        if methods is None:
            methods = ["GET"]

        def decorator(func: Callable):
            if path not in self.routes:
                self.routes[path] = {}

            for method in methods:
                self.routes[path][method] = func
                logger.info(f"Registered route: {method} {path}")

            return func

        return decorator

    def add_middleware(self, middleware: Callable) -> None:
        """
        Add middleware.

        Args:
            middleware: Middleware function
        """
        self.middleware.append(middleware)
        logger.info(f"Added middleware: {middleware.__name__}")

    async def handle_request(
        self, method: str, path: str, body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle a request.

        Args:
            method: HTTP method
            path: Request path
            body: Request body

        Returns:
            Response dictionary
        """
        self.request_count += 1

        try:
            # Execute middleware
            for middleware in self.middleware:
                result = await middleware(method, path, body) if hasattr(middleware, '__await__') else middleware(method, path, body)
                if result is not None:
                    return result

            # Find route
            if path not in self.routes:
                return self._error_response(404, "Route not found")

            if method not in self.routes[path]:
                return self._error_response(405, "Method not allowed")

            # Execute handler
            handler = self.routes[path][method]
            result = await handler(body) if hasattr(handler, '__await__') else handler(body)

            logger.info(f"{method} {path} - 200")
            return self._success_response(result)

        except Exception as e:
            self.error_count += 1
            logger.error(f"{method} {path} - {str(e)}")
            return self._error_response(500, str(e))

    def _success_response(self, data: Any) -> Dict[str, Any]:
        """Create success response"""
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }

    def _error_response(self, status_code: int, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "status": "error",
            "code": status_code,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get gateway statistics"""
        return {
            "host": self.host,
            "port": self.port,
            "routes_count": len(self.routes),
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": (
                self.error_count / self.request_count * 100
                if self.request_count > 0
                else 0.0
            ),
        }
