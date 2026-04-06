"""
Demo Expert 1 - Basic Analysis

A simple demo expert that always returns the same result.
Used for testing the basic framework functionality.

Characteristics:
- Quick execution (100ms)
- High confidence (0.85)
- Fixed result format
"""

import asyncio
from datetime import datetime
from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult


class DemoExpert1(Expert):
    """
    Demo Expert 1: Simple Fixed-Result Expert
    
    This expert demonstrates the simplest possible expert implementation.
    It:
    - Processes any input
    - Performs minimal computation
    - Returns a fixed result with high confidence
    - Completes in ~100ms
    
    Purpose: Framework testing and demonstration
    
    Supported Tasks:
    - demo: General demonstration
    - test: Testing framework functionality
    - simple_analysis: Quick analysis with fixed result
    """
    
    def __init__(self):
        """Initialize Demo Expert 1."""
        super().__init__(name="DemoExpert1", version="1.0")
        self.call_count = 0
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        Analyze user request and return a fixed demo result.
        
        This is a minimal implementation that:
        1. Extracts basic info from request
        2. Simulates some async work (asyncio.sleep)
        3. Returns a fixed result
        
        Args:
            request: ExpertRequest with user input
        
        Returns:
            ExpertResult with demo analysis
        """
        timestamp_start = datetime.now().timestamp()
        self.call_count += 1
        
        try:
            # Extract info from request
            text_length = len(request.text)
            user_id = request.user_id
            
            # Simulate some async work (100ms)
            await asyncio.sleep(0.1)
            
            # Build analysis result
            analysis = {
                "input_length": text_length,
                "user_id": user_id,
                "message": f"Demo analysis of: {request.text[:50]}...",
                "score": 0.85,
                "type": "DEMO_RESULT",
                "call_number": self.call_count,
            }
            
            timestamp_end = datetime.now().timestamp()
            
            return ExpertResult(
                expert_name=self.name,
                result=analysis,
                confidence=0.85,
                metadata={
                    "version": self.version,
                    "model": "demo_v1",
                    "type": "fixed_result",
                },
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
            )
        
        except Exception as e:
            timestamp_end = datetime.now().timestamp()
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            
            return ExpertResult(
                expert_name=self.name,
                result={},
                confidence=0.0,
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
                error=f"Analysis error: {str(e)}",
            )
    
    def get_supported_tasks(self) -> list:
        """
        Return list of task types this expert handles.
        
        Returns:
            List of supported task types
        """
        return ["demo", "test", "simple_analysis"]
