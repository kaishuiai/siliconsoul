from __future__ import annotations

import asyncio
import inspect
from typing import Any, Optional

from src.core.tools.registry import ToolRegistry


class ToolRunner:
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    async def run(self, name: str, *, timeout_sec: Optional[float] = None, **kwargs: Any) -> Any:
        spec = self._registry.get(name)
        effective_timeout = timeout_sec if timeout_sec is not None else spec.timeout_sec

        async def _invoke() -> Any:
            if inspect.iscoroutinefunction(spec.fn):
                return await spec.fn(**kwargs)
            return await asyncio.to_thread(spec.fn, **kwargs)

        if effective_timeout is None:
            return await _invoke()
        return await asyncio.wait_for(_invoke(), timeout=effective_timeout)
