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
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from pydantic import BaseModel

from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult

logger = logging.getLogger(__name__)


class KnowledgeItem(BaseModel):
    """知识项数据模型"""
    source: str
    content: str
    title: str = ""
    confidence: float = 0.0


class KnowledgeExpert(Expert):
    """知识专家 - 集成向量数据库的语义搜索"""
    
    def __init__(self):
        """初始化知识专家"""
        super().__init__(name="KnowledgeExpert", version="2.0")
        self._knowledge_base = self._initialize_knowledge_base()
        self._vector_db = None  # 延迟初始化 Chroma
        self.logger.info("KnowledgeExpert v2.0 initialized")
    
    def get_supported_tasks(self) -> List[str]:
        """返回支持的任务类型"""
        return ["knowledge_retrieval", "semantic_search", "qa"]
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        主要知识检索方法
        
        Args:
            request: 包含查询文本的请求
        
        Returns:
            知识检索结果
        """
        start_time = time.time()
        
        try:
            query = request.text or request.extra_params.get("query", "")
            
            if not query:
                return self._error_result(start_time, "查询文本不能为空")
            
            self.logger.info(f"知识查询: {query[:100]}")
            
            # 首先尝试向量数据库搜索
            results = await self._semantic_search(query)
            
            # 如果向量搜索失败，使用关键词搜索
            if not results:
                results = self._keyword_search(query)
            
            # 合成答案
            if results:
                answer = self._synthesize_answer(results, query)
                confidence = self._calculate_confidence(results)
            else:
                answer = f"抱歉，我在知识库中没有找到关于'{query}'的相关信息。"
                confidence = 0.0
            
            result_data = {
                "query": query,
                "answer": answer,
                "sources": [r.get("source", "Unknown") for r in results[:3]],
                "confidence": confidence,
                "result_count": len(results)
            }
            
            return ExpertResult(
                status="success",
                data=result_data,
                confidence=confidence,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.logger.error(f"知识检索失败: {str(e)}")
            return self._error_result(start_time, f"检索错误: {str(e)}")
    
    async def _semantic_search(self, query: str) -> List[Dict]:
        """
        向量数据库语义搜索
        
        使用 Chroma 进行相似度搜索
        """
        try:
            # 延迟初始化 Chroma
            if self._vector_db is None:
                from chromadb import Client
                self._vector_db = Client()
                self._initialize_vector_db()
            
            # 执行相似度搜索
            collection = self._vector_db.get_or_create_collection("knowledge")
            results = collection.query(
                query_texts=[query],
                n_results=5
            )
            
            if results and results["ids"] and len(results["ids"]) > 0:
                # 格式化结果
                docs = []
                for i, doc_id in enumerate(results["ids"][0]):
                    docs.append({
                        "id": doc_id,
                        "content": results["documents"][0][i] if results["documents"] else "",
                        "distance": results["distances"][0][i] if results["distances"] else 0,
                        "source": f"Vector DB - {doc_id}"
                    })
                
                self.logger.info(f"向量搜索找到 {len(docs)} 个结果")
                return docs
                
        except ImportError:
            self.logger.warning("Chroma 未安装，使用关键词搜索")
        except Exception as e:
            self.logger.warning(f"向量搜索失败: {str(e)}")
        
        return []
    
    def _initialize_vector_db(self):
        """初始化向量数据库并加载文档"""
        try:
            collection = self._vector_db.get_or_create_collection("knowledge")
            
            # 添加知识库文档
            documents = []
            ids = []
            
            for doc_id, doc_data in self._knowledge_base.items():
                documents.append(doc_data["content"])
                ids.append(doc_id)
            
            # 添加到 Chroma
            if documents:
                collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=[{"source": self._knowledge_base[id]["source"]} for id in ids]
                )
                
                self.logger.info(f"加载 {len(documents)} 个文档到向量数据库")
                
        except Exception as e:
            self.logger.warning(f"向量数据库初始化失败: {str(e)}")
    
    def _keyword_search(self, query: str) -> List[Dict]:
        """关键词搜索（向量数据库不可用时的备选）"""
        results = []
        query_lower = query.lower()
        
        for doc_id, doc_data in self._knowledge_base.items():
            content_lower = doc_data["content"].lower()
            title_lower = doc_data["title"].lower()
            
            # 计算匹配度
            score = 0
            if query_lower in title_lower:
                score += 3
            
            words = query_lower.split()
            for word in words:
                if len(word) > 2 and word in content_lower:
                    score += 1
            
            if score > 0:
                results.append({
                    "id": doc_id,
                    "content": doc_data["content"],
                    "title": doc_data["title"],
                    "score": score,
                    "source": doc_data["source"]
                })
        
        # 按得分排序
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:5]
    
    def _synthesize_answer(self, results: List[Dict], query: str) -> str:
        """合成答案"""
        if not results:
            return f"关于'{query}'的信息暂时不可用。"
        
        # 使用第一个（最相关的）结果
        best_result = results[0]
        content = best_result.get("content", "")
        title = best_result.get("title", "")
        
        # 生成答案
        if len(content) > 200:
            answer = content[:200] + "..."
        else:
            answer = content
        
        return f"根据知识库中的'{title}'：{answer}"
    
    def _calculate_confidence(self, results: List[Dict]) -> float:
        """计算置信度"""
        if not results:
            return 0.0
        
        # 基于最佳结果的相关性
        best_result = results[0]
        
        # 向量搜索的距离
        if "distance" in best_result:
            distance = best_result["distance"]
            confidence = max(0.0, 1.0 - distance)
        # 关键词搜索的得分
        elif "score" in best_result:
            score = best_result["score"]
            confidence = min(0.95, score / 3.0)
        else:
            confidence = 0.5
        
        return confidence
    
    def _initialize_knowledge_base(self) -> Dict[str, Dict]:
        """初始化知识库"""
        return {
            "doc_001": {
                "title": "股票投资基础",
                "content": "股票投资是长期财富积累的重要方式。投资前应了解基本概念、风险管理原则和常见的交易策略。",
                "source": "Knowledge Base"
            },
            "doc_002": {
                "title": "技术分析指标",
                "content": "常见技术分析指标包括移动平均(MA)、相对强度指数(RSI)、MACD和布林带等。这些指标帮助识别趋势和买卖点。",
                "source": "Knowledge Base"
            },
            "doc_003": {
                "title": "风险管理",
                "content": "风险管理是投资成功的关键。包括止损设置、头寸管理、资产配置和多元化投资等策略。",
                "source": "Knowledge Base"
            },
            "doc_004": {
                "title": "市场心理学",
                "content": "市场参与者的情绪和心理因素影响股价波动。理解市场心理有助于做出更理性的投资决策。",
                "source": "Knowledge Base"
            },
            "doc_005": {
                "title": "投资组合构建",
                "content": "成功的投资组合应该根据风险承受能力和投资目标进行多元化配置。定期调整和再平衡很重要。",
                "source": "Knowledge Base"
            }
        }
    
    def _error_result(self, start_time: float, error_msg: str) -> ExpertResult:
        """返回错误结果"""
        return ExpertResult(
            status="error",
            data={"error": error_msg},
            confidence=0.0,
            execution_time=time.time() - start_time
        )
