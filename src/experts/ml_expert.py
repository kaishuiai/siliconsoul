"""
ML Expert - 机器学习预测和异常检测专家

功能:
- 时间序列预测（LSTM）
- 异常检测
- 情感分析
- 风险评分
- 特征工程
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np

from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult

logger = logging.getLogger(__name__)


class MLExpert(Expert):
    """机器学习专家 - 预测和异常检测"""
    
    def __init__(self):
        """初始化 ML 专家"""
        super().__init__(name="MLExpert", version="1.0")
        self._models = {}
        self._scalers = {}
        self._features = {}
        self.logger.info("MLExpert initialized with prediction and anomaly detection")
    
    def get_supported_tasks(self) -> List[str]:
        """返回支持的任务类型"""
        return ["price_prediction", "anomaly_detection", "risk_scoring", "sentiment_analysis"]
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        主要 ML 分析方法
        
        Args:
            request: 包含价格数据和参数的请求
        
        Returns:
            预测或异常检测结果
        """
        start_time = time.time()
        
        try:
            extra_params = request.extra_params or {}
            task_type = extra_params.get("task", "price_prediction")
            prices = extra_params.get("prices", [])
            
            if not prices or len(prices) < 10:
                return self._error_result(start_time, "需要至少 10 个价格数据点")
            
            self.logger.info(f"执行 ML 任务: {task_type}")
            
            # 特征工程
            features = self._engineer_features(prices)
            
            # 根据任务类型选择处理方法
            if task_type == "price_prediction":
                result = self._predict_price(prices, features)
            elif task_type == "anomaly_detection":
                result = self._detect_anomalies(prices, features)
            elif task_type == "risk_scoring":
                result = self._calculate_risk_score(prices, features)
            elif task_type == "sentiment_analysis":
                result = self._analyze_sentiment(prices, features)
            else:
                result = self._predict_price(prices, features)
            
            return ExpertResult(
                status="success",
                data=result,
                confidence=result.get("confidence", 0.7),
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.logger.error(f"ML 分析失败: {str(e)}")
            return self._error_result(start_time, f"分析错误: {str(e)}")
    
    def _engineer_features(self, prices: List[float]) -> Dict[str, List[float]]:
        """
        特征工程
        
        Args:
            prices: 价格数据列表
        
        Returns:
            特征字典
        """
        prices = np.array(prices)
        n = len(prices)
        
        features = {}
        
        # 基础特征
        features['returns'] = np.diff(prices) / prices[:-1] * 100  # 日收益率 %
        features['log_returns'] = np.log(prices[1:] / prices[:-1]) * 100
        features['price_momentum'] = np.diff(prices)
        
        # 移动平均特征
        features['ma5'] = self._moving_average(prices, 5)
        features['ma10'] = self._moving_average(prices, 10)
        features['ma20'] = self._moving_average(prices, 20)
        
        # 波动率特征
        features['volatility_5'] = [np.std(prices[max(0,i-5):i+1]) for i in range(n)]
        features['volatility_20'] = [np.std(prices[max(0,i-20):i+1]) for i in range(n)]
        
        # 极值特征
        features['high_low_ratio'] = [
            max(prices[max(0,i-5):i+1]) / min(prices[max(0,i-5):i+1], default=1)
            for i in range(n)
        ]
        
        # 趋势特征
        features['trend'] = [
            1 if prices[i] > self._moving_average(prices[:i+1], min(5, i+1))[-1] else -1
            for i in range(n)
        ]
        
        return features
    
    def _predict_price(
        self, prices: List[float], features: Dict
    ) -> Dict[str, Any]:
        """
        价格预测（基于历史趋势的简单模型）
        
        Args:
            prices: 价格数据
            features: 特征数据
        
        Returns:
            预测结果
        """
        prices = np.array(prices)
        last_price = prices[-1]
        
        # 简单的移动平均预测
        ma5 = features['ma5'][-1] if len(features['ma5']) > 0 else last_price
        ma10 = features['ma10'][-1] if len(features['ma10']) > 0 else last_price
        ma20 = features['ma20'][-1] if len(features['ma20']) > 0 else last_price
        
        # 加权平均预测
        predicted_price = (ma5 * 0.5 + ma10 * 0.3 + ma20 * 0.2)
        
        # 计算改变百分比
        change_percent = (predicted_price - last_price) / last_price * 100
        
        # 计算置信度（基于一致性）
        ma_agreement = abs(ma5 - ma10) / ma10 < 0.02 and abs(ma10 - ma20) / ma20 < 0.02
        confidence = 0.8 if ma_agreement else 0.6
        
        return {
            "task": "price_prediction",
            "current_price": float(last_price),
            "predicted_price": float(predicted_price),
            "change_percent": float(change_percent),
            "direction": "上升" if change_percent > 0 else "下降",
            "confidence": confidence,
            "prediction_period": "下一交易日"
        }
    
    def _detect_anomalies(
        self, prices: List[float], features: Dict
    ) -> Dict[str, Any]:
        """
        异常检测（基于标准差的 3-sigma 规则）
        
        Args:
            prices: 价格数据
            features: 特征数据
        
        Returns:
            异常检测结果
        """
        prices = np.array(prices)
        returns = np.array(features['returns'])
        
        # 计算统计指标
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        # 检测极端值（3-sigma）
        anomalies = []
        threshold = 3 * std_return
        
        for i, ret in enumerate(returns):
            if abs(ret - mean_return) > threshold:
                anomalies.append({
                    "index": i,
                    "price": float(prices[i+1]),
                    "return": float(ret),
                    "z_score": float((ret - mean_return) / std_return)
                })
        
        # 检测 volatility 跳跃
        volatility = features['volatility_5']
        vol_mean = np.mean(volatility)
        vol_std = np.std(volatility)
        
        vol_anomalies = []
        for i, vol in enumerate(volatility):
            if abs(vol - vol_mean) > 2 * vol_std:
                vol_anomalies.append({
                    "index": i,
                    "volatility": float(vol),
                    "z_score": float((vol - vol_mean) / vol_std)
                })
        
        return {
            "task": "anomaly_detection",
            "return_anomalies": anomalies[:5],  # 前 5 个
            "volatility_anomalies": vol_anomalies[:5],
            "total_anomalies": len(anomalies) + len(vol_anomalies),
            "recommendation": "价格波动异常，建议谨慎操作" if len(anomalies) > 0 else "未检测到异常"
        }
    
    def _calculate_risk_score(
        self, prices: List[float], features: Dict
    ) -> Dict[str, Any]:
        """
        风险评分（0-100）
        
        Args:
            prices: 价格数据
            features: 特征数据
        
        Returns:
            风险评分结果
        """
        prices = np.array(prices)
        returns = np.array(features['returns'])
        
        # 计算各项风险指标
        volatility_score = min(100, np.std(returns) * 10)  # 波动率风险
        
        # 下行风险（负收益的标准差）
        negative_returns = returns[returns < 0]
        downside_risk = np.std(negative_returns) if len(negative_returns) > 0 else 0
        downside_score = min(100, downside_risk * 15)
        
        # 最大回撤
        cumsum = np.cumprod(1 + returns / 100)
        running_max = np.maximum.accumulate(cumsum)
        drawdown = (cumsum - running_max) / running_max * 100
        max_drawdown = abs(np.min(drawdown))
        max_drawdown_score = min(100, max_drawdown * 2)
        
        # 综合风险评分
        risk_score = (
            volatility_score * 0.4 +
            downside_score * 0.3 +
            max_drawdown_score * 0.3
        )
        
        # 风险等级
        if risk_score < 20:
            risk_level = "低风险"
        elif risk_score < 40:
            risk_level = "低-中风险"
        elif risk_score < 60:
            risk_level = "中风险"
        elif risk_score < 80:
            risk_level = "中-高风险"
        else:
            risk_level = "高风险"
        
        return {
            "task": "risk_scoring",
            "risk_score": float(risk_score),
            "risk_level": risk_level,
            "volatility_score": float(volatility_score),
            "downside_score": float(downside_score),
            "max_drawdown": float(max_drawdown),
            "recommendation": "建议降低仓位" if risk_score > 70 else "风险可控"
        }
    
    def _analyze_sentiment(
        self, prices: List[float], features: Dict
    ) -> Dict[str, Any]:
        """
        情感分析（基于价格动量和趋势）
        
        Args:
            prices: 价格数据
            features: 特征数据
        
        Returns:
            情感分析结果
        """
        prices = np.array(prices)
        returns = np.array(features['returns'])
        
        # 短期动量
        recent_returns = returns[-5:]
        momentum = np.mean(recent_returns)
        
        # 趋势
        trend = features['trend'][-1]
        
        # 成交量信号（模拟）
        price_range = np.max(prices) - np.min(prices)
        price_std = np.std(prices)
        volume_signal = price_std / (price_range / len(prices)) if price_range > 0 else 1
        
        # 综合情感评分
        sentiment_score = 50  # 初始中立
        
        # 加入动量
        if momentum > 0.5:
            sentiment_score += 20  # 正面
        elif momentum < -0.5:
            sentiment_score -= 20  # 负面
        
        # 加入趋势
        if trend > 0:
            sentiment_score += 10
        else:
            sentiment_score -= 10
        
        # 确保在 0-100 范围内
        sentiment_score = max(0, min(100, sentiment_score))
        
        # 情感判断
        if sentiment_score > 70:
            sentiment = "极度看涨"
        elif sentiment_score > 55:
            sentiment = "看涨"
        elif sentiment_score > 45:
            sentiment = "中立"
        elif sentiment_score > 30:
            sentiment = "看跌"
        else:
            sentiment = "极度看跌"
        
        return {
            "task": "sentiment_analysis",
            "sentiment_score": float(sentiment_score),
            "sentiment": sentiment,
            "momentum": float(momentum),
            "trend": "上升" if trend > 0 else "下降",
            "recommendation": "建议加仓" if sentiment_score > 70 else ("建议减仓" if sentiment_score < 30 else "观望")
        }
    
    def _moving_average(self, prices: List[float], period: int) -> List[float]:
        """计算移动平均"""
        prices = np.array(prices)
        if len(prices) < period:
            return [prices[-1]] * len(prices)
        
        mas = []
        for i in range(len(prices)):
            if i < period - 1:
                mas.append(np.mean(prices[:i+1]))
            else:
                mas.append(np.mean(prices[i-period+1:i+1]))
        
        return mas
    
    def _error_result(self, start_time: float, error_msg: str) -> ExpertResult:
        """返回错误结果"""
        return ExpertResult(
            status="error",
            data={"error": error_msg},
            confidence=0.0,
            execution_time=time.time() - start_time
        )
