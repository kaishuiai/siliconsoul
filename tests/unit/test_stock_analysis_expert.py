"""
Unit tests for StockAnalysisExpert - Updated for new ExpertResult model
"""

import pytest
from datetime import datetime, timedelta
from src.experts.stock_analysis_expert import StockAnalysisExpert
from src.models.request_response import ExpertRequest, ExpertResult


@pytest.fixture
def expert():
    """Create a fresh StockAnalysisExpert for each test."""
    return StockAnalysisExpert()


@pytest.fixture
def basic_request():
    """Create a basic stock analysis request."""
    return ExpertRequest(
        text="Analyze 600000.SH",
        user_id="test_user"
    )


class TestStockAnalysisExpertInitialization:
    """Tests for expert initialization."""
    
    def test_expert_initializes_with_correct_name(self, expert):
        """Test that expert is initialized with correct name."""
        assert expert.name == "StockAnalysisExpert"
        assert expert.version == "1.0"
    
    def test_expert_has_supported_tasks(self, expert):
        """Test that expert declares supported task types."""
        supported = expert.get_supported_tasks()
        assert "stock_analysis" in supported
        assert "technical_analysis" in supported
    
    def test_supported_indicators_list(self, expert):
        """Test that supported indicators are properly defined."""
        assert "MA" in expert._supported_indicators
        assert "RSI" in expert._supported_indicators
        assert "MACD" in expert._supported_indicators
        assert "Bollinger" in expert._supported_indicators


class TestMovingAverage:
    """Tests for MA calculation."""
    
    def test_ma_calculation_5_day(self, expert):
        """Test 5-day moving average calculation."""
        prices = [10.0, 10.1, 10.2, 10.3, 10.4, 10.5]
        result = expert._calculate_ma(prices)
        
        assert result["MA5"] is not None
        assert abs(result["MA5"] - 10.3) < 0.01
    
    def test_ma_calculation_insufficient_data(self, expert):
        """Test MA with insufficient data."""
        prices = [10.0, 10.1, 10.2]
        result = expert._calculate_ma(prices)
        
        assert result["MA5"] is None
        assert result["MA10"] is None
    
    def test_ma_position_above_ma20(self, expert):
        """Test price position detection (above MA20)."""
        prices = [10.0 + (i * 0.01) for i in range(30)]
        result = expert._calculate_ma(prices)
        
        assert result["position"] == "above_ma20"
    
    def test_sma_calculation(self, expert):
        """Test simple moving average helper method."""
        values = [10, 20, 30, 40, 50]
        sma = expert._sma(values, 3)
        
        assert sma == 40


class TestRelativeStrengthIndex:
    """Tests for RSI calculation."""
    
    def test_rsi_calculation_valid(self, expert):
        """Test RSI calculation with valid data."""
        prices = [10.0 + (i * 0.01) for i in range(30)]
        result = expert._calculate_rsi(prices)
        
        assert result["value"] is not None
        assert 0 <= result["value"] <= 100
        assert result["status"] in ["oversold", "normal", "overbought", "insufficient_data"]
    
    def test_rsi_insufficient_data(self, expert):
        """Test RSI with insufficient data."""
        prices = [10.0, 10.1, 10.2]
        result = expert._calculate_rsi(prices)
        
        assert result["status"] == "insufficient_data"


class TestMACD:
    """Tests for MACD calculation."""
    
    def test_macd_calculation_valid(self, expert):
        """Test MACD calculation with valid data."""
        prices = [10.0 + (i * 0.01) for i in range(30)]
        result = expert._calculate_macd(prices)
        
        assert result["MACD"] is not None or result["status"] == "insufficient_data"
        assert result["Signal"] is not None or result["status"] == "insufficient_data"
        assert result["Histogram"] is not None or result["status"] == "insufficient_data"
    
    def test_macd_insufficient_data(self, expert):
        """Test MACD with insufficient data."""
        prices = [10.0, 10.1, 10.2]
        result = expert._calculate_macd(prices)
        
        assert result["status"] == "insufficient_data"


