"""
Dialog Expert - 自然语言理解和对话管理（集成 LLM）

功能:
- 意图分类
- 实体提取（股票、指标、时间框架）
- 上下文感知回复
- 多轮对话支持
- 自然语言生成（通过 LLM）
"""

import time
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import os

from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult

logger = logging.getLogger(__name__)


class DialogExpert(Expert):
    """自然语言对话专家 - 集成 LLM 生成自然回复"""
    
    def __init__(self):
        """初始化对话专家"""
        super().__init__(name="DialogExpert", version="2.0")
        self._intents = {
            "analyze_stock": ["分析", "查看", "检查", "研究", "查询"],
            "get_price": ["价格", "成本", "多少钱", "报价"],
            "technical_analysis": ["技术", "指标", "MA", "RSI", "MACD"],
            "buy_signal": ["买", "看涨", "上升", "多头"],
            "sell_signal": ["卖", "看跌", "下降", "空头"],
            "risk_management": ["风险", "止损", "头寸", "配置"],
            "portfolio": ["投资组合", "分散", "配置", "持仓"],
            "knowledge_query": ["什么", "如何", "解释", "告诉我"]
        }
        self._conversation_history = {}
        self._llm_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.logger.info("DialogExpert v2.0 initialized with LLM integration")
    
    def get_supported_tasks(self) -> List[str]:
        """返回支持的任务类型"""
        return ["dialog", "intent_classification", "entity_extraction"]
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        主要对话分析方法
        
        Args:
            request: 包含用户输入的请求
        
        Returns:
            对话结果
        """
        start_time = time.time()
        
        try:
            user_text = request.text or request.extra_params.get("text", "")
            user_id = request.user_id or "unknown"
            
            if not user_text:
                return self._error_result(start_time, "输入文本不能为空")
            
            self.logger.info(f"处理对话 用户: {user_id} 文本: {user_text[:50]}")
            
            # 分类意图
            intent = self._classify_intent(user_text)
            
            # 提取实体
            entities = self._extract_entities(user_text)
            
            # 获取或创建对话历史
            if user_id not in self._conversation_history:
                self._conversation_history[user_id] = []
            
            # 生成自然回复（使用 LLM）
            response = await self._generate_response(
                user_text, intent, entities, user_id
            )
            
            # 保存对话历史
            self._conversation_history[user_id].append({
                "timestamp": datetime.now().isoformat(),
                "user": user_text,
                "assistant": response,
                "intent": intent,
                "entities": entities
            })
            
            # 构建结果
            result_data = {
                "user_input": user_text,
                "response": response,
                "intent": intent,
                "entities": entities,
                "confidence": 0.85,
                "conversation_id": user_id
            }
            
            return ExpertResult(
                status="success",
                data=result_data,
                confidence=0.85,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.logger.error(f"对话处理失败: {str(e)}")
            return self._error_result(start_time, f"处理错误: {str(e)}")
    
    async def _generate_response(
        self, user_text: str, intent: str,
        entities: Dict, user_id: str
    ) -> str:
        """
        生成自然对话回复（优先使用 LLM，否则使用规则）
        
        Args:
            user_text: 用户输入
            intent: 分类的意图
            entities: 提取的实体
            user_id: 用户 ID
        
        Returns:
            自然语言回复
        """
        # 首先尝试使用 LLM
        llm_response = await self._call_llm(user_text, intent, entities)
        if llm_response:
            return llm_response
        
        # 备选：规则引擎生成回复
        return self._generate_rule_based_response(user_text, intent, entities)
    
    async def _call_llm(
        self, user_text: str, intent: str, entities: Dict
    ) -> Optional[str]:
        """
        调用 LLM API 生成自然回复
        
        支持的 LLM：
        - DeepSeek
        - Qwen
        - OpenAI 兼容接口
        """
        try:
            # 尝试 DeepSeek API
            if self._llm_api_key:
                return await self._call_deepseek(user_text, intent, entities)
            
            # 尝试通用 LLM 接口
            return await self._call_generic_llm(user_text, intent, entities)
            
        except Exception as e:
            self.logger.warning(f"LLM 调用失败: {str(e)}")
            return None
    
    async def _call_deepseek(
        self, user_text: str, intent: str, entities: Dict
    ) -> Optional[str]:
        """调用 DeepSeek API"""
        try:
            import aiohttp
            
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self._llm_api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建提示
            system_prompt = """你是一个专业的股票投资顾问。
