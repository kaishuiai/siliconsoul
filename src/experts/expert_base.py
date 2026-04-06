"""
Expert Base Class - Foundation for all experts in SiliconSoul MOE

This module defines the abstract base class that all experts must inherit from.
It provides:
- Standard interface (async def analyze method)
- Automatic error handling and timeout enforcement
- Performance monitoring and statistics tracking
- Logging infrastructure
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import asyncio
import logging
from datetime import datetime

from src.models.request_response import ExpertRequest, ExpertResult


# Configure logger
logger = logging.getLogger(__name__)


class Expert(ABC):
    """
    Abstract base class for all experts in the MOE system.
    
    Every expert (stock analysis, knowledge retrieval, dialog, etc.) must
    inherit from this class and implement the analyze() method.
    
    The framework handles:
    - Timeout enforcement (default 2 seconds)
    - Exception catching and error reporting
    - Performance monitoring
    - Logging
    
    Attributes:
        name: Expert identifier (e.g., "StockAnalysisExpert")
        version: Version number (e.g., "1.0")
        _stats: Performance statistics (call count, errors, duration)
    
    Example:
        >>> class MyExpert(Expert):
        ...     def __init__(self):
        ...         super().__init__(name="MyExpert", version="1.0")
        ...
        ...     async def analyze(self, request: ExpertRequest) -> ExpertResult:
        ...         # Your analysis logic here
        ...         return ExpertResult(...)
        ...
        ...     def get_supported_tasks(self) -> list:
        ...         return ["my_task_type"]
    """
    
    def __init__(self, name: str, version: str = "1.0"):
        """
        Initialize an expert.
        
        Args:
            name: Expert name (e.g., "StockAnalysisExpert")
            version: Version number (default "1.0")
        
        Raises:
            ValueError: If name is empty or not a valid identifier
        """
        if not name or not isinstance(name, str):
            raise ValueError("Expert name must be a non-empty string")
        
        self.name = name
        self.version = version
        
        # Create logger for this expert
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # Statistics tracking
        self._stats = {
            "call_count": 0,
            "error_count": 0,
            "total_duration_ms": 0.0,
            "min_duration_ms": float('inf'),
            "max_duration_ms": 0.0,
        }
        
        self.logger.debug(f"Initialized expert: {self.name} v{self.version}")
    
    @abstractmethod
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        Core analysis method - MUST be implemented by subclasses.
        
        This is the main method that contains the expert's analysis logic.
        Subclasses must override this method.
        
        Args:
            request: ExpertRequest containing user input and context
        
        Returns:
            ExpertResult with analysis results or error information
        
        Important:
            - Must be async (use 'async def')
            - Must always return ExpertResult (never raise exceptions)
            - Should return error field instead of raising
            - Typical execution time should be <2 seconds
            - The framework will enforce a 2-second timeout
        
        Note:
            This method is called by execute() which adds timeout and
            error handling. Subclasses should not override execute().
        """
        pass
    
    async def execute(
        self,
        request: ExpertRequest,
        timeout_sec: float = 2.0
    ) -> ExpertResult:
        """
        Execute the expert with timeout and error handling.
        
        This is the framework's entry point for calling experts.
        It wraps analyze() with:
        - Timeout enforcement (raises TimeoutError if exceeded)
        - Exception handling (returns error result)
        - Performance monitoring
        - Logging
        
        Subclasses should NOT override this method.
        
        Args:
            request: ExpertRequest to analyze
            timeout_sec: Maximum execution time in seconds (default 2.0)
        
        Returns:
            ExpertResult: Always returns ExpertResult (never raises)
        """
        timestamp_start = datetime.now().timestamp()
        self._stats["call_count"] += 1
        
        try:
            # Call analyze with timeout
            self.logger.debug(f"Expert {self.name} starting analysis with {timeout_sec}s timeout")
            
            result = await asyncio.wait_for(
                self.analyze(request),
                timeout=timeout_sec
            )
            
            # Validate result structure
            if not isinstance(result, ExpertResult):
                self.logger.error(f"Expert {self.name} returned invalid type: {type(result)}")
                timestamp_end = datetime.now().timestamp()
                return ExpertResult(
                    expert_name=self.name,
                    result={},
                    confidence=0.0,
                    timestamp_start=timestamp_start,
                    timestamp_end=timestamp_end,
                    error=f"Expert returned invalid type: {type(result)}"
                )
            
            # Ensure timestamps are set
            if result.timestamp_end == 0:
                result.timestamp_end = datetime.now().timestamp()
            
            # Update statistics
            duration_ms = (result.timestamp_end - timestamp_start) * 1000
            self._stats["total_duration_ms"] += duration_ms
            self._stats["min_duration_ms"] = min(
                self._stats["min_duration_ms"],
                duration_ms
            )
            self._stats["max_duration_ms"] = max(
                self._stats["max_duration_ms"],
                duration_ms
            )
            
            self.logger.info(
                f"Expert {self.name} succeeded in {duration_ms:.2f}ms "
                f"with confidence {result.confidence:.2f}"
            )
            
            return result
        
        except asyncio.TimeoutError:
            self._stats["error_count"] += 1
            timestamp_end = datetime.now().timestamp()
            
            error_msg = f"Expert timed out after {timeout_sec}s"
            self.logger.error(error_msg)
            
            return ExpertResult(
                expert_name=self.name,
                result={},
                confidence=0.0,
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
                error=error_msg
            )
        
        except Exception as e:
            self._stats["error_count"] += 1
            timestamp_end = datetime.now().timestamp()
            
            error_msg = f"Expert error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return ExpertResult(
                expert_name=self.name,
                result={},
                confidence=0.0,
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
                error=error_msg
            )
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata describing this expert's capabilities.
        
        Returns a dictionary with information about the expert:
        - name, version
        - description
        - supported_tasks
        - performance stats
        
        Returns:
            Dict with expert metadata
        
        Example:
            >>> metadata = expert.get_metadata()
            >>> print(metadata['name'])
            'StockAnalysisExpert'
            >>> print(metadata['supported_tasks'])
            ['stock_analysis', 'recommendation']
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.__class__.__doc__ or "No description provided",
            "supported_tasks": self.get_supported_tasks(),
            "performance": self.get_performance_stats(),
        }
    
    def get_supported_tasks(self) -> List[str]:
        """
        Get list of task types this expert handles.
        
        Subclasses should override this to return list of task types
        they can handle. This is used by the Expert Router to select
        appropriate experts.
        
        Returns:
            List of task type strings
        
        Examples:
            - ["stock_analysis", "recommendation"]
            - ["knowledge_query"]
            - ["dialog", "conversation"]
        
        Default implementation returns empty list.
        """
        return []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for this expert.
        
        Returns aggregate statistics about execution:
        - call_count: Total number of executions
        - error_count: Number of failed executions
        - error_rate: Percentage of calls that failed
        - avg_duration_ms: Average execution time
        - min_duration_ms: Fastest execution
        - max_duration_ms: Slowest execution
        
        Returns:
            Dict with performance statistics
        
        Example:
            >>> stats = expert.get_performance_stats()
            >>> print(stats['avg_duration_ms'])
            425.5
            >>> print(stats['error_rate'])
            0.05  # 5% error rate
        """
        call_count = self._stats["call_count"]
        
        if call_count == 0:
            avg_duration = 0.0
            error_rate = 0.0
        else:
            avg_duration = self._stats["total_duration_ms"] / call_count
            error_rate = self._stats["error_count"] / call_count
        
        return {
            "call_count": call_count,
            "error_count": self._stats["error_count"],
            "error_rate": round(error_rate, 4),
            "avg_duration_ms": round(avg_duration, 2),
            "min_duration_ms": (
                round(self._stats["min_duration_ms"], 2)
                if self._stats["min_duration_ms"] != float('inf')
                else 0.0
            ),
            "max_duration_ms": round(self._stats["max_duration_ms"], 2),
            "total_duration_ms": round(self._stats["total_duration_ms"], 2),
        }
    
    def reset_stats(self) -> None:
        """
        Reset performance statistics.
        
        Clears all accumulated statistics. Useful for benchmarking
        or starting fresh measurements.
        """
        self._stats = {
            "call_count": 0,
            "error_count": 0,
            "total_duration_ms": 0.0,
            "min_duration_ms": float('inf'),
            "max_duration_ms": 0.0,
        }
        self.logger.debug(f"Statistics reset for expert {self.name}")
    
    def __repr__(self) -> str:
        """String representation of the expert."""
        return f"<{self.__class__.__name__}(name={self.name}, version={self.version})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        stats = self.get_performance_stats()
        return (
            f"{self.name} v{self.version} "
            f"(calls: {stats['call_count']}, "
            f"errors: {stats['error_count']}, "
            f"avg: {stats['avg_duration_ms']}ms)"
        )
