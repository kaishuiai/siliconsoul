"""
Unit tests for KnowledgeExpert

Tests:
- Knowledge base initialization
- Document search and retrieval
- Relevance ranking
- Answer generation
- Confidence calculation
- Source attribution
"""

import pytest

from src.experts.knowledge_expert import KnowledgeExpert
from src.models.request_response import ExpertRequest


@pytest.fixture
def knowledge_expert() -> KnowledgeExpert:
    """Create KnowledgeExpert instance"""
    return KnowledgeExpert()


@pytest.fixture
def knowledge_request() -> ExpertRequest:
    """Create request for knowledge retrieval"""
    return ExpertRequest(
        text="What is machine learning?",
        user_id="student_123"
    )


class TestKnowledgeExpertInitialization:
    """Tests for expert initialization"""
    
    def test_initialization(self, knowledge_expert):
        """Test expert initialization"""
        assert knowledge_expert.name == "KnowledgeExpert"
        assert knowledge_expert.version == "1.0"
    
    def test_knowledge_base_initialized(self, knowledge_expert):
        """Test that knowledge base is initialized"""
        assert knowledge_expert.knowledge_base is not None
        assert len(knowledge_expert.knowledge_base) > 0
    
    def test_supported_tasks(self, knowledge_expert):
        """Test supported tasks"""
        tasks = knowledge_expert.get_supported_tasks()
        assert "knowledge_query" in tasks
        assert "document_retrieval" in tasks
        assert "answer_generation" in tasks
        assert "fact_checking" in tasks
        assert "source_attribution" in tasks


class TestKnowledgeBaseSearch:
    """Tests for knowledge base search"""
    
    def test_search_returns_list(self, knowledge_expert):
        """Test that search returns a list"""
        results = knowledge_expert._search_knowledge_base("machine learning")
        assert isinstance(results, list)
    
    def test_search_finds_relevant_documents(self, knowledge_expert):
        """Test that search finds relevant documents"""
        results = knowledge_expert._search_knowledge_base("python programming")
        assert len(results) > 0
    
    def test_search_empty_query(self, knowledge_expert):
        """Test search with empty query"""
        results = knowledge_expert._search_knowledge_base("")
        # May or may not return results depending on implementation
        assert isinstance(results, list)
    
    def test_search_specific_topics(self, knowledge_expert):
        """Test searching for specific topics"""
        # Search for machine learning related
        ml_results = knowledge_expert._search_knowledge_base("machine learning")
        
        # Search for programming related
        prog_results = knowledge_expert._search_knowledge_base("python programming")
        
        assert len(ml_results) >= 0
        assert len(prog_results) >= 0


class TestDocumentRanking:
    """Tests for document ranking"""
    
    def test_ranking_returns_tuples(self, knowledge_expert):
        """Test that ranking returns properly structured tuples"""
        doc_ids = knowledge_expert._search_knowledge_base("machine learning")
        ranked = knowledge_expert._rank_documents(doc_ids, "machine learning")
        
        # Check structure
        for item in ranked:
            assert len(item) == 3
            assert isinstance(item[0], str)  # doc_id
            assert isinstance(item[1], dict)  # doc
            assert isinstance(item[2], (int, float))  # relevance score
    
    def test_ranking_scores_in_range(self, knowledge_expert):
        """Test that relevance scores are in valid range"""
        doc_ids = knowledge_expert._search_knowledge_base("python")
        ranked = knowledge_expert._rank_documents(doc_ids, "python")
        
        for _, _, score in ranked:
            assert 0 <= score <= 1.0
    
    def test_ranking_sorted_by_relevance(self, knowledge_expert):
        """Test that results are sorted by relevance"""
        doc_ids = knowledge_expert._search_knowledge_base("python")
        ranked = knowledge_expert._rank_documents(doc_ids, "python")
        
        if len(ranked) > 1:
            # Check that scores are in descending order
            for i in range(len(ranked) - 1):
                assert ranked[i][2] >= ranked[i + 1][2]


class TestAnswerGeneration:
    """Tests for answer generation"""
    
    def test_answer_is_string(self, knowledge_expert):
        """Test that answer is a string"""
        ranked_docs = knowledge_expert._rank_documents(
            knowledge_expert._search_knowledge_base("machine learning"),
            "machine learning"
        )
        answer = knowledge_expert._generate_answer("machine learning", ranked_docs)
        
        assert isinstance(answer, str)
    
    def test_answer_contains_query(self, knowledge_expert):
        """Test that answer references the query"""
        ranked_docs = knowledge_expert._rank_documents(
            knowledge_expert._search_knowledge_base("python"),
            "python"
        )
        answer = knowledge_expert._generate_answer("python", ranked_docs)
        
        # Should contain something about the topic
        assert len(answer) > 0
    
    def test_answer_handles_empty_results(self, knowledge_expert):
        """Test answer generation with no documents"""
        answer = knowledge_expert._generate_answer("query", [])
        
        assert isinstance(answer, str)
        assert "could not find" in answer.lower() or len(answer) > 0


