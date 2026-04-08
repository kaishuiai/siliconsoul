# Implementation Guide for CC - StockAnalysisExpert Sprint 1

**Date**: 2026-04-07  
**Sprint**: 1 (Stock Analysis Expert)  
**Developer**: CC

---

## 🏗️ Framework Architecture Reference

### Expert Base Class Pattern

All experts must follow this pattern:

```python
from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult

class YourExpert(Expert):
    def __init__(self):
        super().__init__(name="YourExpert", version="1.0")
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        Main analysis method.
        Must return ExpertResult with standardized format.
        """
        try:
            # Your logic here
            result_data = await self._do_analysis(request)
            return ExpertResult(
                expert_name=self.name,
                task_id=request.task_id,
                status="success",
                result=result_data
            )
        except Exception as e:
            return ExpertResult(
                expert_name=self.name,
                task_id=request.task_id,
                status="error",
                error_message=str(e)
            )
    
    def get_supported_tasks(self) -> List[str]:
        """Declare what task types this expert handles."""
        return ["stock_analysis"]
```

### Request/Response Models

**ExpertRequest** fields:
```python
text: str                    # Main input text
user_id: str                # User ID
context: Optional[str]      # Background context
task_type: Optional[str]    # Pre-classified type
timestamp: datetime         # Auto-set
extra_params: Dict[str, Any]  # Extensible data
```

**ExpertResult** structure:
```python
{
    "expert_name": "StockAnalysisExpert",
    "task_id": "uuid-string",
    "status": "success|error|timeout",
    "result": {
        # Your analysis data here
    },
    "error_message": "Only if status=error",
    "metadata": {
        "response_time_ms": 123,
        "model_version": "1.0"
    }
}
```

---

## 📊 StockAnalysisExpert Detailed Design

### Input Format
```python
ExpertRequest with:
- text: "分析600000.SH" or "Analyze 600000.SH"
- extra_params: {
    "symbol": "600000.SH",
    "start_date": "2026-01-01",
    "end_date": "2026-04-07",
    "indicators": ["MA", "RSI", "MACD"],  # Optional
    "period_days": 30  # Optional, default 60
  }
```

### Output Format
```python
{
    "symbol": "600000.SH",
    "name": "浦发银行",
    "current_price": 10.25,
    "current_date": "2026-04-07",
    
    "trend": "uptrend|downtrend|sideways",
    "trend_strength": 0.0-1.0,
    
    "indicators": {
        "MA": {
            "MA5": 10.20,
            "MA10": 10.18,
            "MA20": 10.15,
            "MA50": 10.10,
            "position": "above_ma20"  # Price position relative to MA
        },
        "RSI": {
            "value": 65,
            "status": "overbought|normal|oversold"
        },
        "MACD": {
            "MACD": 0.15,
            "Signal": 0.12,
            "Histogram": 0.03,
            "status": "bullish|bearish"
        },
        "Bollinger": {
            "upper": 10.50,
            "middle": 10.25,
            "lower": 10.00,
            "position": "middle"
        }
    },
    
    "support_resistance": {
        "resistance_1": 10.40,
        "support_1": 10.10,
        "resistance_2": 10.60,
        "support_2": 9.90
    },
    
    "signal": "BUY|HOLD|SELL",
    "confidence": 0.75,
    
    "analysis": "Text explanation of analysis and recommendation",
    
    "price_history": [
        {"date": "2026-04-07", "open": 10.20, "high": 10.30, "low": 10.15, "close": 10.25, "volume": 5000000},
        # ... more dates
    ]
}
```

---

## 💻 Implementation Pseudocode

