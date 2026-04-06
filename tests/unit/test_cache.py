"""
Unit tests for caching system
"""

import pytest
import time
from src.cache.cache_manager import CacheManager, get_cache


@pytest.fixture
def cache_manager():
    """Create cache manager instance"""
    return CacheManager(max_size=100, ttl_sec=3600)


class TestCacheManagerInitialization:
    """Tests for cache initialization"""
    
    def test_cache_creation(self, cache_manager):
        """Test cache creation"""
        assert cache_manager is not None
        assert cache_manager.max_size == 100
        assert cache_manager.ttl_sec == 3600
    
    def test_cache_empty_initially(self, cache_manager):
        """Test cache is empty initially"""
        assert cache_manager.get_size() == 0


class TestCacheBasicOperations:
    """Tests for basic cache operations"""
    
    def test_put_and_get(self, cache_manager):
        """Test put and get operations"""
        cache_manager.put("key1", "value1")
        assert cache_manager.get("key1") == "value1"
    
    def test_get_nonexistent(self, cache_manager):
        """Test getting nonexistent key"""
        assert cache_manager.get("nonexistent") is None
    
    def test_overwrite_value(self, cache_manager):
        """Test overwriting value"""
        cache_manager.put("key1", "value1")
        cache_manager.put("key1", "value2")
        assert cache_manager.get("key1") == "value2"
    
    def test_multiple_keys(self, cache_manager):
        """Test multiple keys"""
        cache_manager.put("key1", "value1")
        cache_manager.put("key2", "value2")
        
        assert cache_manager.get("key1") == "value1"
        assert cache_manager.get("key2") == "value2"


class TestCacheKeyGeneration:
    """Tests for cache key generation"""
    
    def test_generate_key(self, cache_manager):
        """Test key generation"""
        key = cache_manager._generate_key("Expert1", "test input")
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length
    
    def test_consistent_keys(self, cache_manager):
        """Test key generation consistency"""
        key1 = cache_manager._generate_key("Expert1", "input")
        key2 = cache_manager._generate_key("Expert1", "input")
        assert key1 == key2
    
    def test_different_keys(self, cache_manager):
        """Test different inputs generate different keys"""
        key1 = cache_manager._generate_key("Expert1", "input1")
        key2 = cache_manager._generate_key("Expert1", "input2")
        assert key1 != key2


class TestCacheExpiry:
    """Tests for cache expiry (TTL)"""
    
    def test_expired_cache(self):
        """Test cache expiry"""
        cache = CacheManager(ttl_sec=1)
        cache.put("key1", "value1")
        
        assert cache.get("key1") == "value1"
        
        # Wait for expiry
        time.sleep(1.1)
        
        assert cache.get("key1") is None


class TestCacheLRU:
    """Tests for LRU eviction"""
    
    def test_lru_eviction(self):
        """Test LRU eviction when full"""
        cache = CacheManager(max_size=3)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        assert cache.get_size() == 3
        
        # Add new key, should evict oldest
        cache.put("key4", "value4")
        
        assert cache.get_size() == 3
        assert cache.get("key1") is None  # LRU should be evicted
        assert cache.get("key4") == "value4"


class TestCacheStatistics:
    """Tests for cache statistics"""
    
    def test_cache_hits(self, cache_manager):
        """Test cache hits tracking"""
        cache_manager.put("key1", "value1")
        cache_manager.get("key1")
        
        stats = cache_manager.get_stats()
        assert stats["hits"] == 1
    
    def test_cache_misses(self, cache_manager):
        """Test cache misses tracking"""
        cache_manager.get("nonexistent")
        
        stats = cache_manager.get_stats()
        assert stats["misses"] == 1
    
    def test_hit_rate(self, cache_manager):
        """Test hit rate calculation"""
        cache_manager.put("key1", "value1")
        cache_manager.get("key1")
        cache_manager.get("key1")
        cache_manager.get("nonexistent")
        
        stats = cache_manager.get_stats()
        assert stats["hit_rate"] == pytest.approx(2/3, abs=0.01)
    
    def test_get_stats(self, cache_manager):
        """Test stats dictionary"""
        cache_manager.put("key1", "value1")
        cache_manager.get("key1")
        
        stats = cache_manager.get_stats()
        
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats
        assert "cache_size" in stats
        assert "utilization" in stats


class TestExpertCaching:
    """Tests for Expert result caching"""
    
    def test_cache_expert_result(self, cache_manager):
        """Test caching Expert results"""
        result = {"analysis": "test"}
        key = cache_manager.cache_result("StockExpert", "AAPL", result)
        
        cached = cache_manager.get_cached_result("StockExpert", "AAPL")
        assert cached == result
    
    def test_cache_result_with_context(self, cache_manager):
        """Test caching with context"""
        result = {"value": 100}
        key = cache_manager.cache_result(
            "Expert1", "input",
            result,
            context="value1"
        )
        
        cached = cache_manager.get_cached_result(
            "Expert1", "input",
            context="value1"
        )
        assert cached == result


class TestCacheClear:
    """Tests for cache clearing"""
    
    def test_clear_all(self, cache_manager):
        """Test clearing entire cache"""
        cache_manager.put("key1", "value1")
        cache_manager.put("key2", "value2")
        
        cache_manager.clear()
        
        assert cache_manager.get_size() == 0
        assert cache_manager.get("key1") is None
    
    def test_clear_expert(self, cache_manager):
        """Test clearing specific expert cache"""
        cache_manager.put("Expert1:key1", "value1")
        cache_manager.put("Expert2:key1", "value2")
        
        cache_manager.clear_expert("Expert1")
        
        assert cache_manager.get("Expert1:key1") is None
        assert cache_manager.get("Expert2:key1") == "value2"


class TestGlobalCache:
    """Tests for global cache instance"""
    
    def test_get_cache_singleton(self):
        """Test global cache singleton"""
        cache1 = get_cache()
        cache2 = get_cache()
        
        assert cache1 is cache2
    
    def test_global_cache_usage(self):
        """Test using global cache"""
        cache = get_cache()
        cache.put("test_key", "test_value")
        
        cache2 = get_cache()
        assert cache2.get("test_key") == "test_value"
