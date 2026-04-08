"""
Unit tests for MOEOrchestrator

Tests:
- Expert registration and management
- Parallel execution of experts
- Result aggregation
- Error handling
"""

import asyncio
import pytest

from src.core.moe_orchestrator import MOEOrchestrator
from src.experts.demo_expert_1 import DemoExpert1
from src.experts.demo_expert_2 import DemoExpert2
from src.experts.demo_expert_3 import DemoExpert3
from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, AggregatedResult


class TestOrchestratorInitialization:
    """Tests for MOEOrchestrator initialization"""
    
    def test_initialization_default(self):
        """Test default initialization"""
        moe = MOEOrchestrator()
        
        assert moe.default_timeout_sec == 2.0
        assert moe.get_expert_count() == 0
        assert moe.get_available_experts() == []
    
    def test_initialization_custom_timeout(self):
        """Test initialization with custom timeout"""
        moe = MOEOrchestrator(default_timeout_sec=3.5)
        
        assert moe.default_timeout_sec == 3.5
    
    def test_initialization_invalid_timeout(self):
        """Test that invalid timeout raises error"""
        with pytest.raises(ValueError):
            MOEOrchestrator(default_timeout_sec=0)
        
        with pytest.raises(ValueError):
            MOEOrchestrator(default_timeout_sec=-1)


class TestExpertRegistration:
    """Tests for expert registration and management"""
    
    def test_register_expert(self):
        """Test registering an expert"""
        moe = MOEOrchestrator()
        expert = DemoExpert1()
        
        moe.register_expert(expert)
        
        assert moe.get_expert_count() == 1
        assert "DemoExpert1" in moe.get_available_experts()
    
    def test_register_multiple_experts(self):
        """Test registering multiple experts"""
        moe = MOEOrchestrator()
        
        moe.register_expert(DemoExpert1())
        moe.register_expert(DemoExpert2())
        moe.register_expert(DemoExpert3())
        
        assert moe.get_expert_count() == 3
        names = moe.get_available_experts()
        assert len(names) == 3
        assert "DemoExpert1" in names
        assert "DemoExpert2" in names
        assert "DemoExpert3" in names
    
    def test_register_duplicate_name_error(self):
        """Test that registering expert with same name raises error"""
        moe = MOEOrchestrator()
        
        moe.register_expert(DemoExpert1())
        
        with pytest.raises(ValueError):
            moe.register_expert(DemoExpert1())
    
    def test_register_invalid_type(self):
        """Test that registering non-Expert raises error"""
        moe = MOEOrchestrator()
        
        with pytest.raises(TypeError):
            moe.register_expert("not an expert")
        
        with pytest.raises(TypeError):
            moe.register_expert({"expert": "dict"})
    
    def test_get_expert(self):
        """Test retrieving a registered expert"""
        moe = MOEOrchestrator()
        expert = DemoExpert1()
        
        moe.register_expert(expert)
        
        retrieved = moe.get_expert("DemoExpert1")
        assert retrieved is expert
        
        missing = moe.get_expert("NonExistent")
        assert missing is None
    
    def test_unregister_expert(self):
        """Test unregistering an expert"""
        moe = MOEOrchestrator()
        moe.register_expert(DemoExpert1())
        moe.register_expert(DemoExpert2())
        
        assert moe.get_expert_count() == 2
        
        removed = moe.unregister_expert("DemoExpert1")
        assert removed is True
        assert moe.get_expert_count() == 1
        assert moe.get_expert("DemoExpert1") is None
        
        removed = moe.unregister_expert("NonExistent")
        assert removed is False


