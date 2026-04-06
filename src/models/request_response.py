"""
Data Models for SiliconSoul MOE System

This module defines the core Pydantic models for request/response handling.
All data flowing through the MOE system uses these standardized models.

Models:
- ExpertRequest: Input format for all experts
- ExpertResult: Output format from individual experts
- AggregatedResult: Final output combining all expert results
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ExpertRequest(BaseModel):
    """
    Unified request format for all experts.
    
    This model standardizes all input to experts, ensuring consistent
    interface regardless of how the request originates.
    
    Attributes:
        text: The main user input text (required)
        user_id: Unique identifier for the user (required)
        context: Conversation history or background context (optional)
        task_type: Pre-classified task type if available (optional)
        timestamp: Request time (auto-set to current time)
        extra_params: Additional parameters for extensibility (optional)
    
    Examples:
        >>> request = ExpertRequest(
        ...     text="What is the stock price of Apple?",
        ...     user_id="user_123",
        ...     task_type="stock_analysis"
        ... )
    """
    
    # Core required fields
    text: str = Field(
        ...,
        description="User input text",
        min_length=1,
        max_length=10000
    )
    
    user_id: str = Field(
        ...,
        description="User identifier",
        min_length=1,
        max_length=256
    )
    
    # Optional fields
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Conversation context or background information"
    )
    
    task_type: Optional[str] = Field(
        default=None,
        description="Pre-classified task type (e.g., 'stock_analysis', 'knowledge_query')"
    )
    
    timestamp: float = Field(
        default_factory=lambda: datetime.now().timestamp(),
        description="Request timestamp (auto-set to current time)"
    )
    
    extra_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional parameters for extensibility"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "text": "Should I buy AAPL stock?",
                "user_id": "user_123",
                "context": {
                    "previous_topic": "stocks",
                    "user_risk_profile": "aggressive"
                },
                "task_type": "stock_analysis",
                "timestamp": 1712462640.0
            }
        }


class ExpertResult(BaseModel):
    """
    Unified result format for individual experts.
    
    Each expert returns results in this standardized format.
    The framework uses this to aggregate and manage expert outputs.
    
    Attributes:
        expert_name: Name of the expert that produced this result
        result: Dictionary containing the analysis result (structure varies by expert)
        confidence: Confidence score from 0 (no confidence) to 1 (high confidence)
        metadata: Additional metadata about the analysis
        timestamp_start: When execution started (Unix timestamp)
        timestamp_end: When execution completed (Unix timestamp)
        error: Error message if execution failed (optional)
    
    Properties:
        duration_ms: Property that calculates execution duration in milliseconds
    
    Examples:
        >>> result = ExpertResult(
        ...     expert_name="StockAnalysisExpert",
        ...     result={"recommendation": "BUY", "target_price": 150.0},
        ...     confidence=0.92,
        ...     metadata={"version": "1.0", "model": "xgboost_v2"},
        ...     timestamp_start=1712462640.0,
        ...     timestamp_end=1712462641.5
        ... )
        >>> print(result.duration_ms)  # 1500.0
    """
    
    # Core fields
    expert_name: str = Field(
        ...,
        description="Name of the expert",
        min_length=1,
        max_length=128
    )
    
    result: Dict[str, Any] = Field(
        ...,
        description="Analysis result (structure varies by expert)"
    )
    
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score from 0 to 1"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (version, model, execution details, etc.)"
    )
    
    # Timing information
    timestamp_start: float = Field(
        ...,
        description="Execution start time (Unix timestamp)"
    )
    
    timestamp_end: float = Field(
        ...,
        description="Execution end time (Unix timestamp)"
    )
    
    # Error handling
    error: Optional[str] = Field(
        default=None,
        description="Error message if execution failed"
    )
    
    @property
    def duration_ms(self) -> float:
        """
        Calculate execution duration in milliseconds.
        
        Returns:
            float: Duration in milliseconds
        """
        return (self.timestamp_end - self.timestamp_start) * 1000
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "expert_name": "StockAnalysisExpert",
                "result": {
                    "recommendation": "BUY",
                    "confidence_score": 0.92,
                    "target_price": 150.0,
                    "reasoning": "Technical analysis shows breakout pattern"
                },
                "confidence": 0.92,
                "metadata": {
                    "version": "1.0",
                    "model": "xgboost_v2",
                    "model_version": "2.3.1"
                },
                "timestamp_start": 1712462640.0,
                "timestamp_end": 1712462641.5,
                "error": None
            }
        }


class AggregatedResult(BaseModel):
    """
    Final aggregated result combining all expert outputs.
    
    After all experts complete, their results are combined into a single
    AggregatedResult that contains the final decision and supporting information.
    
    Attributes:
        final_result: The aggregated/combined decision and analysis
        expert_results: List of individual expert results
        overall_confidence: Average confidence across all experts
        num_experts: Number of experts that contributed
        consensus_level: Agreement level ("high", "medium", "low")
        duration_ms: Total execution time in milliseconds
    
    Examples:
        >>> aggregated = AggregatedResult(
        ...     final_result={
        ...         "decision": "BUY",
        ...         "confidence": 0.93,
        ...         "reasoning": "All experts agree on buying signal"
        ...     },
        ...     expert_results=[...],
        ...     overall_confidence=0.93,
        ...     num_experts=3,
        ...     consensus_level="high",
        ...     duration_ms=620.0
        ... )
    """
    
    # Final result
    final_result: Dict[str, Any] = Field(
        ...,
        description="Aggregated final decision and analysis"
    )
    
    # Source information
    expert_results: List[ExpertResult] = Field(
        ...,
        description="List of all expert results that were aggregated"
    )
    
    # Aggregation statistics
    overall_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence score (usually average of individual confidences)"
    )
    
    num_experts: int = Field(
        ...,
        ge=0,
        description="Number of experts that contributed results"
    )
    
    consensus_level: str = Field(
        ...,
        description="Consensus level indicating agreement among experts (high/medium/low)"
    )
    
    # Timing
    duration_ms: float = Field(
        ...,
        ge=0.0,
        description="Total execution duration in milliseconds"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "final_result": {
                    "decision": "BUY",
                    "recommendation": "STRONG_BUY",
                    "confidence": 0.93,
                    "reasoning": "Technical and fundamental analysis align"
                },
                "expert_results": [],  # Would contain actual ExpertResult objects
                "overall_confidence": 0.93,
                "num_experts": 3,
                "consensus_level": "high",
                "duration_ms": 620.0
            }
        }


# Type aliases for convenience
RequestType = ExpertRequest
ResultType = ExpertResult
AggregatedType = AggregatedResult
