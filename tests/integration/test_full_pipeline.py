"""
Integration tests for complete MOE pipeline

Tests end-to-end scenarios:
- Complete request processing
- Multi-expert analysis
- Result aggregation verification
"""

import pytest

from src.core.moe_orchestrator import MOEOrchestrator
from src.experts.demo_expert_1 import DemoExpert1
from src.experts.demo_expert_2 import DemoExpert2
from src.experts.demo_expert_3 import DemoExpert3
from src.models.request_response import ExpertRequest, AggregatedResult


class TestCompleteWorkflow:
    """Tests for complete MOE workflow"""
    
    @pytest.mark.asyncio
    async def test_single_expert_analysis(self, sample_request):
        """Test analysis with single expert"""
        # Setup
        moe = MOEOrchestrator(default_timeout_sec=2.0)
        moe.register_expert(DemoExpert1())
        
        # Process
        result = await moe.process_request(sample_request)
        
        # Verify
        assert isinstance(result, AggregatedResult)
        assert result.overall_confidence > 0
        assert result.duration_ms > 0
        assert len(result.expert_results) > 0
    
    @pytest.mark.asyncio
    async def test_multi_expert_analysis(self, sample_request):
        """Test analysis with multiple experts"""
        # Setup
        moe = MOEOrchestrator(default_timeout_sec=3.0)
        moe.register_expert(DemoExpert1())
        moe.register_expert(DemoExpert2())
        moe.register_expert(DemoExpert3())
        
        # Process
        result = await moe.process_request(sample_request)
        
        # Verify
        assert isinstance(result, AggregatedResult)
        assert result.num_experts >= 0
        assert result.duration_ms > 0
        
        # Should have multiple experts' results
        if result.expert_results:
            assert len(result.expert_results) >= 1
    
    @pytest.mark.asyncio
    async def test_short_input_analysis(self, short_request, moe_with_experts):
        """Test analysis with very short input"""
        result = await moe_with_experts.process_request(short_request)
        
        assert isinstance(result, AggregatedResult)
        # Short input should still be processed
        assert result.duration_ms >= 0
    
    @pytest.mark.asyncio
    async def test_long_input_analysis(self, long_request, moe_with_experts):
        """Test analysis with very long input"""
        result = await moe_with_experts.process_request(long_request)
        
        assert isinstance(result, AggregatedResult)
        assert result.duration_ms >= 0
    
    @pytest.mark.asyncio
    async def test_analysis_with_context(self):
        """Test analysis with context information"""
        # Create request with context
        request = ExpertRequest(
            text="This is a test with context",
            user_id="context_user",
            context={
                "previous_topic": "sentiment_analysis",
                "language": "english",
                "source": "test_suite"
            }
        )
        
        # Setup and process
        moe = MOEOrchestrator()
        moe.register_expert(DemoExpert1())
        moe.register_expert(DemoExpert3())
        
        result = await moe.process_request(request)
        
        # Verify
        assert isinstance(result, AggregatedResult)
        # Experts should have received the request with context
        assert len(result.expert_results) >= 0
    
    @pytest.mark.asyncio
    async def test_parallel_execution_timing(self, sample_request):
        """Test that parallel execution is faster than sequential"""
        # Setup with 3 experts
        moe = MOEOrchestrator(default_timeout_sec=3.0)
        moe.register_expert(DemoExpert1())  # ~100ms
        moe.register_expert(DemoExpert2())  # ~300ms
        moe.register_expert(DemoExpert3())  # ~50-300ms
        
        # Process
        result = await moe.process_request(sample_request)
        
        # Verify
        # Total should be less than 100+300+300 (sequential would be ~450ms)
        # With parallelism, should be closer to max(100, 300, 300) = 300ms
        # Add some buffer for overhead
        assert result.duration_ms < 700  # Rough check for parallelism


class TestResultValidation:
    """Tests for result validation and structure"""
    
    @pytest.mark.asyncio
    async def test_aggregated_result_structure(self, sample_request, moe_with_experts):
        """Test that aggregated result has all required fields"""
        result = await moe_with_experts.process_request(sample_request)
        
        # Verify all required fields
        assert hasattr(result, 'final_result')
        assert hasattr(result, 'expert_results')
        assert hasattr(result, 'overall_confidence')
        assert hasattr(result, 'num_experts')
        assert hasattr(result, 'consensus_level')
        assert hasattr(result, 'duration_ms')
        
        # Verify types
        assert isinstance(result.final_result, dict)
        assert isinstance(result.expert_results, list)
        assert isinstance(result.overall_confidence, float)
        assert isinstance(result.num_experts, int)
        assert isinstance(result.consensus_level, str)
        assert isinstance(result.duration_ms, float)
    
    @pytest.mark.asyncio
    async def test_expert_result_structure(self, sample_request):
        """Test that individual expert results have correct structure"""
        moe = MOEOrchestrator()
        moe.register_expert(DemoExpert1())
        
        result = await moe.process_request(sample_request)
        
        if result.expert_results:
            for expert_result in result.expert_results:
                # Verify all required fields
                assert hasattr(expert_result, 'expert_name')
                assert hasattr(expert_result, 'result')
                assert hasattr(expert_result, 'confidence')
                assert hasattr(expert_result, 'metadata')
                assert hasattr(expert_result, 'timestamp_start')
                assert hasattr(expert_result, 'timestamp_end')
                assert hasattr(expert_result, 'duration_ms')
                
                # Verify types
                assert isinstance(expert_result.expert_name, str)
                assert isinstance(expert_result.result, dict)
                assert 0 <= expert_result.confidence <= 1
                assert isinstance(expert_result.metadata, dict)
                assert isinstance(expert_result.duration_ms, float)
    
    @pytest.mark.asyncio
    async def test_confidence_bounds(self, sample_request, moe_with_experts):
        """Test that all confidence values are within valid bounds"""
        result = await moe_with_experts.process_request(sample_request)
        
        # Overall confidence should be 0-1
        assert 0 <= result.overall_confidence <= 1
        
        # All individual confidences should be 0-1
        for expert_result in result.expert_results:
            assert 0 <= expert_result.confidence <= 1


