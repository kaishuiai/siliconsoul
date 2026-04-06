"""
Unit tests for Expert base class

Tests:
- Expert initialization
- analyze() abstract method
- execute() with timeout and error handling
- Performance statistics
- Metadata management
"""

import pytest
import asyncio
from datetime import datetime

from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult


class SimpleTestExpert(Expert):
    """Simple test expert implementation"""
    
    def __init__(self, name="SimpleExpert", version="1.0"):
        super().__init__(name=name, version=version)
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """Simple analysis that returns success"""
        await asyncio.sleep(0.05)  # 50ms
        
        return ExpertResult(
            expert_name=self.name,
            result={"simple": True},
            confidence=0.8,
            metadata={"version": self.version},
            timestamp_start=datetime.now().timestamp(),
            timestamp_end=datetime.now().timestamp(),
        )
    
    def get_supported_tasks(self) -> list:
        return ["test", "simple"]


class SlowTestExpert(Expert):
    """Expert that takes longer"""
    
    def __init__(self):
        super().__init__(name="SlowExpert", version="1.0")
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """Analysis that takes 500ms"""
        await asyncio.sleep(0.5)
        
        return ExpertResult(
            expert_name=self.name,
            result={"slow": True},
            confidence=0.7,
            metadata={},
            timestamp_start=datetime.now().timestamp(),
            timestamp_end=datetime.now().timestamp(),
        )


class TimeoutTestExpert(Expert):
    """Expert that will timeout"""
    
    def __init__(self):
        super().__init__(name="TimeoutExpert", version="1.0")
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """Analysis that takes too long"""
        await asyncio.sleep(10)  # 10 seconds - will timeout
        
        return ExpertResult(
            expert_name=self.name,
            result={},
            confidence=0.0,
            metadata={},
            timestamp_start=datetime.now().timestamp(),
            timestamp_end=datetime.now().timestamp(),
        )


class ErrorTestExpert(Expert):
    """Expert that raises an exception"""
    
    def __init__(self):
        super().__init__(name="ErrorExpert", version="1.0")
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """Analysis that raises exception"""
        raise RuntimeError("Intentional error for testing")


class TestExpertInitialization:
    """Tests for Expert initialization"""
    
    def test_initialization_valid(self):
        """Test valid expert initialization"""
        expert = SimpleTestExpert()
        
        assert expert.name == "SimpleExpert"
        assert expert.version == "1.0"
        assert expert._stats["call_count"] == 0
        assert expert._stats["error_count"] == 0
    
    def test_initialization_custom_name_and_version(self):
        """Test initialization with custom name and version"""
        expert = SimpleTestExpert(name="CustomExpert", version="2.5")
        
        assert expert.name == "CustomExpert"
        assert expert.version == "2.5"
    
    def test_initialization_invalid_name(self):
        """Test that invalid name raises error"""
        with pytest.raises(ValueError):
            SimpleTestExpert(name="")
    
    def test_repr_and_str(self):
        """Test __repr__ and __str__ methods"""
        expert = SimpleTestExpert()
        
        repr_str = repr(expert)
        assert "SimpleTestExpert" in repr_str
        assert "SimpleExpert" in repr_str
        
        str_str = str(expert)
        assert "SimpleExpert" in str_str


class TestExpertAnalyze:
    """Tests for Expert.analyze() method"""
    
    @pytest.mark.asyncio
    async def test_analyze_simple(self, sample_request):
        """Test simple analyze implementation"""
        expert = SimpleTestExpert()
        
        result = await expert.analyze(sample_request)
        
        assert isinstance(result, ExpertResult)
        assert result.expert_name == "SimpleExpert"
        assert result.result == {"simple": True}
        assert result.confidence == 0.8
        assert not result.error
    
    @pytest.mark.asyncio
    async def test_analyze_returns_expert_result(self, sample_request):
        """Test that analyze returns ExpertResult"""
        expert = SimpleTestExpert()
        
        result = await expert.analyze(sample_request)
        
        assert isinstance(result, ExpertResult)


