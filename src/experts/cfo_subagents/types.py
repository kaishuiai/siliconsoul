from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class CFOAgentOutput:
    capability: str
    answer_markdown: str
    structured: Dict[str, Any]
    confidence: float
    needs_followup: bool = False
    followup_question: Optional[str] = None
