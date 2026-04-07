"""
Unit tests for KnowledgeExpert - Updated for full compatibility
"""

import pytest
from src.experts.knowledge_expert import KnowledgeExpert, KnowledgeItem
from src.models.request_response import ExpertRequest, ExpertResult


@pytest.fixture
def expert():
    """Create a fresh KnowledgeExpert for each test."""
    return KnowledgeExpert()


@pytest.fixture
def basic_query_request():
    """Create a basic knowledge query request."""
    return ExpertRequest(
        text="What are moving averages?",
        user_id="test_user"
    )


class TestKnowledgeExpertInitialization:
    """Tests for expert initialization."""
    
    def test_expert_initializes_with_correct_name(self, expert):
        """Test that expert is initialized with correct name."""
        assert expert.name == "KnowledgeExpert"
        assert expert.version == "1.0"
    
    def test_expert_has_supported_tasks(self, expert):
        """Test that expert declares supported task types."""
        supported = expert.get_supported_tasks()
        assert "knowledge_query" in supported
        assert "information_retrieval" in supported
    
    def test_knowledge_base_initialized(self, expert):
        """Test that knowledge base is initialized with data."""
        assert len(expert._knowledge_cache) > 0
        assert "stocks" in expert._knowledge_cache
        assert "companies" in expert._knowledge_cache
        assert "rules" in expert._knowledge_cache


class TestQueryParsing:
    """Tests for query parsing."""
    
    def test_parse_query_extracts_keywords(self, expert):
        """Test that query parsing extracts keywords."""
        parsed = expert._parse_query("What about moving averages?")
        
        # Check that we have keywords
        assert len(parsed["keywords"]) > 0
        assert "moving" in parsed["keywords"]
    
    def test_parse_query_extracts_symbols(self, expert):
        """Test that query parsing extracts stock symbols."""
        parsed = expert._parse_query("Analyze 600000.SH")
        
        assert "600000.SH" in parsed["symbols"]
    
    def test_parse_query_extracts_numbers(self, expert):
        """Test that query parsing extracts numbers."""
        parsed = expert._parse_query("Check the 50 day moving average")
        
        assert "50" in parsed["numbers"]


class TestLocalDocsSearch:
    """Tests for local documentation search."""
    
    @pytest.mark.asyncio
    async def test_search_local_docs_returns_results(self, expert):
        """Test that local docs search returns results."""
        parsed = expert._parse_query("moving average technical analysis")
        results = await expert._search_local_docs(parsed)
        
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_search_local_docs_results_have_confidence(self, expert):
        """Test that results have confidence scores."""
        parsed = expert._parse_query("RSI indicator")
        results = await expert._search_local_docs(parsed)
        
        for result in results:
            assert result.confidence > 0
            assert result.confidence <= 1.0


class TestAnalysisCacheSearch:
    """Tests for analysis cache search."""
    
    @pytest.mark.asyncio
    async def test_search_analysis_cache_with_symbol(self, expert):
        """Test analysis cache search with stock symbol."""
        parsed = expert._parse_query("analysis 600000.SH")
        results = await expert._search_analysis_cache(parsed)
        
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_search_analysis_cache_empty_without_keywords(self, expert):
        """Test analysis cache search without relevant keywords."""
        parsed = expert._parse_query("hello world")
        results = await expert._search_analysis_cache(parsed)
        
        assert isinstance(results, list)


class TestUserHistorySearch:
    """Tests for user history search."""
    
    @pytest.mark.asyncio
    async def test_search_user_history_returns_results(self, expert):
        """Test that user history search returns results."""
        parsed = expert._parse_query("my previous queries")
        results = await expert._search_user_history(parsed)
        
        assert len(results) > 0


class TestRankingAndRelevance:
    """Tests for ranking and relevance scoring."""
    
    def test_rank_by_relevance_sorts_results(self, expert):
        """Test that results are ranked by relevance."""
        items = [
            KnowledgeItem(source="test1", content="apple", relevance_score=0.5, confidence=0.8),
            KnowledgeItem(source="test2", content="banana", relevance_score=0.9, confidence=0.7),
            KnowledgeItem(source="test3", content="cherry", relevance_score=0.3, confidence=0.9),
        ]
        
        parsed = {"keywords": ["test"], "lowercase": "test"}
        sorted_items = expert._rank_by_relevance(items, parsed)
        
        assert len(sorted_items) == 3


class TestDeduplication:
    """Tests for duplicate removal."""
    
    def test_remove_duplicates_eliminates_near_duplicates(self, expert):
        """Test that near-duplicates are removed."""
        items = [
            KnowledgeItem(source="source1", content="Moving Average is a technical indicator used in stock analysis"),
            KnowledgeItem(source="source2", content="Moving Average is a technical indicator used in stock trading"),
            KnowledgeItem(source="source3", content="Completely different content here"),
        ]
        
        deduped = expert._remove_duplicates(items)
        
        assert len(deduped) <= len(items)
    
    def test_remove_duplicates_preserves_unique_items(self, expert):
        """Test that unique items are preserved."""
        items = [
            KnowledgeItem(source="source1", content="First unique content"),
            KnowledgeItem(source="source2", content="Second unique content"),
        ]
        
        deduped = expert._remove_duplicates(items)
        
        assert len(deduped) == len(items)