class TestBollingerBands:
    """Tests for Bollinger Bands calculation."""
    
    def test_bollinger_calculation_valid(self, expert):
        """Test Bollinger Bands calculation."""
        prices = [10.0 + (i * 0.01) for i in range(30)]
        result = expert._calculate_bollinger(prices)
        
        assert result["upper"] is not None
        assert result["middle"] is not None
        assert result["lower"] is not None
        assert result["upper"] > result["middle"] > result["lower"]
    
    def test_bollinger_insufficient_data(self, expert):
        """Test Bollinger Bands with insufficient data."""
        prices = [10.0, 10.1, 10.2]
        result = expert._calculate_bollinger(prices)
        
        assert result["position"] == "insufficient_data"


class TestTrendAnalysis:
    """Tests for trend analysis."""
    
    def test_trend_analysis_uptrend(self, expert):
        """Test uptrend detection."""
        prices = [10.0 + (i * 0.05) for i in range(30)]
        indicators = expert._calculate_ma(prices)
        trend = expert._analyze_trend(prices, indicators)
        
        assert trend["direction"] in ["uptrend", "sideways", "insufficient_data"]
        assert 0 <= trend["strength"] <= 1
    
    def test_trend_analysis_downtrend(self, expert):
        """Test downtrend detection."""
        prices = [10.0 - (i * 0.05) for i in range(30)]
        indicators = expert._calculate_ma(prices)
        trend = expert._analyze_trend(prices, indicators)
        
        assert trend["direction"] in ["downtrend", "sideways", "insufficient_data"]
        assert 0 <= trend["strength"] <= 1


class TestSupportResistance:
    """Tests for support and resistance detection."""
    
    def test_support_resistance_detection(self, expert):
        """Test support/resistance level detection."""
        prices = [10.0 + (i * 0.01) for i in range(30)]
        levels = expert._detect_support_resistance(prices)
        
        assert "resistance_1" in levels
        assert "support_1" in levels
        assert levels["resistance_1"] >= levels["support_1"]


class TestSignalGeneration:
    """Tests for trading signal generation."""
    
    def test_signal_generation_basic(self, expert):
        """Test basic signal generation."""
        prices = [10.0 + (i * 0.01) for i in range(30)]
        indicators = {
            "MA": expert._calculate_ma(prices),
            "RSI": expert._calculate_rsi(prices),
            "MACD": expert._calculate_macd(prices),
            "Bollinger": expert._calculate_bollinger(prices)
        }
        trend = expert._analyze_trend(prices, indicators)
        levels = expert._detect_support_resistance(prices)
        
        signal = expert._generate_signal(indicators, trend, prices[-1], levels)
        
        assert signal["action"] in ["BUY", "HOLD", "SELL"]
        assert 0 <= signal["confidence"] <= 1
        assert isinstance(signal["explanation"], str)


class TestMockDataGeneration:
    """Tests for mock data generation."""
    
    def test_mock_data_generation(self, expert):
        """Test mock price data generation."""
        data = expert._generate_mock_data("600000.SH", 60)
        
        assert len(data) == 60
        assert all("date" in d for d in data)
        assert all("open" in d for d in data)
        assert all("close" in d for d in data)
    
    def test_mock_data_ohlc_validity(self, expert):
        """Test OHLC relationships in mock data."""
        data = expert._generate_mock_data("600000.SH", 30)
        
        for day in data:
            assert day["low"] <= day["open"] or day["low"] <= day["close"]
            assert day["high"] >= day["open"] or day["high"] >= day["close"]


