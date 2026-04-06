"""
Unit tests for storage system
"""

import pytest
import json
from pathlib import Path
from src.storage.storage_manager import StorageManager
from src.storage.models import RequestRecord, ResultRecord


@pytest.fixture
def memory_storage():
    """Create memory storage"""
    return StorageManager(storage_type="memory")


@pytest.fixture
def sqlite_storage(tmp_path):
    """Create SQLite storage"""
    db_path = str(tmp_path / "test.db")
    return StorageManager(storage_type="sqlite", connection_string=db_path)


@pytest.fixture
def json_storage(tmp_path):
    """Create JSON storage"""
    json_path = str(tmp_path / "storage.json")
    return StorageManager(storage_type="json", connection_string=json_path)


class TestStorageInitialization:
    """Tests for storage initialization"""
    
    def test_memory_storage_creation(self, memory_storage):
        """Test memory storage creation"""
        assert memory_storage.storage_type == "memory"
        assert memory_storage.requests == []
        assert memory_storage.results == []
    
    def test_sqlite_storage_creation(self, sqlite_storage):
        """Test SQLite storage creation"""
        assert sqlite_storage.storage_type == "sqlite"
    
    def test_json_storage_creation(self, json_storage):
        """Test JSON storage creation"""
        assert json_storage.storage_type == "json"


class TestRequestStorage:
    """Tests for request storage"""
    
    def test_add_request(self, memory_storage):
        """Test adding request"""
        request_id = memory_storage.add_request(
            user_id="user1",
            text="test query"
        )
        
        assert request_id is not None
        assert memory_storage.request_count == 1
    
    def test_get_request(self, memory_storage):
        """Test getting request"""
        request_id = memory_storage.add_request(
            user_id="user1",
            text="test query"
        )
        
        request = memory_storage.get_request(request_id)
        assert request is not None
        assert request.user_id == "user1"
        assert request.text == "test query"
    
    def test_add_request_with_context(self, memory_storage):
        """Test adding request with context"""
        context = {"key": "value"}
        request_id = memory_storage.add_request(
            user_id="user1",
            text="query",
            context=context
        )
        
        request = memory_storage.get_request(request_id)
        assert request.context == context


class TestResultStorage:
    """Tests for result storage"""
    
    def test_add_result(self, memory_storage):
        """Test adding result"""
        request_id = memory_storage.add_request(user_id="user1", text="query")
        
        result_id = memory_storage.add_result(
            request_id=request_id,
            expert_name="Expert1",
            result={"analysis": "test"},
            confidence=0.95,
            duration_ms=100.5
        )
        
        assert result_id is not None
        assert memory_storage.result_count == 1
    
    def test_get_results(self, memory_storage):
        """Test getting results"""
        request_id = memory_storage.add_request(user_id="user1", text="query")
        
        result_id = memory_storage.add_result(
            request_id=request_id,
            expert_name="Expert1",
            result={"data": "value"},
            confidence=0.9,
            duration_ms=50.0
        )
        
        results = memory_storage.get_results(request_id)
        assert len(results) == 1
        assert results[0].expert_name == "Expert1"
    
    def test_multiple_results(self, memory_storage):
        """Test multiple results for same request"""
        request_id = memory_storage.add_request(user_id="user1", text="query")
        
        for i in range(3):
            memory_storage.add_result(
                request_id=request_id,
                expert_name=f"Expert{i}",
                result={"index": i},
                confidence=0.8 + i*0.05,
                duration_ms=50.0 + i*10
            )
        
        results = memory_storage.get_results(request_id)
        assert len(results) == 3


class TestExpertStats:
    """Tests for expert statistics"""
    
    def test_expert_stats(self, memory_storage):
        """Test expert statistics"""
        req1 = memory_storage.add_request(user_id="user1", text="query1")
        req2 = memory_storage.add_request(user_id="user2", text="query2")
        
        memory_storage.add_result(req1, "Expert1", {}, 0.9, 100)
        memory_storage.add_result(req1, "Expert1", {}, 0.8, 110)
        memory_storage.add_result(req2, "Expert2", {}, 0.7, 90)
        
        stats = memory_storage.get_expert_stats()
        
        assert "Expert1" in stats
        assert stats["Expert1"]["count"] == 2
        assert stats["Expert1"]["avg_confidence"] == pytest.approx(0.85, abs=0.01)


class TestStorageMultipleBackends:
    """Tests with multiple storage backends"""
    
    def test_memory_vs_sqlite(self, memory_storage, sqlite_storage):
        """Test both backends work the same way"""
        # Memory storage
        req_mem = memory_storage.add_request(user_id="user1", text="query")
        res_mem = memory_storage.add_result(req_mem, "Expert", {}, 0.9, 100)
        
        # SQLite storage
        req_sql = sqlite_storage.add_request(user_id="user1", text="query")
        res_sql = sqlite_storage.add_result(req_sql, "Expert", {}, 0.9, 100)
        
        # Verify both work
        assert memory_storage.get_request(req_mem) is not None
        assert sqlite_storage.get_request(req_sql) is not None
    
    def test_json_storage_persistence(self, json_storage, tmp_path):
        """Test JSON storage persistence"""
        json_path = str(tmp_path / "test.json")
        storage1 = StorageManager(storage_type="json", connection_string=json_path)
        
        request_id = storage1.add_request(user_id="user1", text="query")
        storage1.add_result(request_id, "Expert", {"data": "value"}, 0.9, 100)
        
        # Create new instance - should load from file
        storage2 = StorageManager(storage_type="json", connection_string=json_path)
        
        assert len(storage2.requests) > 0
        assert len(storage2.results) > 0


class TestStorageUtilities:
    """Tests for storage utilities"""
    
    def test_clear_storage(self, memory_storage):
        """Test clearing storage"""
        memory_storage.add_request(user_id="user1", text="query")
        memory_storage.add_result(
            memory_storage.requests[0].request_id,
            "Expert",
            {},
            0.9,
            100
        )
        
        assert len(memory_storage.requests) > 0
        
        memory_storage.clear()
        
        assert len(memory_storage.requests) == 0
        assert len(memory_storage.results) == 0
    
    def test_get_stats(self, memory_storage):
        """Test storage statistics"""
        memory_storage.add_request(user_id="user1", text="query")
        
        stats = memory_storage.get_stats()
        
        assert "storage_type" in stats
        assert "request_count" in stats
        assert stats["storage_type"] == "memory"