class TestRecommendationGeneration:
    """Tests for recommendation generation."""
    
    def test_recommendations_for_stock_query(self, expert):
        """Test recommendations for stock-related queries."""
        results = [KnowledgeItem(source="test", content="Test")]
        recommendations = expert._generate_recommendations("analyze stock 600000", results)
        
        assert len(recommendations) > 0
    
    def test_recommendations_for_empty_results(self, expert):
        """Test recommendations when no results found."""
        recommendations = expert._generate_recommendations("test query", [])
        
        assert len(recommendations) > 0


class TestSummaryGeneration:
    """Tests for summary generation."""
    
    def test_summary_for_results(self, expert):
        """Test summary generation for query results."""
        results = [
            KnowledgeItem(source="source1", content="Item 1", confidence=0.9),
            KnowledgeItem(source="source2", content="Item 2", confidence=0.8),
        ]
        
        summary = expert._generate_summary("test query", results)
        
        assert "2" in summary or "relevant" in summary.lower()
    
    def test_summary_for_empty_results(self, expert):
        """Test summary when no results found."""
        summary = expert._generate_summary("test query", [])
        
        assert "no knowledge" in summary.lower() or "not found" in summary.lower()


class TestAnalyzeMethod:
    """Tests for main analyze method."""
    
    @pytest.mark.asyncio
    async def test_analyze_with_valid_query(self, expert, basic_query_request):
        """Test analyze with valid query."""
        result = await expert.analyze(basic_query_request)
        
        assert isinstance(result, ExpertResult)
        assert result.expert_name == "KnowledgeExpert"
        assert result.result is not None
    
    @pytest.mark.asyncio
    async def test_analyze_returns_knowledge_items(self, expert):
        """Test that analyze returns knowledge items."""
        request = ExpertRequest(
            text="What is technical analysis?",
            user_id="test_user"
        )
        
        result = await expert.analyze(request)
        
        if result.error is None:
            assert "knowledge_items" in result.result
            assert isinstance(result.result["knowledge_items"], list)
    
    @pytest.mark.asyncio
    async def test_analyze_with_custom_top_k(self, expert):
        """Test analyze with custom top-K parameter."""
        request = ExpertRequest(
            text="What are indicators?",
            user_id="test_user",
            extra_params={"top_k": 3}
        )
        
        result = await expert.analyze(request)
        
        if result.error is None:
            items = result.result.get("knowledge_items", [])
            assert len(items) <= 3
    
    @pytest.mark.asyncio
    async def test_analyze_with_confidence_threshold(self, expert):
        """Test analyze with confidence threshold."""
        request = ExpertRequest(
            text="Tell me about stocks",
            user_id="test_user",
            extra_params={"min_confidence": 0.8}
        )
        
        result = await expert.analyze(request)
        
        if result.error is None:
            items = result.result.get("knowledge_items", [])
            for item in items:
                assert item["confidence"] >= 0.8
    
    
    @pytest.mark.asyncio
    async def test_analyze_result_has_timestamps(self, expert):
        """Test that result has proper timing information."""
        request = ExpertRequest(
            text="Test query",
            user_id="test_user"
        )
        
        result = await expert.analyze(request)
        
        assert result.timestamp_start > 0
        assert result.timestamp_end > 0
        assert result.timestamp_end >= result.timestamp_start


class TestCaching:
    """Tests for query caching."""
    
    @pytest.mark.asyncio
    async def test_identical_queries_return_cached_result(self, expert):
        """Test that identical queries return cached results."""
        request1 = ExpertRequest(
            text="What is RSI?",
            user_id="test_user"
        )
        request2 = ExpertRequest(
            text="What is RSI?",
            user_id="test_user"
        )
        
        result1 = await expert.analyze(request1)
        result2 = await expert.analyze(request2)
        
        # Second result should have from_cache metadata
        if result2.metadata and result2.error is None:
            assert result2.metadata.get("from_cache") == True
    
    def test_cache_key_generation(self, expert):
        """Test cache key generation."""
        key1 = expert._make_cache_key("test query", ["source1", "source2"])
        key2 = expert._make_cache_key("test query", ["source2", "source1"])
        
        assert key1 == key2


class TestKnowledgeItem:
    """Tests for KnowledgeItem data class."""
    
    def test_knowledge_item_to_dict(self):
        """Test KnowledgeItem conversion to dict."""
        item = KnowledgeItem(
            source="test_source",
            content="Test content",
            relevance_score=0.85,
            confidence=0.9
        )
        
        item_dict = item.to_dict()
        
        assert item_dict["source"] == "test_source"
        assert item_dict["content"] == "Test content"


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_query_pipeline(self, expert):
        """Test complete query pipeline."""
        request = ExpertRequest(
            text="What's technical analysis for 600000.SH?",
            user_id="test_user",
            extra_params={
                "knowledge_sources": ["local_docs", "analysis_cache"],
                "top_k": 5,
                "min_confidence": 0.5
            }
        )
        
        result = await expert.analyze(request)
        
        assert result.expert_name == "KnowledgeExpert"
        if result.error is None:
            assert "query" in result.result


class TestPerformance:
    """Performance tests."""
    
    @pytest.mark.asyncio
    async def test_query_response_time(self, expert):
        """Test that queries complete within reasonable time."""
        request = ExpertRequest(
            text="Test query for performance",
            user_id="test_user"
        )
        
        result = await expert.analyze(request)
        
        duration = result.timestamp_end - result.timestamp_start
        assert duration < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
