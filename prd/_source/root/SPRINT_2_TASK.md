# Sprint 2 Task: Implement KnowledgeExpert

**Status**: ACTIVE - Start Implementation Now  
**Priority**: P0 - Critical Path  
**Timeline**: Tomorrow morning (2026-04-08)  
**Developer**: CC

---

## 🎯 Objective

Implement `KnowledgeExpert` that provides intelligent knowledge base querying, retrieval, and information aggregation.

---

## 📋 Requirements

### 1. Core Functionality
- [ ] Initialize knowledge base connection
- [ ] Query knowledge base with natural language
- [ ] Rank results by relevance
- [ ] Aggregate multiple sources
- [ ] Remove duplicates
- [ ] Format results for readability
- [ ] Cache frequently accessed knowledge
- [ ] Provide confidence scores for results

### 2. Knowledge Sources
- [ ] Local documentation/wiki
- [ ] Previously stored analysis results
- [ ] User context and history
- [ ] Domain-specific knowledge base (stocks, investment rules)
- [ ] Web search integration (optional)

### 3. Input/Output Format

**Input**: `ExpertRequest` containing:
```python
{
  "text": "What's the latest analysis on 600000.SH?",
  "user_id": "user_123",
  "context": {
    "previous_topics": ["stock_analysis", "technical_indicators"],
    "user_preferences": {...}
  },
  "extra_params": {
    "query": "600000.SH analysis",
    "knowledge_sources": ["local_docs", "analysis_cache"],  # Optional
    "top_k": 5,  # Number of results
    "min_confidence": 0.5  # Minimum confidence threshold
  }
}
```

**Output**: `ExpertResult` containing:
```python
{
  "expert_name": "KnowledgeExpert",
  "result": {
    "query": "600000.SH analysis",
    "total_sources_searched": 3,
    "results_found": 5,
    "knowledge_items": [
      {
        "source": "analysis_cache",
        "content": "Stock analysis results...",
        "relevance_score": 0.95,
        "confidence": 0.92,
        "last_updated": "2026-04-07",
        "metadata": {...}
      },
      # ... more results
    ],
    "summary": "Found 5 relevant knowledge items about 600000.SH",
    "recommendations": ["Check latest analysis", "Compare with peers"]
  },
  "confidence": 0.88
}
```

### 4. Implementation File

Create: `src/experts/knowledge_expert.py`

**Structure**:
```python
class KnowledgeExpert(Expert):
    name = "KnowledgeExpert"
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        # Query knowledge bases
        # Aggregate results
        # Rank by relevance
        # Return formatted response
        pass
    
    def _query_local_docs(self, query: str):
        pass
    
    def _query_analysis_cache(self, query: str):
        pass
    
    def _rank_by_relevance(self, results, query):
        pass
    
    def _aggregate_results(self, results):
        pass
```

---

## 🧪 Testing Requirements

### File: `tests/unit/test_knowledge_expert.py`

**Minimum 15 test cases**:

1. [ ] Test initialization
2. [ ] Test query parsing
3. [ ] Test local docs search
4. [ ] Test relevance ranking
5. [ ] Test duplicate removal
6. [ ] Test result aggregation
7. [ ] Test cache operations
8. [ ] Test confidence scoring
9. [ ] Test with empty query
10. [ ] Test with multiple sources
11. [ ] Test with confidence threshold
12. [ ] Test timeout handling
13. [ ] Test error handling
14. [ ] Test empty results
15. [ ] Test result formatting

---

## 📝 Documentation Requirements

### Create new files:
- `docs/knowledge_expert.md` - KnowledgeExpert usage guide
- `docs/knowledge_sources.md` - Available knowledge sources

### Update files:
- `docs/architecture.md` - Add KnowledgeExpert to architecture
- `docs/api.md` - Add KnowledgeExpert endpoints

---

## 🎯 Success Criteria

- [x] Code compiles without errors
- [x] All 15+ tests pass
- [x] Code follows PEP 8
- [x] 100% function documentation
- [x] 100% type hints
- [x] Integrates with MOEOrchestrator
- [x] Handles all error cases
- [x] Performance < 1000ms for typical queries

---

## 🔧 Technical Considerations

### 1. Query Processing
- Natural language query understanding
- Named entity extraction (stock symbols, dates)
- Query expansion for synonyms
- Context awareness from user history

### 2. Relevance Scoring
- TF-IDF or similar similarity metric
- Recency weighting (newer information scores higher)
- Domain relevance (domain-specific keywords)
- Popularity/citation count

### 3. Knowledge Base Integration
- Local file system for documentation
- In-memory cache for recent analyses
- Structured metadata for each knowledge item
- Version tracking for updates

### 4. Result Aggregation
- Combine results from multiple sources
- Remove exact duplicates (same content)
- Remove near-duplicates (similar content)
- Maintain source attribution
- Preserve confidence scores

---

## 📊 Deliverables

```
src/experts/knowledge_expert.py              (~400 lines)
tests/unit/test_knowledge_expert.py          (~300 lines)
docs/knowledge_expert.md                     (~150 lines)
Updated docs/architecture.md                 (add KnowledgeExpert)
Updated docs/api.md                          (add examples)
```

---

## 🚀 Implementation Tips

1. **Start with mock knowledge base** - Use simple in-memory data structures
2. **Implement search first** - Before ranking
3. **Add relevance scoring** - Use simple string matching initially
4. **Test incrementally** - Add tests as you implement features
5. **Cache results** - For performance improvement

---

## 🔗 Reference

Look at `StockAnalysisExpert` for patterns:
- Proper Expert class inheritance
- ExpertRequest/ExpertResult usage
- Error handling patterns
- Test structure

---

## 📋 Integration Checklist

After implementation:

1. [ ] Test with MOEOrchestrator
2. [ ] Run full test suite
3. [ ] Check coverage (target 70%+)
4. [ ] Verify integration with StockAnalysisExpert
5. [ ] Update architecture docs

---

**Start now. No need to wait for approval. Full steam ahead!** 🚀

*Sprint 2 starts immediately after Sprint 1 completion*
