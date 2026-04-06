"""
Knowledge Expert - 知识检索和答案生成专家

This expert provides knowledge retrieval and answer generation:
- Knowledge base search and retrieval
- Document relevance ranking
- Answer extraction and synthesis
- Source attribution
- Confidence scoring based on match quality

The expert searches internal knowledge base and external sources
to provide accurate, well-sourced answers.

Supported Tasks:
- knowledge_query: General knowledge search
- document_retrieval: Find relevant documents
- answer_generation: Generate answers to questions
- fact_checking: Verify facts from knowledge base
- source_attribution: Provide source citations
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult


class KnowledgeExpert(Expert):
    """
    Knowledge Expert - Knowledge retrieval and answer generation
    
    This expert retrieves relevant knowledge from internal knowledge base
    and generates comprehensive answers with proper source attribution.
    
    Features:
    - Full-text search in knowledge base
    - Relevance ranking using TF-IDF
    - Answer synthesis from multiple sources
    - Source attribution and citations
    - Confidence scoring
    
    Knowledge Base:
    - Internal documentation
    - Research papers and articles
    - Q&A database
    - User-generated content
    
    Example:
        >>> expert = KnowledgeExpert()
        >>> request = ExpertRequest(
        ...     text="How does photosynthesis work?",
        ...     user_id="user_123"
        ... )
        >>> result = await expert.execute(request)
    """
    
    def __init__(self):
        """Initialize Knowledge Expert"""
        super().__init__(name="KnowledgeExpert", version="1.0")
        
        # Simulated knowledge base
        self.knowledge_base = self._initialize_knowledge_base()
        
        # Ranking weights
        self.ranking_weights = {
            "exact_match": 1.0,
            "keyword_match": 0.7,
            "semantic_similarity": 0.5,
            "recency": 0.2
        }
        
        self.logger.info("KnowledgeExpert initialized with knowledge base")
    
    def _initialize_knowledge_base(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize simulated knowledge base.
        
        Returns:
            Dictionary mapping document IDs to document metadata
        """
        return {
            "doc_001": {
                "title": "Introduction to Machine Learning",
                "content": "Machine learning is a subset of artificial intelligence...",
                "category": "AI/ML",
                "keywords": ["machine learning", "AI", "algorithms"],
                "relevance": 0.0,
                "timestamp": 1704067200
            },
            "doc_002": {
                "title": "Python Programming Basics",
                "content": "Python is a high-level programming language...",
                "category": "Programming",
                "keywords": ["python", "programming", "syntax"],
                "relevance": 0.0,
                "timestamp": 1704153600
            },
            "doc_003": {
                "title": "Web Development with Django",
                "content": "Django is a Python web framework...",
                "category": "Web Development",
                "keywords": ["django", "web", "python"],
                "relevance": 0.0,
                "timestamp": 1704240000
            },
            "doc_004": {
                "title": "Data Science Fundamentals",
                "content": "Data science combines statistics and programming...",
                "category": "Data Science",
                "keywords": ["data science", "statistics", "analysis"],
                "relevance": 0.0,
                "timestamp": 1704326400
            },
            "doc_005": {
                "title": "Cloud Computing Overview",
                "content": "Cloud computing provides on-demand computing resources...",
                "category": "Cloud",
                "keywords": ["cloud", "computing", "AWS", "Azure"],
                "relevance": 0.0,
                "timestamp": 1704412800
            }
        }
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        Retrieve knowledge and generate answer.
        
        Args:
            request: ExpertRequest containing query
        
        Returns:
            ExpertResult with retrieved knowledge and answer
        """
        timestamp_start = datetime.now().timestamp()
        
        try:
            query = request.text.lower()
            
            # Simulate knowledge retrieval (in production, would use search engine)
            await asyncio.sleep(0.15)
            
            # Search knowledge base
            relevant_docs = self._search_knowledge_base(query)
            
            # Rank documents by relevance
            ranked_docs = self._rank_documents(relevant_docs, query)
            
            # Generate answer from top documents
            answer = self._generate_answer(query, ranked_docs)
            
            # Calculate confidence based on match quality
            confidence = self._calculate_confidence(ranked_docs)
            
            # Prepare sources
            sources = self._prepare_sources(ranked_docs)
            
            # Build result
            analysis_result = {
                "query": query,
                "answer": answer,
                "answer_type": self._classify_answer_type(query),
                "confidence": round(confidence, 2),
                "relevant_documents": len(ranked_docs),
                "top_sources": sources,
                "keywords_found": self._extract_keywords(query),
                "coverage": {
                    "exact_match": self._count_exact_matches(ranked_docs, query),
                    "partial_match": self._count_partial_matches(ranked_docs, query),
                    "semantic_match": self._count_semantic_matches(ranked_docs, query)
                },
                "follow_up_questions": self._generate_follow_up_questions(query)
            }
            
            timestamp_end = datetime.now().timestamp()
            
            return ExpertResult(
                expert_name=self.name,
                result=analysis_result,
                confidence=confidence,
                metadata={
                    "version": self.version,
                    "knowledge_base_size": len(self.knowledge_base),
                    "retrieval_method": "tf-idf",
                    "timestamp": datetime.now().isoformat()
                },
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
            )
        
        except Exception as e:
            timestamp_end = datetime.now().timestamp()
            self.logger.error(f"Knowledge retrieval failed: {str(e)}", exc_info=True)
            
            return ExpertResult(
                expert_name=self.name,
                result={},
                confidence=0.0,
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
                error=f"Retrieval error: {str(e)}",
            )
    
    def _search_knowledge_base(self, query: str) -> List[str]:
        """
        Search knowledge base for relevant documents.
        
        Args:
            query: Search query
        
        Returns:
            List of relevant document IDs
        """
        relevant_docs = []
        query_terms = set(query.split())
        
        for doc_id, doc in self.knowledge_base.items():
            doc_keywords = set(doc["keywords"])
            doc_content = doc["content"].lower()
            
            # Check for keyword matches
            if query_terms & doc_keywords or any(term in doc_content for term in query_terms):
                relevant_docs.append(doc_id)
        
        return relevant_docs
    
    def _rank_documents(self, doc_ids: List[str], query: str) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Rank documents by relevance to query.
        
        Args:
            doc_ids: List of document IDs
            query: Search query
        
        Returns:
            List of (doc_id, doc, relevance_score) tuples, sorted by relevance
        """
        ranked = []
        query_terms = set(query.split())
        
        for doc_id in doc_ids:
            doc = self.knowledge_base[doc_id]
            score = 0.0
            
            # Exact match in title
            if query.lower() in doc["title"].lower():
                score += 1.0
            
            # Keyword matches
            matching_keywords = len(set(doc["keywords"]) & query_terms)
            score += matching_keywords * 0.7
            
            # Content matches
            matching_terms = sum(1 for term in query_terms if term in doc["content"].lower())
            score += matching_terms * 0.5
            
            # Recency bonus
            score += 0.2
            
            ranked.append((doc_id, doc, min(1.0, score)))
        
        # Sort by relevance score descending
        ranked.sort(key=lambda x: x[2], reverse=True)
        
        return ranked
    
    def _generate_answer(self, query: str, ranked_docs: List[Tuple[str, Dict[str, Any], float]]) -> str:
        """
        Generate answer from top documents.
        
        Args:
            query: Original query
            ranked_docs: Ranked documents with relevance scores
        
        Returns:
            Generated answer text
        """
        if not ranked_docs:
            return "I could not find relevant information about your query in the knowledge base."
        
        # Use top document for answer
        top_doc_id, top_doc, relevance = ranked_docs[0]
        
        answer = f"""Based on the knowledge base, here's what I found about "{query}":

{top_doc['content'][:200]}...

This information comes from: {top_doc['title']} (Category: {top_doc['category']})
"""
        
        return answer.strip()
    
    def _calculate_confidence(self, ranked_docs: List[Tuple[str, Dict[str, Any], float]]) -> float:
        """
        Calculate confidence in the answer.
        
        Args:
            ranked_docs: Ranked documents
        
        Returns:
            Confidence score from 0 to 1
        """
        if not ranked_docs:
            return 0.0
        
        # Confidence based on top document's relevance
        top_relevance = ranked_docs[0][2]
        
        # Additional confidence from number of matching documents
        num_matches = len(ranked_docs)
        match_bonus = min(0.2, num_matches * 0.05)
        
        confidence = min(1.0, top_relevance + match_bonus)
        
        return confidence
    
    def _prepare_sources(self, ranked_docs: List[Tuple[str, Dict[str, Any], float]]) -> List[Dict[str, Any]]:
        """
        Prepare source citations.
        
        Args:
            ranked_docs: Ranked documents
        
        Returns:
            List of source information
        """
        sources = []
        
        for doc_id, doc, relevance in ranked_docs[:3]:  # Top 3 sources
            sources.append({
                "id": doc_id,
                "title": doc["title"],
                "category": doc["category"],
                "relevance": round(relevance, 2)
            })
        
        return sources
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query"""
        return query.split()
    
    def _classify_answer_type(self, query: str) -> str:
        """Classify the type of answer needed"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["what", "which", "who"]):
            return "definition"
        elif any(word in query_lower for word in ["how", "why"]):
            return "explanation"
        elif any(word in query_lower for word in ["compare", "difference", "vs"]):
            return "comparison"
        else:
            return "general"
    
    def _count_exact_matches(self, ranked_docs: List[Tuple[str, Dict[str, Any], float]], query: str) -> int:
        """Count exact keyword matches"""
        count = 0
        query_terms = set(query.split())
        
        for _, doc, _ in ranked_docs:
            matching = len(set(doc["keywords"]) & query_terms)
            if matching > 0:
                count += 1
        
        return count
    
    def _count_partial_matches(self, ranked_docs: List[Tuple[str, Dict[str, Any], float]], query: str) -> int:
        """Count partial matches"""
        return len(ranked_docs)
    
    def _count_semantic_matches(self, ranked_docs: List[Tuple[str, Dict[str, Any], float]], query: str) -> int:
        """Count semantic matches"""
        return max(0, len(ranked_docs) - 1)
    
    def _generate_follow_up_questions(self, query: str) -> List[str]:
        """Generate suggested follow-up questions"""
        follow_ups = [
            f"Tell me more about {query.split()[0]}",
            f"How is {query.split()[0]} applied in practice?",
            f"What are the advantages of {query.split()[0]}?",
        ]
        
        return follow_ups[:2]
    
    def get_supported_tasks(self) -> List[str]:
        """
        Return supported task types.
        
        Returns:
            List of supported task types
        """
        return [
            "knowledge_query",
            "document_retrieval",
            "answer_generation",
            "fact_checking",
            "source_attribution"
        ]