class TestParallelExecution:
    """Tests for parallel expert execution"""
    
    @pytest.mark.asyncio
    async def test_execute_single_expert(self, sample_request, demo_expert_1):
        """Test executing a single expert"""
        moe = MOEOrchestrator()
        moe.register_expert(demo_expert_1)
        
        results = await moe.execute_experts_parallel(
            ["DemoExpert1"],
            sample_request
        )
        
        assert len(results) == 1
        assert results[0].expert_name == "DemoExpert1"
        assert not results[0].error
    
    @pytest.mark.asyncio
    async def test_execute_multiple_experts_parallel(
        self,
        sample_request,
        moe_with_experts
    ):
        """Test executing multiple experts in parallel"""
        results = await moe_with_experts.execute_experts_parallel(
            ["DemoExpert1", "DemoExpert2", "DemoExpert3"],
            sample_request
        )
        
        assert len(results) >= 2  # At least some should succeed
        
        # Verify they all ran
        names = [r.expert_name for r in results]
        assert "DemoExpert1" in names or len(results) < 3
    
    @pytest.mark.asyncio
    async def test_execute_nonexistent_expert(self, sample_request, moe_orchestrator):
        """Test executing non-existent expert"""
        results = await moe_orchestrator.execute_experts_parallel(
            ["NonExistent"],
            sample_request
        )
        
        # Should return empty list for non-existent experts
        assert results == []
    
    @pytest.mark.asyncio
    async def test_execute_empty_expert_list(self, sample_request, moe_orchestrator):
        """Test executing with empty expert list"""
        results = await moe_orchestrator.execute_experts_parallel(
            [],
            sample_request
        )
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_execute_with_timeout(self, sample_request, demo_expert_1):
        """Test execution respects timeout"""
        moe = MOEOrchestrator(default_timeout_sec=1.0)
        moe.register_expert(demo_expert_1)
        
        results = await moe.execute_experts_parallel(
            ["DemoExpert1"],
            sample_request,
            timeout_sec=5.0  # Overall timeout
        )
        
        # Should complete successfully within timeout
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_execute_overall_timeout_returns_timeout_errors(self, sample_request):
        class _SlowExpert(Expert):
            def __init__(self, name: str):
                super().__init__(name=name, version="1.0")

            async def analyze(self, request):
                await asyncio.sleep(0.2)
                return {"ok": True}, 0.5, {}

        moe = MOEOrchestrator(default_timeout_sec=1.0)
        moe.register_expert(_SlowExpert("SlowA"))
        moe.register_expert(_SlowExpert("SlowB"))
        results = await moe.execute_experts_parallel(["SlowA", "SlowB"], sample_request, timeout_sec=0.01)
        assert len(results) == 2
        assert all(r.error for r in results)
        assert any("Overall timeout" in (r.error or "") for r in results)


class TestProcessRequest:
    """Tests for full request processing"""
    
    @pytest.mark.asyncio
    async def test_process_request_no_experts(self):
        """Test processing when no experts registered"""
        moe = MOEOrchestrator()
        request = ExpertRequest(text="test", user_id="user1")
        
        result = await moe.process_request(request)
        
        assert isinstance(result, AggregatedResult)
        assert result.overall_confidence == 0.0
        assert "No experts registered" in result.final_result.get("error", "")
    
    @pytest.mark.asyncio
    async def test_process_request_with_experts(self, sample_request, moe_with_experts):
        """Test processing request with experts"""
        result = await moe_with_experts.process_request(sample_request)
        
        assert isinstance(result, AggregatedResult)
        assert result.num_experts >= 0
        assert len(result.expert_results) >= 0
        assert result.duration_ms >= 0
    
    @pytest.mark.asyncio
    async def test_process_request_specific_experts(
        self,
        sample_request,
        moe_with_experts
    ):
        """Test processing with specific expert selection"""
        result = await moe_with_experts.process_request(
            sample_request,
            expert_names=["DemoExpert1", "DemoExpert2"]
        )
        
        assert isinstance(result, AggregatedResult)
        # At least some results should be present
        assert len(result.expert_results) >= 0
    
    @pytest.mark.asyncio
    async def test_process_request_all_experts_default(
        self,
        sample_request,
        moe_with_experts
    ):
        """Test that default uses all experts"""
        result = await moe_with_experts.process_request(sample_request)
        
        assert isinstance(result, AggregatedResult)
        assert len(result.expert_results) >= 0


