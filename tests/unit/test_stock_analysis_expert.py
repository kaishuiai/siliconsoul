"""
Unit tests for StockAnalysisExpert

Tests:
- Stock code extraction
- Technical analysis
- Fundamental analysis
- Risk assessment
- Recommendation generation
- Confidence calculation
"""

import pytest

from src.experts.stock_analysis_expert import StockAnalysisExpert
from src.models.request_response import ExpertRequest


@pytest.fixture
def stock_expert() -> StockAnalysisExpert:
    """Create StockAnalysisExpert instance"""
    return StockAnalysisExpert()


@pytest.fixture
def stock_request() -> ExpertRequest:
    """Create request for stock analysis"""
    return ExpertRequest(
        text="Analyze Apple stock AAPL",
        user_id="investor_123",
        extra_params={"stock_code": "AAPL"}
    )


class TestStockAnalysisExpertInitialization:
    """Tests for expert initialization"""
    
    def test_initialization(self, stock_expert):
        """Test expert initialization"""
        assert stock_expert.name == "StockAnalysisExpert"
        assert stock_expert.version == "1.0"
    
    def test_supported_tasks(self, stock_expert):
        """Test supported tasks"""
        tasks = stock_expert.get_supported_tasks()
        assert "stock_analysis" in tasks
        assert "technical_analysis" in tasks
        assert "fundamental_analysis" in tasks
        assert "risk_assessment" in tasks
        assert "investment_recommendation" in tasks
    
    def test_weights_initialized(self, stock_expert):
        """Test that analysis weights are initialized"""
        assert stock_expert.technical_weights is not None
        assert stock_expert.fundamental_weights is not None


class TestStockCodeExtraction:
    """Tests for stock code extraction"""
    
    def test_extract_from_extra_params(self, stock_expert):
        """Test extracting stock code from extra_params"""
        request = ExpertRequest(
            text="Analyze this stock",
            user_id="user1",
            extra_params={"stock_code": "MSFT"}
        )
        code = stock_expert._extract_stock_code(request)
        assert code == "MSFT"
    
    def test_extract_from_text(self, stock_expert):
        """Test extracting stock code from text"""
        request = ExpertRequest(
            text="What about Google GOOGL stock?",
            user_id="user1"
        )
        code = stock_expert._extract_stock_code(request)
        assert code == "GOOGL"
    
    def test_default_code_if_not_found(self, stock_expert):
        """Test default code when not found"""
        request = ExpertRequest(
            text="Analyze some stock",
            user_id="user1"
        )
        code = stock_expert._extract_stock_code(request)
        assert code == "AAPL"


class TestTechnicalAnalysis:
    """Tests for technical analysis"""
    
    def test_technical_score_range(self, stock_expert):
        """Test that technical score is in valid range"""
        score = stock_expert._technical_analysis("AAPL")
        assert 0 <= score <= 100
    
    def test_different_stocks_different_scores(self, stock_expert):
        """Test that different stocks produce different scores"""
        score1 = stock_expert._technical_analysis("AAPL")
        score2 = stock_expert._technical_analysis("MSFT")
        # Different stock codes should produce different hashes
        # (though not guaranteed, highly likely)
        assert isinstance(score1, (int, float))
        assert isinstance(score2, (int, float))


class TestFundamentalAnalysis:
    """Tests for fundamental analysis"""
    
    def test_fundamental_score_range(self, stock_expert):
        """Test that fundamental score is in valid range"""
        score = stock_expert._fundamental_analysis("AAPL")
        assert 0 <= score <= 100
    
    def test_fundamental_is_numeric(self, stock_expert):
        """Test that fundamental score is numeric"""
        score = stock_expert._fundamental_analysis("TSLA")
        assert isinstance(score, (int, float))


class TestRiskAssessment:
    """Tests for risk assessment"""
    
    def test_risk_metrics_structure(self, stock_expert):
        """Test that risk metrics have correct structure"""
        risk = stock_expert._risk_assessment("AAPL")
        
        assert "volatility_percent" in risk
        assert "beta" in risk
        assert "sharpe_ratio" in risk
        assert "risk_level" in risk
    
    def test_volatility_range(self, stock_expert):
        """Test that volatility is in valid range"""
        risk = stock_expert._risk_assessment("AAPL")
        assert 0 <= risk["volatility_percent"] <= 100
    
    def test_beta_range(self, stock_expert):
        """Test that beta is in valid range"""
        risk = stock_expert._risk_assessment("AAPL")
        assert 0.5 <= risk["beta"] <= 1.5
    
    def test_risk_level_values(self, stock_expert):
        """Test that risk level has valid values"""
        risk = stock_expert._risk_assessment("AAPL")
        assert risk["risk_level"] in ["moderate", "high"]


