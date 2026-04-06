"""
Unit tests for remaining experts (Decision, Reflection, Execution)
"""

import pytest

from src.experts.decision_expert import DecisionExpert
from src.experts.reflection_expert import ReflectionExpert
from src.experts.execution_expert import ExecutionExpert
from src.models.request_response import ExpertRequest


@pytest.fixture
def decision_expert() -> DecisionExpert:
    return DecisionExpert()

@pytest.fixture
def reflection_expert() -> ReflectionExpert:
    return ReflectionExpert()

@pytest.fixture
def execution_expert() -> ExecutionExpert:
    return ExecutionExpert()

@pytest.fixture
def request_obj() -> ExpertRequest:
    return ExpertRequest(text="test decision", user_id="user1")


class TestDecisionExpert:
    """Tests for DecisionExpert"""
    
    def test_initialization(self, decision_expert):
        assert decision_expert.name == "DecisionExpert"
        assert decision_expert.version == "1.0"
    
    def test_supported_tasks(self, decision_expert):
        tasks = decision_expert.get_supported_tasks()
        assert "decision_support" in tasks
        assert "risk_assessment" in tasks
    
    @pytest.mark.asyncio
    async def test_analyze(self, decision_expert, request_obj):
        result = await decision_expert.execute(request_obj)
        assert result.expert_name == "DecisionExpert"
        assert result.confidence >= 0
        assert not result.error


class TestReflectionExpert:
    """Tests for ReflectionExpert"""
    
    def test_initialization(self, reflection_expert):
        assert reflection_expert.name == "ReflectionExpert"
        assert reflection_expert.version == "1.0"
    
    def test_supported_tasks(self, reflection_expert):
        tasks = reflection_expert.get_supported_tasks()
        assert "decision_review" in tasks
        assert "lesson_extraction" in tasks
    
    @pytest.mark.asyncio
    async def test_analyze(self, reflection_expert, request_obj):
        result = await reflection_expert.execute(request_obj)
        assert result.expert_name == "ReflectionExpert"
        assert result.confidence >= 0
        assert not result.error


class TestExecutionExpert:
    """Tests for ExecutionExpert"""
    
    def test_initialization(self, execution_expert):
        assert execution_expert.name == "ExecutionExpert"
        assert execution_expert.version == "1.0"
    
    def test_supported_tasks(self, execution_expert):
        tasks = execution_expert.get_supported_tasks()
        assert "task_execution" in tasks
        assert "progress_tracking" in tasks
    
    @pytest.mark.asyncio
    async def test_analyze(self, execution_expert, request_obj):
        result = await execution_expert.execute(request_obj)
        assert result.expert_name == "ExecutionExpert"
        assert result.confidence >= 0
        assert not result.error


@pytest.mark.asyncio
async def test_all_three_experts(decision_expert, reflection_expert, execution_expert, request_obj):
    """Test all three experts in sequence"""
    
    # Test DecisionExpert
    d_result = await decision_expert.execute(request_obj)
    assert d_result.expert_name == "DecisionExpert"
    assert not d_result.error
    
    # Test ReflectionExpert
    r_result = await reflection_expert.execute(request_obj)
    assert r_result.expert_name == "ReflectionExpert"
    assert not r_result.error
    
    # Test ExecutionExpert
    e_result = await execution_expert.execute(request_obj)
    assert e_result.expert_name == "ExecutionExpert"
    assert not e_result.error
