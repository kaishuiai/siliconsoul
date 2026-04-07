"""Unit tests for DialogExpert"""
import pytest
from src.experts.dialog_expert import DialogExpert
from src.models.request_response import ExpertRequest, ExpertResult

@pytest.fixture
def expert():
    return DialogExpert()

@pytest.fixture
def basic_request():
    return ExpertRequest(text="Analyze 600000.SH please", user_id="test_user")

class TestDialogExpertInitialization:
    def test_expert_name(self, expert):
        assert expert.name == "DialogExpert"
    
    def test_supported_tasks(self, expert):
        supported = expert.get_supported_tasks()
        assert "dialog" in supported

class TestIntentClassification:
    def test_classify_intent_analyze(self, expert):
        intent, conf = expert._classify_intent("analyze 600000.SH")
        assert intent in expert._intents
        assert 0 <= conf <= 1.0
    
    def test_classify_intent_confidence(self, expert):
        intent, conf = expert._classify_intent("buy signal")
        assert conf > 0.3

class TestEntityExtraction:
    def test_extract_stock_symbols(self, expert):
        entities = expert._extract_entities("Check 600000.SH")
        assert "600000.SH" in entities.get("stock_symbols", [])
    
    def test_extract_indicators(self, expert):
        entities = expert._extract_entities("Check RSI and MACD")
        indicators = entities.get("indicators", [])
        assert len(indicators) > 0

class TestAnalyzeMethod:
    @pytest.mark.asyncio
    async def test_analyze_with_valid_input(self, expert, basic_request):
        result = await expert.analyze(basic_request)
        assert isinstance(result, ExpertResult)
        assert result.expert_name == "DialogExpert"
    
    @pytest.mark.asyncio
    async def test_analyze_returns_intent(self, expert):
        request = ExpertRequest(text="What should I do with my stocks?", user_id="test")
        result = await expert.analyze(request)
        assert "intent" in result.result
    
    @pytest.mark.asyncio
    async def test_analyze_returns_response(self, expert):
        request = ExpertRequest(text="Buy signal for Apple", user_id="test")
        result = await expert.analyze(request)
        assert "response" in result.result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