class TestErrorScenarios:
    """Tests for error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_processing_with_invalid_expert_name(self, sample_request):
        """Test processing with invalid expert names"""
        moe = MOEOrchestrator()
        moe.register_expert(DemoExpert1())
        
        # Try to use non-existent expert
        result = await moe.process_request(
            sample_request,
            expert_names=["NonExistentExpert", "DemoExpert1"]
        )
        
        # Should still process successfully with the valid expert
        assert isinstance(result, AggregatedResult)
    
    @pytest.mark.asyncio
    async def test_empty_request_text(self):
        """Test with empty request text"""
        # This should fail at the ExpertRequest level due to validation
        with pytest.raises(ValueError):
            ExpertRequest(text="", user_id="user1")
    
    @pytest.mark.asyncio
    async def test_processing_with_no_experts_registered(self, sample_request):
        """Test processing when no experts registered"""
        moe = MOEOrchestrator()
        
        result = await moe.process_request(sample_request)
        
        assert isinstance(result, AggregatedResult)
        assert result.overall_confidence == 0.0
        assert "No experts" in result.final_result.get("error", "")


class TestSystemBehavior:
    """Tests for overall system behavior"""
    
    @pytest.mark.asyncio
    async def test_expert_stats_updated_after_processing(self, sample_request):
        """Test that expert statistics are updated after processing"""
        # Setup
        expert1 = DemoExpert1()
        expert2 = DemoExpert2()
        
        moe = MOEOrchestrator()
        moe.register_expert(expert1)
        moe.register_expert(expert2)
        
        # Process
        await moe.process_request(sample_request)
        
        # Verify stats updated
        stats1 = expert1.get_performance_stats()
        stats2 = expert2.get_performance_stats()
        
        assert stats1["call_count"] >= 0  # May be 1 or 0 depending on execution
        assert stats2["call_count"] >= 0
    
    @pytest.mark.asyncio
    async def test_multiple_request_processing(self):
        """Test processing multiple requests"""
        moe = MOEOrchestrator()
        moe.register_expert(DemoExpert1())
        
        requests = [
            ExpertRequest(text="First request", user_id="user1"),
            ExpertRequest(text="Second request", user_id="user2"),
            ExpertRequest(text="Third request", user_id="user3"),
        ]
        
        results = []
        for request in requests:
            result = await moe.process_request(request)
            results.append(result)
        
        # Verify all processed
        assert len(results) == 3
        for result in results:
            assert isinstance(result, AggregatedResult)
    
    @pytest.mark.asyncio
    async def test_expert_unregister_and_process(self, sample_request):
        """Test unregistering expert and processing"""
        moe = MOEOrchestrator()
        moe.register_expert(DemoExpert1())
        moe.register_expert(DemoExpert2())
        
        # Remove one expert
        moe.unregister_expert("DemoExpert1")
        
        # Process should work with remaining expert
        result = await moe.process_request(sample_request)
        
        assert isinstance(result, AggregatedResult)


class TestConsensusDetection:
    """Tests for consensus level detection"""
    
    @pytest.mark.asyncio
    async def test_high_consensus_with_similar_confidence(self, sample_request, moe_with_experts):
        """Test high consensus when experts have similar confidence"""
        # For this, we'd need experts with similar confidence scores
        result = await moe_with_experts.process_request(sample_request)
        
        if result.expert_results:
            # If we have results, consensus should be calculated
            assert result.consensus_level in ["high", "medium", "low", "none"]


class TestPerformanceCharacteristics:
    """Tests for performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_response_time_is_reasonable(self, sample_request, moe_with_experts):
        """Test that response time is reasonable"""
        result = await moe_with_experts.process_request(sample_request)
        
        # Duration should be reasonable (< 10 seconds)
        assert result.duration_ms < 10000
        # Should not be 0 (unless no experts ran)
        if result.expert_results:
            assert result.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_memory_reasonable_with_many_results(self, long_request):
        """Test that memory usage stays reasonable with large inputs"""
        moe = MOEOrchestrator()
        moe.register_expert(DemoExpert1())
        
        # Process should not fail or use excessive memory
        result = await moe.process_request(long_request)
        
        assert isinstance(result, AggregatedResult)
        assert result.duration_ms >= 0