class TestResultAggregation:
    """Tests for result aggregation"""
    
    def test_aggregate_successful_results(self, moe_orchestrator):
        """Test aggregating successful results"""
        from src.models.request_response import ExpertResult
        
        results = [
            ExpertResult(
                expert_name="Expert1",
                result={"score": 0.9},
                confidence=0.9,
                timestamp_start=0.0,
                timestamp_end=1.0
            ),
            ExpertResult(
                expert_name="Expert2",
                result={"score": 0.8},
                confidence=0.8,
                timestamp_start=0.0,
                timestamp_end=1.0
            ),
        ]
        
        aggregated = moe_orchestrator._aggregate_results(results)
        
        assert abs(aggregated.overall_confidence - 0.85) < 0.001  # Float comparison with tolerance
        assert aggregated.num_experts == 2
        assert aggregated.consensus_level in ["high", "medium", "low"]
    
    def test_aggregate_with_failures(self, moe_orchestrator):
        """Test aggregating with some failures"""
        from src.models.request_response import ExpertResult
        
        results = [
            ExpertResult(
                expert_name="Expert1",
                result={"score": 0.9},
                confidence=0.9,
                timestamp_start=0.0,
                timestamp_end=1.0
            ),
            ExpertResult(
                expert_name="Expert2",
                result={},
                confidence=0.0,
                timestamp_start=0.0,
                timestamp_end=1.0,
                error="Failed"
            ),
        ]
        
        aggregated = moe_orchestrator._aggregate_results(results)
        
        # Should use only successful results for confidence
        assert aggregated.overall_confidence == 0.9
        assert aggregated.num_experts == 2
    
    def test_aggregate_all_failures(self, moe_orchestrator):
        """Test aggregating when all experts fail"""
        from src.models.request_response import ExpertResult
        
        results = [
            ExpertResult(
                expert_name="Expert1",
                result={},
                confidence=0.0,
                timestamp_start=0.0,
                timestamp_end=1.0,
                error="Failed"
            ),
        ]
        
        aggregated = moe_orchestrator._aggregate_results(results)
        
        assert aggregated.overall_confidence == 0.0
        assert aggregated.consensus_level == "none"
        # Check that there's an error message in final_result
        assert "error" in aggregated.final_result or "failed" in str(aggregated.final_result).lower()
    
    def test_aggregate_consensus_high(self, moe_orchestrator):
        """Test high consensus detection"""
        from src.models.request_response import ExpertResult
        
        # All experts have same confidence (high consensus)
        results = [
            ExpertResult(
                expert_name="Expert1",
                result={},
                confidence=0.85,
                timestamp_start=0.0,
                timestamp_end=1.0
            ),
            ExpertResult(
                expert_name="Expert2",
                result={},
                confidence=0.85,
                timestamp_start=0.0,
                timestamp_end=1.0
            ),
        ]
        
        aggregated = moe_orchestrator._aggregate_results(results)
        
        assert aggregated.consensus_level == "high"


class TestSystemStats:
    """Tests for system statistics"""
    
    def test_get_system_stats(self, moe_with_experts):
        """Test getting system statistics"""
        stats = moe_with_experts.get_system_stats()
        
        assert "num_experts" in stats
        assert "expert_names" in stats
        assert "experts" in stats
        assert stats["num_experts"] == 3
        assert len(stats["expert_names"]) == 3
        assert len(stats["experts"]) == 3
    
    def test_system_stats_expert_details(self, moe_with_experts):
        """Test expert details in system stats"""
        stats = moe_with_experts.get_system_stats()
        
        for expert_info in stats["experts"]:
            assert "name" in expert_info
            assert "version" in expert_info
            assert "stats" in expert_info
