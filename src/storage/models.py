"""
Storage Data Models

Defines data structures for persistent storage.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class RequestRecord:
    """
    Record of a request to the system.
    
    Attributes:
        request_id: Unique request identifier
        user_id: User who made the request
        text: Request text
        timestamp: Request timestamp
        context: Additional context data
    """
    request_id: str
    user_id: str
    text: str
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if data['timestamp']:
            data['timestamp'] = data['timestamp'].isoformat()
        return data


@dataclass
class ResultRecord:
    """
    Record of Expert result.
    
    Attributes:
        result_id: Unique result identifier
        request_id: Associated request ID
        expert_name: Name of Expert that generated result
        result: The actual result data
        confidence: Confidence score (0-1)
        duration_ms: Execution duration in milliseconds
        timestamp: Result timestamp
    """
    result_id: str
    request_id: str
    expert_name: str
    result: Dict[str, Any]
    confidence: float
    duration_ms: float
    timestamp: datetime
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if data['timestamp']:
            data['timestamp'] = data['timestamp'].isoformat()
        return data