class TestAnalyzeMethod:
    """Tests for main analyze method."""
    
    @pytest.mark.asyncio
    async def test_analyze_with_valid_request(self, expert, basic_request):
        """Test analyze with valid request."""
        result = await expert.analyze(basic_request)
        
        assert isinstance(result, ExpertResult)
        assert result.expert_name == "StockAnalysisExpert"
        assert result.result is not None
        assert result.confidence is not None
    
    @pytest.mark.asyncio
    async def test_analyze_result_contains_required_fields(self, expert):
        """Test that result contains all required analysis fields."""
        request = ExpertRequest(
            text="Analyze 600000.SH",
            user_id="test_user",
            extra_params={"symbol": "600000.SH"}
        )
        result = await expert.analyze(request)
        
        if result.error is None:
            result_data = result.result
            assert "symbol" in result_data
            assert "current_price" in result_data
            assert "trend" in result_data
            assert "signal" in result_data
    
    @pytest.mark.asyncio
    async def test_analyze_with_multiple_indicators(self, expert):
        """Test analyze with specific indicators requested."""
        request = ExpertRequest(
            text="Analyze 600000.SH with MA and RSI",
            user_id="test_user",
            extra_params={
                "symbol": "600000.SH",
                "indicators": ["MA", "RSI"]
            }
        )
        
        result = await expert.analyze(request)
        
        if result.error is None:
            assert "indicators" in result.result
    
    @pytest.mark.asyncio
    async def test_analyze_signal_is_valid(self, expert):
        """Test that generated signal is always valid."""
        request = ExpertRequest(
            text="Analyze 600000.SH",
            user_id="test_user"
        )
        result = await expert.analyze(request)
        
        if result.error is None:
            signal = result.result.get("signal")
            assert signal in ["BUY", "HOLD", "SELL"]
            
            confidence = result.result.get("confidence")
            assert 0 <= confidence <= 1
    
    @pytest.mark.asyncio
    async def test_expert_result_has_timestamps(self, expert):
        """Test that result has proper timing information."""
        request = ExpertRequest(
            text="Analyze 600000.SH",
            user_id="test_user"
        )
        result = await expert.analyze(request)
        
        assert result.timestamp_start > 0
        assert result.timestamp_end > 0
        assert result.timestamp_end >= result.timestamp_start


class TestErrorHandling:
    """Tests for error handling and edge cases."""
    
    def test_get_stock_name_known_symbol(self, expert):
        """Test stock name lookup for known symbol."""
        name = expert._get_stock_name("600000.SH")
        assert name == "浦发银行"
    
    def test_get_stock_name_unknown_symbol(self, expert):
        """Test stock name lookup for unknown symbol."""
        name = expert._get_stock_name("999999.XX")
        assert name == "999999.XX"
    
    @pytest.mark.asyncio
    async def test_load_price_data_fallback(self, expert):
        """Test price data loading with fallback to mock."""
        data = await expert._load_price_data("600000.SH", 60)
        
        assert data is not None
        assert len(data) > 0
        assert "close" in data[0]


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_analysis_pipeline(self, expert):
        """Test complete analysis pipeline."""
        request = ExpertRequest(
            text="Full analysis of 600000.SH",
            user_id="test_user_full",
            extra_params={
                "symbol": "600000.SH",
                "period_days": 60,
                "indicators": ["MA", "RSI", "MACD", "Bollinger"]
            }
        )
        
        result = await expert.analyze(request)
        
        assert result.expert_name == "StockAnalysisExpert"
        result_data = result.result
        
        # Check all components are present
        assert "symbol" in result_data
        assert "indicators" in result_data
        assert "MA" in result_data["indicators"]
        assert "RSI" in result_data["indicators"]


class TestPerformance:
    """Performance tests."""
    
    @pytest.mark.asyncio
    async def test_analysis_response_time(self, expert):
        """Test that analysis completes within reasonable time."""
        request = ExpertRequest(
            text="Analyze 600000.SH",
            user_id="test_user_perf"
        )
        
        result = await expert.analyze(request)
        
        # Should complete in under 2 seconds
        duration = result.timestamp_end - result.timestamp_start
        assert duration < 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