用户提出的问题都与股票分析、投资决策有关。
请用中文回答，保持专业、友好的语气。
回答要简洁明了，控制在 100 字以内。"""
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        content = data["choices"][0]["message"]["content"]
                        self.logger.info(f"DeepSeek 成功生成回复")
                        return content
                    else:
                        self.logger.warning(f"DeepSeek API 返回 {resp.status}")
                        return None
                        
        except Exception as e:
            self.logger.warning(f"DeepSeek 调用失败: {str(e)}")
            return None
    
    async def _call_generic_llm(
        self, user_text: str, intent: str, entities: Dict
    ) -> Optional[str]:
        """调用通用 LLM 接口"""
        try:
            import aiohttp
            
            # 支持 OpenAI 兼容接口
            api_key = os.getenv("OPENAI_API_KEY", "")
            api_base = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
            
            if not api_key:
                return None
            
            url = f"{api_base}/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.7,
                "max_tokens": 150
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["choices"][0]["message"]["content"]
                        
        except Exception as e:
            self.logger.warning(f"LLM 调用失败: {str(e)}")
            
        return None
    
    def _generate_rule_based_response(
        self, user_text: str, intent: str, entities: Dict
    ) -> str:
        """
        规则引擎生成回复（LLM 不可用时的备选）
        """
        responses = {
            "analyze_stock": "我已收到您的股票分析请求。请告诉我具体分析哪只股票？",
            "get_price": "我正在查询最新价格。请指定您关注的股票代码。",
            "technical_analysis": "技术分析涉及多个指标，我建议关注 MA、RSI 和 MACD。",
            "buy_signal": "如果出现买入信号，我们需要结合风险管理策略进行决策。",
            "sell_signal": "售出决策应基于技术面和基本面的综合分析。",
            "risk_management": "风险管理是投资的关键。建议设定合理的止损位置。",
            "portfolio": "投资组合应该分散配置，降低单只股票的风险。",
            "knowledge_query": "很高兴为您解答。请告诉我您想了解哪方面的内容？",
        }
        
        return responses.get(intent, f"我理解您在询问关于{intent}的问题。我很乐意帮助您。")
    
    def _classify_intent(self, user_text: str) -> str:
        """分类用户意图"""
        user_text_lower = user_text.lower()
        
        best_intent = "knowledge_query"
        best_score = 0
        
        for intent, keywords in self._intents.items():
            score = sum(1 for kw in keywords if kw in user_text_lower)
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return best_intent
    
    def _extract_entities(self, user_text: str) -> Dict[str, List[str]]:
        """
        提取命名实体
        
        包括：
        - 股票代码（如 600000.SH）
        - 技术指标（MA, RSI, MACD）
        - 时间表达（今天、周、月）
        """
        entities = {
            "stocks": [],
            "indicators": [],
            "timeframes": []
        }
        
        # 提取股票代码
        stock_pattern = r'\b[0-9]{6}\.(SH|SZ|HK)\b'
        entities["stocks"] = re.findall(stock_pattern, user_text, re.IGNORECASE)
        
        # 提取技术指标
        indicators = ["MA", "RSI", "MACD", "布林带", "KDJ", "CCI"]
        for ind in indicators:
            if ind.lower() in user_text.lower():
                entities["indicators"].append(ind)
        
        # 提取时间表达
        timeframes = ["今天", "本周", "本月", "本年", "实时"]
        for tf in timeframes:
            if tf in user_text:
                entities["timeframes"].append(tf)
        
        return entities
    
    def _error_result(self, start_time: float, error_msg: str) -> ExpertResult:
        """返回错误结果"""
        return ExpertResult(
            status="error",
            data={"error": error_msg},
            confidence=0.0,
            execution_time=time.time() - start_time
        )
