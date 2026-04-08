from __future__ import annotations

from typing import Any, Dict, Optional

from src.core.tools.runner import ToolRunner


class CFOIndicatorEngine:
    def __init__(self, tool_runner: ToolRunner) -> None:
        self._tool_runner = tool_runner

    async def compute(
        self,
        parsed_data: Optional[Dict[str, Any]],
        *,
        financials: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not parsed_data and not financials:
            return {}
        return await self._tool_runner.run(
            "cfo.compute_financial_indicators",
            parsed_data=parsed_data,
            financials=financials,
        )