```python
class StockAnalysisExpert(Expert):
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """Main entry point."""
        try:
            # Parse request
            symbol = request.extra_params.get("symbol", "600000.SH")
            start_date = request.extra_params.get("start_date")
            end_date = request.extra_params.get("end_date")
            
            # Load price data
            prices = await self._load_price_data(symbol, start_date, end_date)
            
            # Calculate indicators
            indicators = {
                "MA": self._calculate_ma(prices),
                "RSI": self._calculate_rsi(prices),
                "MACD": self._calculate_macd(prices),
                "Bollinger": self._calculate_bollinger(prices)
            }
            
            # Detect support/resistance
            support_resistance = self._detect_levels(prices)
            
            # Generate trend
            trend = self._analyze_trend(prices, indicators)
            
            # Generate signal
            signal = self._generate_signal(indicators, trend, prices[-1])
            
            # Build result
            result = {
                "symbol": symbol,
                "current_price": prices[-1]["close"],
                "trend": trend["direction"],
                "indicators": indicators,
                "support_resistance": support_resistance,
                "signal": signal["action"],
                "confidence": signal["confidence"],
                "analysis": signal["explanation"]
            }
            
            return ExpertResult(
                expert_name=self.name,
                task_id=request.task_id,
                status="success",
                result=result
            )
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return ExpertResult(
                expert_name=self.name,
                task_id=request.task_id,
                status="error",
                error_message=str(e)
            )
    
    async def _load_price_data(self, symbol, start_date, end_date):
        """Load price data from source (mock/CSV/Tushare)."""
        # Option 1: Mock data (recommended for testing)
        return self._generate_mock_data(symbol)
        
        # Option 2: Load from CSV
        # return self._load_from_csv(symbol)
        
        # Option 3: Query Tushare
        # return await self._query_tushare(symbol, start_date, end_date)
    
    def _generate_mock_data(self, symbol):
        """Generate realistic mock stock data for testing."""
        import random
        from datetime import datetime, timedelta
        
        base_price = 10.25
        data = []
        
        for i in range(60):  # 60 days
            date = datetime.now() - timedelta(days=60-i)
            # Generate realistic OHLC
            close = base_price + random.uniform(-0.5, 0.5)
            open_price = close + random.uniform(-0.2, 0.2)
            high = max(open_price, close) + abs(random.uniform(0, 0.3))
            low = min(open_price, close) - abs(random.uniform(0, 0.3))
            volume = random.randint(2000000, 10000000)
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "volume": volume
            })
            
            base_price = close
        
        return data
    
    def _calculate_ma(self, prices):
        """Calculate Moving Averages."""
        closes = [p["close"] for p in prices]
        return {
            "MA5": self._sma(closes, 5),
            "MA10": self._sma(closes, 10),
            "MA20": self._sma(closes, 20),
            "MA50": self._sma(closes, 50)
        }
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index."""
        # ... RSI calculation
        pass
    
    def _calculate_macd(self, prices):
        """Calculate MACD."""
        # ... MACD calculation
        pass
    
    def _sma(self, values, period):
        """Simple Moving Average."""
        if len(values) < period:
            return None
        return sum(values[-period:]) / period
    
    def _generate_signal(self, indicators, trend, current_bar):
        """Generate BUY/HOLD/SELL signal."""
        # Combine indicators
        signal_score = 0
        
        # RSI signal
        rsi = indicators["RSI"]["value"]
        if rsi < 30:
            signal_score += 2  # Buy signal
        elif rsi > 70:
            signal_score -= 2  # Sell signal
        
        # MACD signal
        if indicators["MACD"]["Histogram"] > 0:
            signal_score += 1
        else:
            signal_score -= 1
        
        # Trend signal
        if trend == "uptrend":
            signal_score += 1
        elif trend == "downtrend":
            signal_score -= 1
        
        # Determine action
        if signal_score >= 2:
            action = "BUY"
            confidence = min(0.9, 0.6 + abs(signal_score) * 0.1)
        elif signal_score <= -2:
            action = "SELL"
            confidence = min(0.9, 0.6 + abs(signal_score) * 0.1)
        else:
            action = "HOLD"
            confidence = 0.5
        
        return {
            "action": action,
            "confidence": confidence,
            "explanation": f"Based on RSI={rsi}, MACD histogram, trend analysis"
        }
```

---

## 🧪 Testing Template

```python
# tests/unit/test_stock_analysis_expert.py

import pytest
from src.experts.stock_analysis_expert import StockAnalysisExpert
from src.models.request_response import ExpertRequest

@pytest.fixture
def expert():
    return StockAnalysisExpert()

@pytest.mark.asyncio
async def test_initialization():
    """Test expert can be initialized."""
    expert = StockAnalysisExpert()
    assert expert.name == "StockAnalysisExpert"
    assert expert.version == "1.0"

@pytest.mark.asyncio
async def test_analyze_with_mock_data(expert):
    """Test analysis with mock data."""
    request = ExpertRequest(
        text="Analyze 600000.SH",
        user_id="test_user",
        task_type="stock_analysis",
        extra_params={"symbol": "600000.SH"}
    )
    result = await expert.analyze(request)
    
    assert result.status == "success"
    assert result.result["signal"] in ["BUY", "HOLD", "SELL"]
    assert 0 <= result.result["confidence"] <= 1

@pytest.mark.asyncio
async def test_ma_calculation(expert):
    """Test MA calculation."""
    prices = [10.0, 10.1, 10.2, 10.3, 10.4, 10.5]
    ma = expert._calculate_ma([{"close": p} for p in prices])
    assert ma["MA5"] is not None

@pytest.mark.asyncio
async def test_error_handling(expert):
    """Test error handling."""
    request = ExpertRequest(
        text="Invalid",
        user_id="test",
        extra_params={"symbol": ""}
    )
    result = await expert.analyze(request)
    # Should handle gracefully
```

---

## 🚀 Development Checklist

- [ ] Create `src/experts/stock_analysis_expert.py`
- [ ] Implement `__init__` and `analyze` methods
- [ ] Implement all helper methods (MA, RSI, MACD, etc.)
- [ ] Create `tests/unit/test_stock_analysis_expert.py`
- [ ] Add 10+ test cases
- [ ] Run tests: `pytest tests/unit/test_stock_analysis_expert.py -v`
- [ ] Run coverage: `pytest --cov=src tests/`
- [ ] Update `docs/api.md`
- [ ] Update `docs/architecture.md`
- [ ] Run integration test with MOEOrchestrator
- [ ] Verify no regression in existing tests

---

## 📂 File Structure

```
siliconsoul-moe/
├── src/
│   └── experts/
│       ├── expert_base.py          (already exists)
│       ├── demo_expert_1.py        (reference)
│       ├── demo_expert_2.py        (reference)
│       ├── demo_expert_3.py        (reference)
│       └── stock_analysis_expert.py    ← CREATE THIS
├── tests/
│   └── unit/
│       ├── test_expert_base.py
│       └── test_stock_analysis_expert.py    ← CREATE THIS
├── docs/
│   ├── architecture.md    ← UPDATE
│   ├── api.md            ← UPDATE
│   └── stock_analysis.md ← CREATE NEW
└── requirements.txt
```

---

## 🎯 Success Metrics

✅ All tests pass  
✅ No test regressions  
✅ 100% type hints  
✅ 100% docstrings  
✅ < 500ms per analysis  
✅ Handles all error cases  
✅ Ready for integration with other 5 experts  

---

**Start implementing now. No interruptions. Full steam ahead!** 🚀

