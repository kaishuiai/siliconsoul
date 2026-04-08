"""
API Gateway

Core API gateway for SiliconSoul.
"""

import inspect
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
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

            handler, params = self._resolve_route(path, method)
            if handler is None:
                if self._path_exists(path):
                    return self._error_response(405, "Method not allowed")
                return self._error_response(404, "Route not found")

            result = await self._call_handler(handler, body, params)

            logger.info(f"{method} {path} - 200")
            return self._success_response(result)

        except Exception as e:
            self.error_count += 1
            logger.error(f"{method} {path} - {str(e)}")
            if isinstance(e, ValueError):
                return self._error_response(400, str(e))
            return self._error_response(500, str(e))

    def _path_exists(self, path: str) -> bool:
        if path in self.routes:
            return True
        for template in self.routes.keys():
            if "<" in template and self._match_template(template, path) is not None:
                return True
        return False

    def _resolve_route(self, path: str, method: str) -> tuple[Optional[Callable], Dict[str, str]]:
        if path in self.routes and method in self.routes[path]:
            return self.routes[path][method], {}

        for template, methods in self.routes.items():
            if "<" not in template:
                continue
            params = self._match_template(template, path)
            if params is None:
                continue
            if method in methods:
                return methods[method], params

        return None, {}

    def _match_template(self, template: str, path: str) -> Optional[Dict[str, str]]:
        template_parts = [p for p in template.strip("/").split("/") if p]
        path_parts = [p for p in path.strip("/").split("/") if p]
        if len(template_parts) != len(path_parts):
            return None

        params: Dict[str, str] = {}
        for t, p in zip(template_parts, path_parts):
            if t.startswith("<") and t.endswith(">"):
                key = t[1:-1].strip()
                if not key:
                    return None
                params[key] = p
                continue
            if t != p:
                return None
        return params

    async def _call_handler(
        self, handler: Callable, body: Optional[Dict[str, Any]], params: Dict[str, str]
    ) -> Any:
        sig = inspect.signature(handler)
        kwargs: Dict[str, Any] = {}
        if "body" in sig.parameters:
            kwargs["body"] = body
        elif sig.parameters:
            kwargs[list(sig.parameters.keys())[0]] = body
        for k, v in params.items():
            if k in sig.parameters:
                kwargs[k] = v
        result = handler(**kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    def _success_response(self, data: Any) -> Dict[str, Any]:
        """Create success response"""
        now = datetime.now().isoformat()
        ts = time.time()
        return {
            "success": True,
            "status": "success",
            "data": data,
            "timestamp": ts,
            "timestamp_iso": now,
        }

    def _error_response(self, status_code: int, message: str) -> Dict[str, Any]:
        """Create error response"""
        now = datetime.now().isoformat()
        ts = time.time()
        return {
            "success": False,
            "status": "error",
            "code": status_code,
            "message": message,
            "error": {"code": status_code, "message": message},
            "timestamp": ts,
            "timestamp_iso": now,
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
