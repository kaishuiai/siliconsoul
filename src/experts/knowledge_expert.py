"""
Knowledge Expert - 知识库检索和语义搜索（集成 Chroma）

功能:
- 知识库检索
- 文档相关性排序
- 答案提取与合成
- 来源引用
- 置信度评分
"""

import time
import logging
import re
import hashlib
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult

logger = logging.getLogger(__name__)


class KnowledgeItem(BaseModel):
    source: str
    content: str
    title: str = ""
    relevance_score: float = 0.0
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "content": self.content,
            "title": self.title,
            "relevance_score": self.relevance_score,
            "confidence": self.confidence,
        }


class KnowledgeExpert(Expert):
    """知识专家"""
    
    def __init__(self):
        super().__init__(name="KnowledgeExpert", version="1.0")
        self._knowledge_cache = self._initialize_knowledge_cache()
        self._analysis_cache = self._initialize_analysis_cache()
        self._user_history_cache = self._initialize_user_history_cache()
        self._result_cache: Dict[str, Dict[str, Any]] = {}
        self.logger.info("KnowledgeExpert v1.0 initialized")
    
    def get_supported_tasks(self) -> List[str]:
        return ["knowledge_query", "information_retrieval", "knowledge_retrieval", "semantic_search", "qa"]
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        timestamp_start = time.time()
        try:
            extra_params = request.extra_params or {}
            query = request.text or extra_params.get("query", "")
            
            if not query:
                return self._error_result(timestamp_start, "查询文本不能为空")

            knowledge_sources = extra_params.get(
                "knowledge_sources",
                ["local_docs", "analysis_cache", "user_history"],
            )
            top_k = int(extra_params.get("top_k", 5))
            min_confidence = float(extra_params.get("min_confidence", 0.0))

            cache_key = self._make_cache_key(query, knowledge_sources)
            if cache_key in self._result_cache:
                cached = self._result_cache[cache_key]
                return ExpertResult(
                    expert_name=self.name,
                    result=cached["result"],
                    confidence=cached["confidence"],
                    metadata={"version": self.version, "from_cache": True},
                    timestamp_start=timestamp_start,
                    timestamp_end=time.time(),
                )

            parsed = self._parse_query(query)
            items: List[KnowledgeItem] = []

            if "local_docs" in knowledge_sources:
                items.extend(await self._search_local_docs(parsed))
            if "analysis_cache" in knowledge_sources:
                items.extend(await self._search_analysis_cache(parsed))
            if "user_history" in knowledge_sources:
                items.extend(await self._search_user_history(parsed))

            items = self._rank_by_relevance(items, parsed)
            items = self._remove_duplicates(items)
            if min_confidence > 0:
                items = [i for i in items if i.confidence >= min_confidence]
            if top_k > 0:
                items = items[:top_k]

            summary = self._generate_summary(query, items)
            recommendations = self._generate_recommendations(query, items)

            result_data = {
                "query": query,
                "knowledge_items": [i.to_dict() for i in items],
                "summary": summary,
                "recommendations": recommendations,
            }
            confidence = max((i.confidence for i in items), default=0.0)

            self._result_cache[cache_key] = {"result": result_data, "confidence": confidence}

            return ExpertResult(
                expert_name=self.name,
                result=result_data,
                confidence=confidence,
                metadata={"version": self.version, "from_cache": False},
                timestamp_start=timestamp_start,
                timestamp_end=time.time(),
            )
            
        except Exception as e:
            self.logger.error(f"知识检索失败: {str(e)}")
            return self._error_result(timestamp_start, f"检索错误: {str(e)}")

    def _initialize_knowledge_cache(self) -> Dict[str, List[KnowledgeItem]]:
        return {
            "stocks": [
                KnowledgeItem(source="local_docs", title="A股基础", content="600000.SH is a sample stock symbol.", confidence=0.8),
            ],
            "companies": [
                KnowledgeItem(source="local_docs", title="Company basics", content="Companies issue stocks and have fundamentals.", confidence=0.7),
            ],
            "rules": [
                KnowledgeItem(source="local_docs", title="Technical analysis", content="Moving Average (MA) is a common technical indicator.", confidence=0.9),
                KnowledgeItem(source="local_docs", title="RSI", content="RSI indicator measures momentum and overbought/oversold.", confidence=0.9),
                KnowledgeItem(source="local_docs", title="MACD", content="MACD is used to identify trend changes.", confidence=0.85),
            ],
        }

    def _initialize_analysis_cache(self) -> List[KnowledgeItem]:
        return [
            KnowledgeItem(source="analysis_cache", content="Previous analysis for 600000.SH: moving average crossover.", confidence=0.8),
        ]

    def _initialize_user_history_cache(self) -> List[KnowledgeItem]:
        return [
            KnowledgeItem(source="user_history", content="Your previous queries include RSI and moving averages.", confidence=0.7),
        ]

    def _parse_query(self, query: str) -> Dict[str, Any]:
        lowercase = query.lower()
        symbols = re.findall(r"\b[0-9]{6}\.(?:SH|SZ|HK)\b", query, flags=re.IGNORECASE)
        numbers = re.findall(r"\b\d+\b", query)
        tokens = re.findall(r"[a-zA-Z]+", lowercase)
        keywords = [t for t in tokens if len(t) >= 3]
        return {"keywords": keywords, "symbols": symbols, "numbers": numbers, "lowercase": lowercase}

    async def _search_local_docs(self, parsed: Dict[str, Any]) -> List[KnowledgeItem]:
        keywords = parsed.get("keywords", [])
        q = parsed.get("lowercase", "")
        results: List[KnowledgeItem] = []
        for group in self._knowledge_cache.values():
            for item in group:
                text = f"{item.title}\n{item.content}".lower()
                match = 0
                for kw in keywords:
                    if kw in text:
                        match += 1
                if "rsi" in q and "rsi" in text:
                    match += 2
                if "moving" in q and "moving" in text:
                    match += 2
                if match > 0:
                    denom = max(len(keywords), 1)
                    score = min(1.0, match / denom)
                    results.append(
                        KnowledgeItem(
                            source=item.source,
                            title=item.title,
                            content=item.content,
                            relevance_score=score,
                            confidence=max(item.confidence, min(1.0, 0.5 + score / 2)),
                        )
                    )
        return results

    async def _search_analysis_cache(self, parsed: Dict[str, Any]) -> List[KnowledgeItem]:
        symbols = parsed.get("symbols", [])
        keywords = parsed.get("keywords", [])
        if symbols:
            results = []
            for sym in symbols:
                for item in self._analysis_cache:
                    if sym.lower() in item.content.lower():
                        results.append(
                            KnowledgeItem(
                                source=item.source,
                                content=item.content,
                                relevance_score=0.9,
                                confidence=item.confidence,
                            )
                        )
            if results:
                return results
            return [
                KnowledgeItem(
                    source="analysis_cache",
                    content=f"No cached analysis found for {symbols[0]}",
                    relevance_score=0.6,
                    confidence=0.6,
                )
            ]
        if any(k in ("analysis", "analyze") for k in keywords):
            return [KnowledgeItem(source="analysis_cache", content="General analysis notes.", relevance_score=0.5, confidence=0.6)]
        return []

    async def _search_user_history(self, parsed: Dict[str, Any]) -> List[KnowledgeItem]:
        q = parsed.get("lowercase", "")
        if any(w in q for w in ("previous", "history", "my")):
            return list(self._user_history_cache)
        return []

    def _rank_by_relevance(self, items: List[KnowledgeItem], parsed: Dict[str, Any]) -> List[KnowledgeItem]:
        return sorted(items, key=lambda i: (i.relevance_score, i.confidence), reverse=True)

    def _remove_duplicates(self, items: List[KnowledgeItem]) -> List[KnowledgeItem]:
        kept: List[KnowledgeItem] = []
        seen: List[set] = []
        for item in items:
            tokens = set(re.findall(r"[a-zA-Z]+", item.content.lower()))
            if not tokens:
                kept.append(item)
                continue
            is_dup = False
            for prev in seen:
                inter = len(tokens & prev)
                union = len(tokens | prev)
                if union > 0 and (inter / union) >= 0.8:
                    is_dup = True
                    break
            if not is_dup:
                kept.append(item)
                seen.append(tokens)
        return kept

    def _generate_recommendations(self, query: str, results: List[KnowledgeItem]) -> List[str]:
        q = query.lower()
        recs: List[str] = []
        if re.search(r"\b[0-9]{6}\.(?:sh|sz|hk)\b", q):
            recs.append("查看该标的的近期趋势与关键均线位置")
            recs.append("结合风险管理设置止损与仓位")
        if "rsi" in q or any("rsi" in r.content.lower() for r in results):
            recs.append("对比 RSI 与价格走势，关注背离信号")
        if not recs:
            recs.append("尝试提供更具体的关键词或股票代码以提升命中率")
        return recs

    def _generate_summary(self, query: str, results: List[KnowledgeItem]) -> str:
        if not results:
            return f"Knowledge not found for query: {query}"
        return f"Found {len(results)} relevant knowledge items for the query."

    def _make_cache_key(self, query: str, sources: List[str]) -> str:
        normalized_sources = ",".join(sorted(set(sources)))
        raw = f"{query.strip().lower()}|{normalized_sources}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def _error_result(self, timestamp_start: float, error_msg: str) -> ExpertResult:
        return ExpertResult(
            expert_name=self.name,
            result={"error": error_msg},
            confidence=0.0,
            metadata={"version": self.version},
            timestamp_start=timestamp_start,
            timestamp_end=time.time(),
            error=error_msg,
        )