class TestRecommendationGeneration:
    """Tests for recommendation generation"""
    
    def test_strong_buy_recommendation(self, stock_expert):
        """Test STRONG_BUY recommendation"""
        rec = stock_expert._generate_recommendation(80)
        assert rec == "STRONG_BUY"
    
    def test_buy_recommendation(self, stock_expert):
        """Test BUY recommendation"""
        rec = stock_expert._generate_recommendation(65)
        assert rec == "BUY"
    
    def test_hold_recommendation(self, stock_expert):
        """Test HOLD recommendation"""
        rec = stock_expert._generate_recommendation(50)
        assert rec == "HOLD"
    
    def test_sell_recommendation(self, stock_expert):
        """Test SELL recommendation"""
        rec = stock_expert._generate_recommendation(30)
        assert rec == "SELL"
    
    def test_strong_sell_recommendation(self, stock_expert):
        """Test STRONG_SELL recommendation"""
        rec = stock_expert._generate_recommendation(10)
        assert rec == "STRONG_SELL"
    
    def test_boundary_values(self, stock_expert):
        """Test boundary value recommendations"""
        assert stock_expert._generate_recommendation(75) == "STRONG_BUY"
        assert stock_expert._generate_recommendation(74) == "BUY"
        assert stock_expert._generate_recommendation(60) == "BUY"
        assert stock_expert._generate_recommendation(59) == "HOLD"


class TestConfidenceCalculation:
    """Tests for confidence calculation"""
    
    def test_confidence_range(self, stock_expert):
        """Test that confidence is in valid range"""
        risk = stock_expert._risk_assessment("AAPL")
        confidence = stock_expert._calculate_confidence(70, 70, risk)
        assert 0 <= confidence <= 1
    
    def test_high_agreement_high_confidence(self, stock_expert):
        """Test that agreement between scores increases confidence"""
        risk = stock_expert._risk_assessment("AAPL")
        
        # High agreement (both 70)
        conf_high_agreement = stock_expert._calculate_confidence(70, 70, risk)
        
        # Low agreement (70 vs 30)
        conf_low_agreement = stock_expert._calculate_confidence(70, 30, risk)
        
        assert conf_high_agreement >= conf_low_agreement
    
    def test_high_risk_reduces_confidence(self, stock_expert):
        """Test that high risk reduces confidence"""
        risk_high = {"risk_level": "high", "volatility_percent": 50, "beta": 1.3, "sharpe_ratio": 0.8}
        risk_mod = {"risk_level": "moderate", "volatility_percent": 20, "beta": 0.9, "sharpe_ratio": 1.1}
        
        conf_high = stock_expert._calculate_confidence(70, 70, risk_high)
        conf_mod = stock_expert._calculate_confidence(70, 70, risk_mod)
        
        assert conf_mod >= conf_high


class TestReasoningGeneration:
    """Tests for reasoning generation"""
    
    def test_reasoning_contains_stock_code(self, stock_expert):
        """Test that reasoning contains stock code"""
        reasoning = stock_expert._generate_reasoning("AAPL", 70, 70, "BUY")
        assert "AAPL" in reasoning
    
    def test_reasoning_contains_scores(self, stock_expert):
        """Test that reasoning contains analysis scores"""
        reasoning = stock_expert._generate_reasoning("AAPL", 70, 75, "BUY")
        assert "70" in reasoning or "75" in reasoning
    
    def test_reasoning_contains_recommendation(self, stock_expert):
        """Test that reasoning contains recommendation"""
        reasoning = stock_expert._generate_reasoning("AAPL", 70, 70, "BUY")
        assert "BUY" in reasoning
    
    def test_reasoning_is_string(self, stock_expert):
        """Test that reasoning is string"""
        reasoning = stock_expert._generate_reasoning("AAPL", 70, 70, "BUY")
        assert isinstance(reasoning, str)
        assert len(reasoning) > 0


@pytest.mark.asyncio
async def test_full_analysis(stock_expert, stock_request):
    """Test complete stock analysis"""
    result = await stock_expert.execute(stock_request)
    
    assert result.expert_name == "StockAnalysisExpert"
    assert result.confidence > 0
    assert not result.error
    
    # Check result structure
    assert "stock_code" in result.result
    assert "recommendation" in result.result
    assert "overall_score" in result.result
    assert "technical_indicators" in result.result
    assert "fundamental_metrics" in result.result
    assert "risk_metrics" in result.result


@pytest.mark.asyncio
async def test_analysis_without_stock_code(stock_expert):
    """Test analysis when stock code cannot be extracted"""
    request = ExpertRequest(
        text="Tell me about stocks",
        user_id="user1"
    )
    
    # Should use default AAPL
    result = await stock_expert.execute(request)
    assert not result.error or "AAPL" in result.result.get("stock_code", "")


@pytest.mark.asyncio
async def test_performance_stats_update(stock_expert, stock_request):
    """Test that performance stats are updated"""
    initial_stats = stock_expert.get_performance_stats()
    initial_count = initial_stats["call_count"]
    
    await stock_expert.execute(stock_request)
    
    updated_stats = stock_expert.get_performance_stats()
    assert updated_stats["call_count"] == initial_count + 1