class TestExpertExecute:
    """Tests for Expert.execute() method with framework features"""
    
    @pytest.mark.asyncio
    async def test_execute_success(self, sample_request):
        """Test successful execution"""
        expert = SimpleTestExpert()
        
        result = await expert.execute(sample_request, timeout_sec=2.0)
        
        assert isinstance(result, ExpertResult)
        assert result.expert_name == "SimpleExpert"
        assert result.confidence == 0.8
        assert not result.error
        assert result.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_execute_timeout(self, sample_request):
        """Test that timeout is enforced"""
        expert = TimeoutTestExpert()
        
        result = await expert.execute(sample_request, timeout_sec=0.5)
        
        assert isinstance(result, ExpertResult)
        assert result.error is not None
        assert "timed out" in result.error.lower()
        assert result.confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_execute_exception_handling(self, sample_request):
        """Test that exceptions are caught and returned as errors"""
        expert = ErrorTestExpert()
        
        result = await expert.execute(sample_request, timeout_sec=2.0)
        
        assert isinstance(result, ExpertResult)
        assert result.error is not None
        assert "Intentional error" in result.error
        assert result.confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_execute_stats_tracking(self, sample_request):
        """Test that execution stats are tracked"""
        expert = SimpleTestExpert()
        
        # Initial state
        assert expert._stats["call_count"] == 0
        
        # Execute once
        await expert.execute(sample_request)
        assert expert._stats["call_count"] == 1
        
        # Execute again
        await expert.execute(sample_request)
        assert expert._stats["call_count"] == 2
    
    @pytest.mark.asyncio
    async def test_execute_error_counting(self, sample_request):
        """Test that errors are counted in stats"""
        expert = ErrorTestExpert()
        
        # Execute failing expert
        await expert.execute(sample_request)
        
        stats = expert.get_performance_stats()
        assert stats["error_count"] == 1
        assert stats["call_count"] == 1
        assert stats["error_rate"] == 1.0


class TestPerformanceStats:
    """Tests for performance statistics"""
    
    @pytest.mark.asyncio
    async def test_get_performance_stats(self, sample_request):
        """Test getting performance statistics"""
        expert = SimpleTestExpert()
        
        # Execute a few times
        for _ in range(3):
            await expert.execute(sample_request)
        
        stats = expert.get_performance_stats()
        
        assert stats["call_count"] == 3
        assert stats["error_count"] == 0
        assert stats["error_rate"] == 0.0
        assert stats["avg_duration_ms"] > 0
        assert stats["min_duration_ms"] > 0
        assert stats["max_duration_ms"] > 0
    
    @pytest.mark.asyncio
    async def test_reset_stats(self, sample_request):
        """Test resetting statistics"""
        expert = SimpleTestExpert()
        
        # Execute to accumulate stats
        for _ in range(5):
            await expert.execute(sample_request)
        
        stats_before = expert.get_performance_stats()
        assert stats_before["call_count"] == 5
        
        # Reset
        expert.reset_stats()
        
        stats_after = expert.get_performance_stats()
        assert stats_after["call_count"] == 0
        assert stats_after["total_duration_ms"] == 0.0


class TestMetadata:
    """Tests for expert metadata"""
    
    def test_get_metadata(self):
        """Test getting expert metadata"""
        expert = SimpleTestExpert()
        
        metadata = expert.get_metadata()
        
        assert metadata["name"] == "SimpleExpert"
        assert metadata["version"] == "1.0"
        assert "supported_tasks" in metadata
        assert "performance" in metadata
        assert metadata["supported_tasks"] == ["test", "simple"]
    
    def test_get_supported_tasks(self):
        """Test getting supported tasks"""
        expert = SimpleTestExpert()
        
        tasks = expert.get_supported_tasks()
        
        assert isinstance(tasks, list)
        assert "test" in tasks
        assert "simple" in tasks
    
    def test_get_supported_tasks_empty_default(self):
        """Test that default supported tasks is empty list"""
        class MinimalExpert(Expert):
            async def analyze(self, request):
                return ExpertResult(
                    expert_name=self.name,
                    result={},
                    confidence=0.5,
                    timestamp_start=0.0,
                    timestamp_end=1.0
                )
        
        expert = MinimalExpert(name="MinimalExpert")
        tasks = expert.get_supported_tasks()
        
        assert tasks == []


@pytest.mark.asyncio
async def test_abstract_expert_cannot_be_instantiated():
    """Test that Expert cannot be instantiated directly"""
    with pytest.raises(TypeError):
        Expert(name="DirectExpert")
