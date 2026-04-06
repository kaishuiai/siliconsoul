"""
Pytest configuration and fixtures for SiliconSoul MOE tests

This module provides shared fixtures and configuration for all tests.
"""

import pytest
import asyncio
from datetime import datetime

from src.core.moe_orchestrator import MOEOrchestrator
from src.models.request_response import ExpertRequest, ExpertResult, AggregatedResult
from src.experts.demo_expert_1 import DemoExpert1
from src.experts.demo_expert_2 import DemoExpert2
from src.experts.demo_expert_3 import DemoExpert3


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_request() -> ExpertRequest:
    """Create a sample ExpertRequest for testing."""
    return ExpertRequest(
        text="This is a great product! I love it very much.",
        user_id="test_user_123",
        context={"source": "test", "type": "demo"},
        task_type="sentiment_analysis"
    )


@pytest.fixture
def short_request() -> ExpertRequest:
    """Create a short sample request."""
    return ExpertRequest(
        text="Hi",
        user_id="test_user_short"
    )


@pytest.fixture
def long_request() -> ExpertRequest:
    """Create a long sample request."""
    text = " ".join(["word"] * 100)
    return ExpertRequest(
        text=text,
        user_id="test_user_long"
    )


@pytest.fixture
def demo_expert_1() -> DemoExpert1:
    """Create a DemoExpert1 instance."""
    return DemoExpert1()


@pytest.fixture
def demo_expert_2() -> DemoExpert2:
    """Create a DemoExpert2 instance."""
    return DemoExpert2()


@pytest.fixture
def demo_expert_3() -> DemoExpert3:
    """Create a DemoExpert3 instance."""
    return DemoExpert3()


@pytest.fixture
def moe_orchestrator() -> MOEOrchestrator:
    """Create a MOEOrchestrator with default timeout."""
    return MOEOrchestrator(default_timeout_sec=2.0)


@pytest.fixture
def moe_with_experts(moe_orchestrator, demo_expert_1, demo_expert_2, demo_expert_3) -> MOEOrchestrator:
    """Create a MOEOrchestrator with all demo experts registered."""
    moe_orchestrator.register_expert(demo_expert_1)
    moe_orchestrator.register_expert(demo_expert_2)
    moe_orchestrator.register_expert(demo_expert_3)
    return moe_orchestrator
