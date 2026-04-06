"""
Unit tests for data models (Pydantic models)

Tests validation, serialization, and properties of:
- ExpertRequest
- ExpertResult
- AggregatedResult
"""

import pytest
from datetime import datetime

from src.models.request_response import (
    ExpertRequest,
    ExpertResult,
    AggregatedResult
)


class TestExpertRequest:
    """Tests for ExpertRequest model"""
    
    def test_create_with_required_fields(self):
        """Test creating ExpertRequest with only required fields"""
        request = ExpertRequest(
            text="test input",
            user_id="user_123"
        )
        
        assert request.text == "test input"
        assert request.user_id == "user_123"
        assert request.context is None
        assert request.task_type is None
        assert request.extra_params is None
        assert isinstance(request.timestamp, float)
    
    def test_create_with_all_fields(self):
        """Test creating ExpertRequest with all fields"""
        timestamp = datetime.now().timestamp()
        context = {"key": "value"}
        extra = {"param": 123}
        
        request = ExpertRequest(
            text="full request",
            user_id="user_456",
            context=context,
            task_type="analysis",
            timestamp=timestamp,
            extra_params=extra
        )
        
        assert request.text == "full request"
        assert request.user_id == "user_456"
        assert request.context == context
        assert request.task_type == "analysis"
        assert request.timestamp == timestamp
        assert request.extra_params == extra
    
    def test_validation_empty_text(self):
        """Test validation rejects empty text"""
        with pytest.raises(ValueError):
            ExpertRequest(text="", user_id="user_123")
    
    def test_validation_missing_user_id(self):
        """Test validation requires user_id"""
        with pytest.raises(ValueError):
            ExpertRequest(text="test")
    
    def test_validation_long_text(self):
        """Test validation rejects overly long text"""
        long_text = "x" * 10001
        with pytest.raises(ValueError):
            ExpertRequest(text=long_text, user_id="user_123")
    
    def test_json_serialization(self):
        """Test JSON serialization"""
        request = ExpertRequest(
            text="test",
            user_id="user_123"
        )
        
        json_data = request.model_dump_json()
        assert isinstance(json_data, str)
        assert "test" in json_data
        assert "user_123" in json_data
    
    def test_auto_timestamp(self):
        """Test that timestamp is auto-set if not provided"""
        request1 = ExpertRequest(text="test", user_id="user_1")
        request2 = ExpertRequest(text="test", user_id="user_2")
        
        # Both should have timestamps
        assert request1.timestamp > 0
        assert request2.timestamp > 0
        
        # Should be different (or at least not earlier)
        assert request2.timestamp >= request1.timestamp


class TestExpertResult:
    """Tests for ExpertResult model"""
    
    def test_create_success_result(self):
        """Test creating a successful ExpertResult"""
        timestamp_start = datetime.now().timestamp()
        timestamp_end = timestamp_start + 1.5
        
        result = ExpertResult(
            expert_name="TestExpert",
            result={"score": 0.9},
            confidence=0.95,
            metadata={"version": "1.0"},
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end
        )
        
        assert result.expert_name == "TestExpert"
        assert result.result == {"score": 0.9}
        assert result.confidence == 0.95
        assert result.error is None
        assert result.duration_ms == 1500.0
    
    def test_create_error_result(self):
        """Test creating an error ExpertResult"""
        timestamp_start = datetime.now().timestamp()
        timestamp_end = timestamp_start + 0.5
        
        result = ExpertResult(
            expert_name="TestExpert",
            result={},
            confidence=0.0,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
            error="Something went wrong"
        )
        
        assert result.error == "Something went wrong"
        assert result.confidence == 0.0
        assert result.duration_ms == 500.0
    
    def test_duration_ms_property(self):
        """Test duration_ms property calculation"""
        timestamp_start = 1000.0
        timestamp_end = 1002.5  # 2.5 seconds later
        
        result = ExpertResult(
            expert_name="TestExpert",
            result={},
            confidence=0.8,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end
        )
        
        assert result.duration_ms == 2500.0
    
    def test_confidence_validation(self):
        """Test that confidence is between 0 and 1"""
        # Valid
        result = ExpertResult(
            expert_name="TestExpert",
            result={},
            confidence=0.5,
            timestamp_start=0.0,
            timestamp_end=1.0
        )
        assert result.confidence == 0.5
        
        # Invalid - too high
        with pytest.raises(ValueError):
            ExpertResult(
                expert_name="TestExpert",
                result={},
                confidence=1.5,  # > 1.0
                timestamp_start=0.0,
                timestamp_end=1.0
            )
        
        # Invalid - negative
        with pytest.raises(ValueError):
            ExpertResult(
                expert_name="TestExpert",
                result={},
                confidence=-0.1,  # < 0.0
                timestamp_start=0.0,
                timestamp_end=1.0
            )
    
    def test_metadata_default_empty_dict(self):
        """Test that metadata defaults to empty dict"""
        result = ExpertResult(
            expert_name="TestExpert",
            result={},
            confidence=0.8,
            timestamp_start=0.0,
            timestamp_end=1.0
        )
        
        assert result.metadata == {}
        assert isinstance(result.metadata, dict)


class TestAggregatedResult:
    """Tests for AggregatedResult model"""
    
    def test_create_aggregated_result(self):
        """Test creating an AggregatedResult"""
        results = [
            ExpertResult(
                expert_name="Expert1",
                result={},
                confidence=0.9,
                timestamp_start=0.0,
                timestamp_end=1.0
            ),
            ExpertResult(
                expert_name="Expert2",
                result={},
                confidence=0.8,
                timestamp_start=0.0,
                timestamp_end=1.0
            )
        ]
        
        aggregated = AggregatedResult(
            final_result={"decision": "ACCEPT"},
            expert_results=results,
            overall_confidence=0.85,
            num_experts=2,
            consensus_level="high",
            duration_ms=1000.0
        )
        
        assert aggregated.overall_confidence == 0.85
        assert aggregated.num_experts == 2
        assert aggregated.consensus_level == "high"
        assert len(aggregated.expert_results) == 2
    
    def test_consensus_level_validation(self):
        """Test consensus level validation"""
        # Valid levels
        for level in ["high", "medium", "low", "none"]:
            aggregated = AggregatedResult(
                final_result={},
                expert_results=[],
                overall_confidence=0.5,
                num_experts=0,
                consensus_level=level,
                duration_ms=0.0
            )
            assert aggregated.consensus_level == level
    
    def test_overall_confidence_validation(self):
        """Test overall_confidence bounds"""
        # Valid
        aggregated = AggregatedResult(
            final_result={},
            expert_results=[],
            overall_confidence=0.75,
            num_experts=0,
            consensus_level="high",
            duration_ms=0.0
        )
        assert aggregated.overall_confidence == 0.75
        
        # Invalid - too high
        with pytest.raises(ValueError):
            AggregatedResult(
                final_result={},
                expert_results=[],
                overall_confidence=1.5,
                num_experts=0,
                consensus_level="high",
                duration_ms=0.0
            )
    
    def test_json_round_trip(self):
        """Test JSON serialization and deserialization"""
        original = AggregatedResult(
            final_result={"score": 0.9},
            expert_results=[],
            overall_confidence=0.85,
            num_experts=0,
            consensus_level="high",
            duration_ms=500.0
        )
        
        # Serialize
        json_data = original.model_dump_json()
        
        # Deserialize
        recovered = AggregatedResult.model_validate_json(json_data)
        
        assert recovered.overall_confidence == original.overall_confidence
        assert recovered.consensus_level == original.consensus_level
        assert recovered.duration_ms == original.duration_ms