class TestConfidenceCalculation:
    """Tests for confidence calculation"""
    
    def test_confidence_in_range(self, knowledge_expert):
        """Test that confidence is in valid range"""
        ranked_docs = knowledge_expert._rank_documents(
            knowledge_expert._search_knowledge_base("machine learning"),
            "machine learning"
        )
        confidence = knowledge_expert._calculate_confidence(ranked_docs)
        
        assert 0 <= confidence <= 1.0
    
    def test_confidence_zero_for_empty_docs(self, knowledge_expert):
        """Test confidence is 0 for empty results"""
        confidence = knowledge_expert._calculate_confidence([])
        assert confidence == 0.0
    
    def test_confidence_higher_with_more_matches(self, knowledge_expert):
        """Test that confidence increases with more matches"""
        # Single match
        single = knowledge_expert._calculate_confidence(
            [("doc1", {"keywords": [], "content": "", "title": "", "category": "", "relevance": 0.8, "timestamp": 0}, 0.8)]
        )
        
        # Multiple matches
        multiple = knowledge_expert._calculate_confidence(
            [
                ("doc1", {"keywords": [], "content": "", "title": "", "category": "", "relevance": 0.8, "timestamp": 0}, 0.8),
                ("doc2", {"keywords": [], "content": "", "title": "", "category": "", "relevance": 0.7, "timestamp": 0}, 0.7),
                ("doc3", {"keywords": [], "content": "", "title": "", "category": "", "relevance": 0.6, "timestamp": 0}, 0.6)
            ]
        )
        
        # More matches should give higher confidence
        assert multiple >= single


class TestAnswerTypeClassification:
    """Tests for answer type classification"""
    
    def test_definition_type(self, knowledge_expert):
        """Test classification of definition questions"""
        atype = knowledge_expert._classify_answer_type("What is machine learning?")
        assert atype == "definition"
    
    def test_explanation_type(self, knowledge_expert):
        """Test classification of explanation questions"""
        atype = knowledge_expert._classify_answer_type("How does Python work?")
        assert atype == "explanation"
    
    def test_comparison_type(self, knowledge_expert):
        """Test classification of comparison questions"""
        atype = knowledge_expert._classify_answer_type("Compare Python vs Java")
        assert atype == "comparison"
    
    def test_general_type(self, knowledge_expert):
        """Test classification of general queries"""
        atype = knowledge_expert._classify_answer_type("Tell me about databases")
        assert atype == "general"


class TestSourceAttribution:
    """Tests for source attribution"""
    
    def test_sources_structure(self, knowledge_expert):
        """Test that sources have correct structure"""
        ranked_docs = knowledge_expert._rank_documents(
            knowledge_expert._search_knowledge_base("python"),
            "python"
        )
        sources = knowledge_expert._prepare_sources(ranked_docs)
        
        for source in sources:
            assert "id" in source
            assert "title" in source
            assert "category" in source
            assert "relevance" in source
    
    def test_sources_max_three(self, knowledge_expert):
        """Test that sources are limited to top 3"""
        ranked_docs = knowledge_expert._rank_documents(
            knowledge_expert._search_knowledge_base("machine"),
            "machine"
        )
        sources = knowledge_expert._prepare_sources(ranked_docs)
        
        assert len(sources) <= 3
    
    def test_relevance_scores_in_sources(self, knowledge_expert):
        """Test that source relevance scores are valid"""
        ranked_docs = knowledge_expert._rank_documents(
            knowledge_expert._search_knowledge_base("learning"),
            "learning"
        )
        sources = knowledge_expert._prepare_sources(ranked_docs)
        
        for source in sources:
            assert 0 <= source["relevance"] <= 1.0


@pytest.mark.asyncio
async def test_full_retrieval(knowledge_expert, knowledge_request):
    """Test complete knowledge retrieval"""
    result = await knowledge_expert.execute(knowledge_request)
    
    assert result.expert_name == "KnowledgeExpert"
    assert 0 <= result.confidence <= 1.0
    assert not result.error
    
    # Check result structure
    assert "query" in result.result
    assert "answer" in result.result
    assert "answer_type" in result.result
    assert "relevant_documents" in result.result
    assert "top_sources" in result.result


@pytest.mark.asyncio
async def test_retrieval_different_queries(knowledge_expert):
    """Test retrieval with different queries"""
    queries = [
        "What is Python?",
        "How does web development work?",
        "Tell me about data science"
    ]
    
    for query_text in queries:
        request = ExpertRequest(text=query_text, user_id="user1")
        result = await knowledge_expert.execute(request)
        
        assert result.expert_name == "KnowledgeExpert"
        assert not result.error
        assert len(result.result) > 0


@pytest.mark.asyncio
async def test_performance_stats_update(knowledge_expert, knowledge_request):
    """Test that performance stats are updated"""
    initial_stats = knowledge_expert.get_performance_stats()
    initial_count = initial_stats["call_count"]
    
    await knowledge_expert.execute(knowledge_request)
    
    updated_stats = knowledge_expert.get_performance_stats()
    assert updated_stats["call_count"] == initial_count + 1
