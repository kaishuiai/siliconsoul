"""
MOE Orchestrator - Core Coordination Engine

The MOEOrchestrator is the heart of the Mixture of Experts system.
It coordinates:
1. Expert registration and management
2. Parallel execution of multiple experts
3. Result aggregation
4. Timeout and error handling

Key features:
- Async/await based parallel execution
- Configurable timeouts
- Comprehensive error handling
- Performance monitoring
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from src.experts.expert_base import Expert
from src.models.request_response import (
    ExpertRequest,
    ExpertResult,
    AggregatedResult
)

# Configure module logger
logger = logging.getLogger(__name__)


class MOEOrchestrator:
    """
    Core orchestrator for the Mixture of Experts system.
    
    The MOEOrchestrator manages:
    1. Expert Registration: Register and manage Expert instances
    2. Parallel Execution: Run multiple experts concurrently
    3. Result Aggregation: Combine results from multiple experts
    4. Error Handling: Graceful degradation when experts fail
    
    Execution Flow:
        User Request
            ↓
        Orchestrator.process_request()
            ↓
        Select Experts (by name)
            ↓
        execute_experts_parallel() [async]
            ├─ Expert1.execute() [2s timeout]
            ├─ Expert2.execute() [2s timeout]
            └─ Expert3.execute() [2s timeout]
            ↓
        _aggregate_results()
            ↓
        AggregatedResult
    
    Attributes:
        experts: Dictionary of registered Expert instances
        default_timeout_sec: Default timeout for each expert (seconds)
        logger: Module logger
    
    Examples:
        >>> # Initialize
        >>> moe = MOEOrchestrator(default_timeout_sec=2.0)
        >>> 
        >>> # Register experts
        >>> moe.register_expert(MyExpert())
        >>> moe.register_expert(AnotherExpert())
        >>> 
        >>> # Process request
        >>> request = ExpertRequest(text="...", user_id="...")
        >>> result = await moe.process_request(request)
    """
    
    def __init__(self, default_timeout_sec: float = 2.0):
        """
        Initialize the MOE Orchestrator.
        
        Args:
            default_timeout_sec: Default timeout per expert in seconds
                                (default: 2.0, recommended 1.5-3.0)
        
        Raises:
            ValueError: If default_timeout_sec is <= 0
        """
        if default_timeout_sec <= 0:
            raise ValueError("default_timeout_sec must be > 0")
        
        self.experts: Dict[str, Expert] = {}
        self.default_timeout_sec = default_timeout_sec
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(
            f"MOEOrchestrator initialized with {default_timeout_sec}s default timeout"
        )
    
    def register_expert(self, expert: Expert) -> None:
        """
        Register a new expert with the orchestrator.
        
        Once registered, an expert can be used in processing requests.
        Expert names must be unique.
        
        Args:
            expert: Expert instance to register
        
        Raises:
            TypeError: If expert is not an Expert instance
            ValueError: If expert with same name already registered
        
        Examples:
            >>> expert = MyExpert()
            >>> moe.register_expert(expert)
            >>> 
            >>> # Later, can access via:
            >>> retrieved = moe.get_expert("MyExpert")
        """
        # Validate input
        if not isinstance(expert, Expert):
            raise TypeError(f"Expert must be an Expert instance, got {type(expert)}")
        
        if expert.name in self.experts:
            raise ValueError(
                f"Expert '{expert.name}' already registered. "
                f"Current experts: {list(self.experts.keys())}"
            )
        
        # Register
        self.experts[expert.name] = expert
        self.logger.info(
            f"Registered expert: {expert.name} v{expert.version} "
            f"(total: {len(self.experts)})"
        )
    
    def unregister_expert(self, name: str) -> bool:
        """
        Unregister an expert by name.
        
        Args:
            name: Name of expert to unregister
        
        Returns:
            bool: True if expert was found and removed, False otherwise
        """
        if name in self.experts:
            del self.experts[name]
            self.logger.info(f"Unregistered expert: {name}")
            return True
        return False
    
    def get_expert(self, name: str) -> Optional[Expert]:
        """
        Retrieve a registered expert by name.
        
        Args:
            name: Expert name
        
        Returns:
            Expert instance or None if not found
        
        Examples:
            >>> expert = moe.get_expert("StockAnalysisExpert")
            >>> if expert:
            ...     print(expert.get_metadata())
        """
        return self.experts.get(name)
    
    def get_available_experts(self) -> List[str]:
        """
        Get list of all registered expert names.
        
        Returns:
            List of expert names in order of registration
        
        Examples:
            >>> names = moe.get_available_experts()
            >>> print(names)
            ['Expert1', 'Expert2', 'Expert3']
        """
        return list(self.experts.keys())
    
    def get_expert_count(self) -> int:
        """Get number of registered experts."""
        return len(self.experts)
    
    async def execute_experts_parallel(
        self,
        expert_names: List[str],
        request: ExpertRequest,
        timeout_sec: Optional[float] = None
    ) -> List[ExpertResult]:
        """
        Execute multiple experts in parallel.
        
        This is the core execution method. It runs the specified experts
        concurrently, each with their own timeout. If one expert fails,
        others continue unaffected.
        
        Execution model:
            Time 0ms:   Start ────────┐
                                      ├─ Expert1 (0-500ms)
            Time 600ms:               ├─ Expert2 (0-600ms)
                                      ├─ Expert3 (0-400ms)
                        Complete ────┘
                        Total: 600ms (vs 1500ms sequential)
        
        Args:
            expert_names: Names of experts to execute
            request: ExpertRequest object
            timeout_sec: Overall timeout for all experts combined (optional)
                        If not specified, uses default_timeout_sec * num_experts
        
        Returns:
            List[ExpertResult]: Results from all experts
                               (includes error results for failed experts)
        
        Notes:
            - Each expert gets default_timeout_sec for execution
            - If timeout_sec is specified, it's the total for all
            - Missing experts are logged and skipped
            - Never raises exceptions (returns error results instead)
        
        Examples:
            >>> results = await moe.execute_experts_parallel(
            ...     ["Expert1", "Expert2"],
            ...     request,
            ...     timeout_sec=5.0  # Overall timeout
            ... )
            >>> print(f"Got {len(results)} results")
            >>> for result in results:
            ...     if result.error:
            ...         print(f"❌ {result.expert_name}: {result.error}")
            ...     else:
            ...         print(f"✅ {result.expert_name}: {result.result}")
        """
        # Validate inputs
        if not expert_names:
            self.logger.warning("execute_experts_parallel called with empty list")
            return []
        
        # Calculate overall timeout
        if timeout_sec is None:
            timeout_sec = self.default_timeout_sec * len(expert_names)
        
        # Log execution start
        self.logger.debug(
            f"Starting parallel execution of {len(expert_names)} experts "
            f"with {timeout_sec}s overall timeout"
        )
        
        # Create execution tasks
        tasks = []
        expert_mapping = {}
        
        for i, name in enumerate(expert_names):
            expert = self.get_expert(name)
            
            if not expert:
                self.logger.warning(
                    f"Expert '{name}' not found. "
                    f"Available: {self.get_available_experts()}"
                )
                continue
            
            # Create task for this expert
            task = expert.execute(request, timeout_sec=self.default_timeout_sec)
            tasks.append(task)
            expert_mapping[i] = name
        
        if not tasks:
            self.logger.error("No valid experts to execute")
            return []
        
        # Execute all tasks in parallel with timeout
        try:
            # Run all tasks concurrently
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout_sec
            )
            
            # Filter and validate results
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, ExpertResult):
                    valid_results.append(result)
                elif isinstance(result, Exception):
                    # Task raised exception
                    expert_name = expert_mapping.get(i, "Unknown")
                    self.logger.error(f"Task {i} ({expert_name}) raised exception")
                else:
                    # Unexpected result type
                    self.logger.warning(f"Task {i} returned invalid type: {type(result)}")
            
            self.logger.info(
                f"Parallel execution completed: {len(valid_results)}/{len(tasks)} "
                f"experts succeeded"
            )
            
            return valid_results
        
        except asyncio.TimeoutError:
            self.logger.error(
                f"Parallel execution timed out after {timeout_sec}s "
                f"(only {len(tasks)} experts started)"
            )
            return []
        
        except Exception as e:
            self.logger.error(
                f"Parallel execution failed: {str(e)}",
                exc_info=True
            )
            return []
    
    async def process_request(
        self,
        request: ExpertRequest,
        expert_names: Optional[List[str]] = None,
        timeout_sec: Optional[float] = None
    ) -> AggregatedResult:
        """
        Process a user request through the full MOE pipeline.
        
        This is the main public API. It handles:
        1. Expert selection (by name or all registered)
        2. Parallel expert execution
        3. Result aggregation
        4. Error handling
        
        Execution Flow:
            User Request
                ↓
            Select Experts (expert_names or all)
                ↓
            execute_experts_parallel()
                ↓
            _aggregate_results()
                ↓
            AggregatedResult
        
        Args:
            request: ExpertRequest with user input
            expert_names: Specific experts to use (None = use all registered)
            timeout_sec: Overall timeout for execution
        
        Returns:
            AggregatedResult: Final aggregated result
        
        Notes:
            - Always returns AggregatedResult (never raises)
            - If no experts registered, returns error result
            - If all experts fail, returns error in final_result
            - Includes timing information
        
        Examples:
            >>> request = ExpertRequest(
            ...     text="What should I do with AAPL stock?",
            ...     user_id="user123",
            ...     task_type="stock_analysis"
            ... )
            >>> result = await moe.process_request(request)
            >>> print(f"Confidence: {result.overall_confidence}")
            >>> print(f"Consensus: {result.consensus_level}")
            >>> for expert_result in result.expert_results:
            ...     print(f"{expert_result.expert_name}: {expert_result.result}")
        """
        timestamp_start = datetime.now().timestamp()
        
        # Select experts to use
        if expert_names is None:
            expert_names = self.get_available_experts()
        
        if not expert_names:
            self.logger.error("No experts available for processing")
            
            timestamp_end = datetime.now().timestamp()
            return AggregatedResult(
                final_result={"error": "No experts registered"},
                expert_results=[],
                overall_confidence=0.0,
                num_experts=0,
                consensus_level="none",
                duration_ms=(timestamp_end - timestamp_start) * 1000
            )
        
        # Log request start
        self.logger.info(
            f"Processing request from {request.user_id} "
            f"using {len(expert_names)} experts: {expert_names}"
        )
        
        # Execute experts in parallel
        results = await self.execute_experts_parallel(
            expert_names,
            request,
            timeout_sec
        )
        
        # Aggregate results
        aggregated = self._aggregate_results(results)
        
        # Add timing information
        timestamp_end = datetime.now().timestamp()
        aggregated.duration_ms = (timestamp_end - timestamp_start) * 1000
        
        # Log completion
        self.logger.info(
            f"Request processing completed in {aggregated.duration_ms:.2f}ms "
            f"with {aggregated.overall_confidence:.2f} overall confidence"
        )
        
        return aggregated
    
    def _aggregate_results(
        self,
        results: List[ExpertResult]
    ) -> AggregatedResult:
        """
        Aggregate multiple expert results into final decision.
        
        Aggregation Strategy (Phase 1 - Simple):
        1. Filter out failed results (has error)
        2. Calculate average confidence
        3. Evaluate consensus level based on confidence variance
        4. Build final_result with metadata
        
        Aggregation Strategy (Phase 2+ - Advanced):
        - Weighted confidence based on expert reliability
        - Majority voting for categorical decisions
        - Conflict resolution when experts disagree
        - Expert credibility tracking
        
        Args:
            results: List of ExpertResult objects
        
        Returns:
            AggregatedResult: Aggregated result
        
        Notes:
            - Handles empty results list gracefully
            - Handles all failures gracefully
            - Calculates consensus level automatically
        """
        # Filter successful results (no error)
        successful_results = [r for r in results if not r.error]
        failed_results = [r for r in results if r.error]
        
        if not successful_results:
            # All experts failed or no results
            self.logger.warning(
                f"All {len(results)} experts failed. "
                f"Returning error aggregation."
            )
            
            return AggregatedResult(
                final_result={
                    "error": "All experts failed",
                    "num_failed": len(results),
                    "failures": [
                        {
                            "expert": r.expert_name,
                            "error": r.error
                        }
                        for r in failed_results
                    ]
                },
                expert_results=results,
                overall_confidence=0.0,
                num_experts=len(results),
                consensus_level="none",
                duration_ms=0.0
            )
        
        # Calculate average confidence
        avg_confidence = (
            sum(r.confidence for r in successful_results) /
            len(successful_results)
        )
        
        # Calculate confidence standard deviation (for consensus)
        if len(successful_results) > 1:
            variance = sum(
                (r.confidence - avg_confidence) ** 2
                for r in successful_results
            ) / len(successful_results)
            stddev = variance ** 0.5
        else:
            stddev = 0.0
        
        # Evaluate consensus level
        if stddev < 0.1:
            consensus = "high"
        elif stddev < 0.2:
            consensus = "medium"
        else:
            consensus = "low"
        
        # Build final result
        final_result = {
            "num_successful": len(successful_results),
            "num_failed": len(failed_results),
            "consensus": consensus,
            "avg_confidence": round(avg_confidence, 4),
            "confidence_stddev": round(stddev, 4),
            "experts": [r.expert_name for r in successful_results],
        }
        
        # Create aggregated result
        aggregated = AggregatedResult(
            final_result=final_result,
            expert_results=results,
            overall_confidence=avg_confidence,
            num_experts=len(results),
            consensus_level=consensus,
            duration_ms=0.0  # Will be set by process_request
        )
        
        return aggregated
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get overall system statistics.
        
        Returns:
            Dict with:
            - num_experts: Total registered experts
            - experts: List of expert names and stats
            - performance: System-wide performance metrics
        """
        return {
            "num_experts": self.get_expert_count(),
            "expert_names": self.get_available_experts(),
            "experts": [
                {
                    "name": expert.name,
                    "version": expert.version,
                    "stats": expert.get_performance_stats()
                }
                for expert in self.experts.values()
            ],
            "default_timeout_sec": self.default_timeout_sec,
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<MOEOrchestrator({self.get_expert_count()} experts)>"
    
    def __str__(self) -> str:
        """Human-readable string."""
        expert_names = self.get_available_experts()
        return (
            f"MOEOrchestrator with {len(expert_names)} experts: "
            f"{', '.join(expert_names)}"
        )
