"""
ML Expert 单元测试

测试机器学习预测和异常检测
"""

import pytest
import numpy as np
from src.experts.ml_expert import MLExpert
from src.models.request_response import ExpertRequest


class TestMLExpertInit:
    """初始化测试"""
    
    def test_init(self):
        """测试 ML 专家初始化"""
        expert = MLExpert()
        assert expert.name == "MLExpert"
        assert expert.version == "1.0"
    
    def test_get_supported_tasks(self):
        """测试支持的任务类型"""
        expert = MLExpert()
        tasks = expert.get_supported_tasks()
        
        assert "price_prediction" in tasks
        assert "anomaly_detection" in tasks
        assert "risk_scoring" in tasks
        assert "sentiment_analysis" in tasks


class TestFeatureEngineering:
    """特征工程测试"""
    
    def test_engineer_features(self):
        """测试特征工程"""
        expert = MLExpert()
        
        # 生成测试数据
        prices = [10.0, 10.1, 10.2, 10.15, 10.3, 10.25, 10.4, 10.5, 10.45, 10.6]
        
        features = expert._engineer_features(prices)
        
        # 验证特征
        assert 'returns' in features
        assert 'ma5' in features
        assert 'volatility_5' in features
        assert 'trend' in features
        
        # 验证特征长度
        assert len(features['returns']) > 0
        assert len(features['ma5']) > 0


class TestPricePrediction:
    """价格预测测试"""
    
    @pytest.mark.asyncio
    async def test_price_prediction_uptrend(self):
        """测试上升趋势预测"""
        expert = MLExpert()
        
        # 生成上升趋势数据
        prices = np.linspace(10.0, 12.0, 20).tolist()
        
        request = ExpertRequest(
            user_id="test_user",
            text="price_prediction",
            extra_params={"task": "price_prediction", "prices": prices}
        )
        
        result = await expert.analyze(request)
        
        assert result.error is None
        data = result.result
        assert "predicted_price" in data
        assert data["direction"] == "上升"
    
    @pytest.mark.asyncio
    async def test_price_prediction_downtrend(self):
        """测试下降趋势预测"""
        expert = MLExpert()
        
        # 生成下降趋势数据
        prices = np.linspace(12.0, 10.0, 20).tolist()
        
        request = ExpertRequest(
            user_id="test_user",
            text="price_prediction",
            extra_params={"task": "price_prediction", "prices": prices}
        )
        
        result = await expert.analyze(request)
        
        assert result.error is None
        data = result.result
        assert data["direction"] == "下降"
    
    @pytest.mark.asyncio
    async def test_price_prediction_insufficient_data(self):
        """测试数据不足"""
        expert = MLExpert()
        
        prices = [10.0, 10.1, 10.2]  # 少于 10 个数据点
        
        request = ExpertRequest(
            user_id="test_user",
            text="price_prediction",
            extra_params={"task": "price_prediction", "prices": prices}
        )
        
        result = await expert.analyze(request)
        
        assert result.error is not None


class TestAnomalyDetection:
    """异常检测测试"""
    
    @pytest.mark.asyncio
    async def test_anomaly_detection(self):
        """测试异常检测"""
        expert = MLExpert()
        
        # 生成数据带异常跳跃
        prices = [10.0] * 10 + [15.0] + [10.0] * 9  # 在第 11 个位置有大跳跃
        
        request = ExpertRequest(
            user_id="test_user",
            text="anomaly_detection",
            extra_params={"task": "anomaly_detection", "prices": prices}
        )
        
        result = await expert.analyze(request)
        
        assert result.error is None
        data = result.result
        assert "return_anomalies" in data
        assert len(data["return_anomalies"]) > 0
    
    @pytest.mark.asyncio
    async def test_no_anomalies(self):
        """测试无异常情况"""
        expert = MLExpert()
        
        # 生成平稳数据
        prices = np.linspace(10.0, 10.5, 20).tolist()
        
        request = ExpertRequest(
            user_id="test_user",
            text="anomaly_detection",
            extra_params={"task": "anomaly_detection", "prices": prices}
        )
        
        result = await expert.analyze(request)
        
        assert result.error is None


class TestRiskScoring:
    """风险评分测试"""
    
    @pytest.mark.asyncio
    async def test_risk_scoring_low_volatility(self):
        """测试低波动风险评分"""
        expert = MLExpert()
        
        # 低波动数据
        prices = np.linspace(10.0, 10.1, 20).tolist()
        
        request = ExpertRequest(
            user_id="test_user",
            text="risk_scoring",
            extra_params={"task": "risk_scoring", "prices": prices}
        )
        
        result = await expert.analyze(request)
        
        assert result.error is None
        data = result.result
        assert "risk_score" in data
        assert "risk_level" in data
        assert data["risk_score"] < 50  # 应该是低-中风险
    
    @pytest.mark.asyncio
    async def test_risk_scoring_high_volatility(self):
        """测试高波动风险评分"""
        expert = MLExpert()
        
        # 高波动数据
        prices = [9.0, 11.0, 8.5, 12.0, 8.0, 12.5, 8.5, 11.5, 9.0, 12.0] * 2
        
        request = ExpertRequest(
            user_id="test_user",
            text="risk_scoring",
            extra_params={"task": "risk_scoring", "prices": prices}
        )
        
        result = await expert.analyze(request)
        
        assert result.error is None
        data = result.result
        assert data["risk_score"] > 50  # 应该是中-高风险


class TestSentimentAnalysis:
    """情感分析测试"""
    
    @pytest.mark.asyncio
    async def test_sentiment_bullish(self):
        """测试看涨情感"""
        expert = MLExpert()
        
        # 上升趋势数据
        prices = np.linspace(10.0, 12.0, 20).tolist()
        
        request = ExpertRequest(
            user_id="test_user",
            text="sentiment_analysis",
            extra_params={"task": "sentiment_analysis", "prices": prices}
        )
        
        result = await expert.analyze(request)
        
        assert result.error is None
        data = result.result
        assert data["sentiment"] in ["看涨", "极度看涨"]
    
    @pytest.mark.asyncio
    async def test_sentiment_bearish(self):
        """测试看跌情感"""
        expert = MLExpert()
        
        # 下降趋势数据
        prices = np.linspace(12.0, 10.0, 20).tolist()
        
        request = ExpertRequest(
            user_id="test_user",
            text="sentiment_analysis",
            extra_params={"task": "sentiment_analysis", "prices": prices}
        )
        
        result = await expert.analyze(request)
        
        assert result.error is None
        data = result.result
        assert data["sentiment"] in ["看跌", "极度看跌"]


class TestMovingAverage:
    """移动平均测试"""
    
    def test_moving_average(self):
        """测试移动平均计算"""
        expert = MLExpert()
        
        prices = [10.0, 11.0, 12.0, 13.0, 14.0]
        mas = expert._moving_average(prices, 2)
        
        assert len(mas) == len(prices)
        # 第二个值应该是前两个的平均
        assert mas[1] == 10.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
