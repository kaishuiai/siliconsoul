"""
Unit tests for DialogExpert

Tests:
- Intent recognition
- Sentiment detection
- Context management
- Response generation
- Confidence calculation
"""

import pytest

from src.experts.dialog_expert import DialogExpert
from src.models.request_response import ExpertRequest


@pytest.fixture
def dialog_expert() -> DialogExpert:
    """Create DialogExpert instance"""
    return DialogExpert()


@pytest.fixture
def dialog_request() -> ExpertRequest:
    """Create request for dialogue"""
    return ExpertRequest(
        text="Hi, how are you doing?",
        user_id="user_123",
        context={"conversation_id": "conv_1"}
    )


class TestDialogExpertInitialization:
    """Tests for expert initialization"""
    
    def test_initialization(self, dialog_expert):
        """Test expert initialization"""
        assert dialog_expert.name == "DialogExpert"
        assert dialog_expert.version == "1.0"
    
    def test_intent_patterns_initialized(self, dialog_expert):
        """Test intent patterns are initialized"""
        assert dialog_expert.intent_patterns is not None
        assert "greeting" in dialog_expert.intent_patterns
        assert "question" in dialog_expert.intent_patterns
    
    def test_supported_tasks(self, dialog_expert):
        """Test supported tasks"""
        tasks = dialog_expert.get_supported_tasks()
        assert "dialog_generation" in tasks
        assert "intent_recognition" in tasks
        assert "context_management" in tasks
        assert "emotion_detection" in tasks


class TestIntentRecognition:
    """Tests for intent recognition"""
    
    def test_recognize_greeting(self, dialog_expert):
        """Test recognition of greeting"""
        intent = dialog_expert._recognize_intent("hello there")
        assert intent == "greeting"
    
    def test_recognize_question(self, dialog_expert):
        """Test recognition of question"""
        # "what" is in question patterns
        intent = dialog_expert._recognize_intent("what about that")
        assert intent == "question"
    
    def test_recognize_request(self, dialog_expert):
        """Test recognition of request"""
        intent = dialog_expert._recognize_intent("please help me")
        assert intent == "request"
    
    def test_recognize_statement(self, dialog_expert):
        """Test recognition of statement"""
        intent = dialog_expert._recognize_intent("i think this is good")
        assert intent in ["statement", "greeting", "other"]
    
    def test_recognize_other(self, dialog_expert):
        """Test recognition of other"""
        intent = dialog_expert._recognize_intent("xyz abc def")
        assert intent == "other"


class TestSentimentDetection:
    """Tests for sentiment detection"""
    
    def test_detect_positive_sentiment(self, dialog_expert):
        """Test positive sentiment detection"""
        sentiment, emotion = dialog_expert._detect_sentiment("this is great and awesome")
        assert sentiment == "positive"
        assert emotion == "happy"
    
    def test_detect_negative_sentiment(self, dialog_expert):
        """Test negative sentiment detection"""
        sentiment, emotion = dialog_expert._detect_sentiment("this is terrible and awful")
        assert sentiment == "negative"
        assert emotion == "sad"
    
    def test_detect_neutral_sentiment(self, dialog_expert):
        """Test neutral sentiment detection"""
        sentiment, emotion = dialog_expert._detect_sentiment("this is okay")
        assert sentiment == "neutral"
        assert emotion == "neutral"
    
    def test_sentiment_structure(self, dialog_expert):
        """Test sentiment detection returns tuple"""
        result = dialog_expert._detect_sentiment("hello")
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestContextManagement:
    """Tests for context management"""
    
    def test_context_creation(self, dialog_expert):
        """Test context creation for new user"""
        context = dialog_expert._manage_context("new_user", "hello", "greeting")
        
        assert "turn" in context
        assert "topics" in context
        assert "history" in context
        assert context["turn"] == 1
    
    def test_context_turn_increment(self, dialog_expert):
        """Test context turn increment"""
        user_id = "test_user"
        
        dialog_expert._manage_context(user_id, "first message", "greeting")
        context = dialog_expert._manage_context(user_id, "second message", "question")
        
        assert context["turn"] == 2
    
    def test_context_history(self, dialog_expert):
        """Test context tracks history"""
        user_id = "test_user"
        
        dialog_expert._manage_context(user_id, "hello", "greeting")
        context = dialog_expert._manage_context(user_id, "how are you?", "question")
        
        assert len(context["history"]) == 2
        assert "hello" in context["history"]


class TestResponseGeneration:
    """Tests for response generation"""
    
    def test_response_is_string(self, dialog_expert):
        """Test response is string"""
        response = dialog_expert._generate_response(
            "hello",
            "greeting",
            "neutral",
            {"turn": 1, "topics": [], "history": []}
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_response_different_for_different_intents(self, dialog_expert):
        """Test responses differ by intent"""
        context = {"turn": 1, "topics": [], "history": []}
        
        greeting_response = dialog_expert._generate_response("hi", "greeting", "neutral", context)
        question_response = dialog_expert._generate_response("what?", "question", "neutral", context)
        
        assert greeting_response != question_response
    
    def test_response_sentiment_adjustment(self, dialog_expert):
        """Test response adjusts for sentiment"""
        context = {"turn": 1, "topics": [], "history": []}
        
        positive_response = dialog_expert._generate_response("great!", "statement", "positive", context)
        negative_response = dialog_expert._generate_response("bad!", "statement", "negative", context)
        
        assert len(positive_response) > 0
        assert len(negative_response) > 0


class TestConfidenceCalculation:
    """Tests for confidence calculation"""
    
    def test_confidence_in_range(self, dialog_expert):
        """Test confidence is in valid range"""
        confidence = dialog_expert._calculate_confidence("greeting", "neutral")
        assert 0 <= confidence <= 1.0
    
    def test_confidence_higher_for_recognized_intent(self, dialog_expert):
        """Test confidence is higher for recognized intents"""
        recognized = dialog_expert._calculate_confidence("greeting", "neutral")
        unrecognized = dialog_expert._calculate_confidence("other", "neutral")
        
        assert recognized > unrecognized
    
    def test_confidence_with_sentiment(self, dialog_expert):
        """Test confidence changes with sentiment"""
        neutral_conf = dialog_expert._calculate_confidence("question", "neutral")
        positive_conf = dialog_expert._calculate_confidence("question", "positive")
        
        assert positive_conf > neutral_conf


class TestResponseStrategy:
    """Tests for response strategy"""
    
    def test_strategy_for_greeting(self, dialog_expert):
        """Test strategy for greeting"""
        strategy = dialog_expert._get_response_strategy("greeting")
        assert strategy == "friendly_acknowledgment"
    
    def test_strategy_for_question(self, dialog_expert):
        """Test strategy for question"""
        strategy = dialog_expert._get_response_strategy("question")
        assert strategy == "informative_answer"
    
    def test_strategy_for_request(self, dialog_expert):
        """Test strategy for request"""
        strategy = dialog_expert._get_response_strategy("request")
        assert strategy == "helpful_action"


class TestTopicExtraction:
    """Tests for topic extraction"""
    
    def test_extract_topics(self, dialog_expert):
        """Test topic extraction"""
        topics = dialog_expert._extract_topics("tell me about machine learning and AI")
        
        assert isinstance(topics, list)
        assert len(topics) <= 3
        # Should contain longer words
        assert all(len(topic) > 0 for topic in topics)
    
    def test_extract_empty_topics(self, dialog_expert):
        """Test with minimal text"""
        topics = dialog_expert._extract_topics("a b c")
        assert isinstance(topics, list)


class TestEntityExtraction:
    """Tests for entity extraction"""
    
    def test_extract_entities(self, dialog_expert):
        """Test entity extraction"""
        entities = dialog_expert._extract_entities("John and Alice went to Paris")
        
        assert isinstance(entities, list)
        assert len(entities) <= 3
    
    def test_extract_no_entities(self, dialog_expert):
        """Test with no entities"""
        entities = dialog_expert._extract_entities("the cat sat on the mat")
        # lowercase words shouldn't be extracted
        assert isinstance(entities, list)


class TestFollowUpGeneration:
    """Tests for follow-up generation"""
    
    def test_follow_ups_for_greeting(self, dialog_expert):
        """Test follow-ups for greeting"""
        follow_ups = dialog_expert._generate_follow_ups("greeting", {"turn": 1})
        
        assert isinstance(follow_ups, list)
        assert len(follow_ups) > 0
    
    def test_follow_ups_for_question(self, dialog_expert):
        """Test follow-ups for question"""
        follow_ups = dialog_expert._generate_follow_ups("question", {"turn": 1})
        
        assert isinstance(follow_ups, list)
        assert len(follow_ups) > 0


@pytest.mark.asyncio
async def test_full_dialog(dialog_expert, dialog_request):
    """Test complete dialogue"""
    result = await dialog_expert.execute(dialog_request)
    
    assert result.expert_name == "DialogExpert"
    assert 0 <= result.confidence <= 1.0
    assert not result.error
    
    # Check result structure
    assert "user_message" in result.result
    assert "intent" in result.result
    assert "sentiment" in result.result
    assert "response" in result.result


@pytest.mark.asyncio
async def test_dialog_different_inputs(dialog_expert):
    """Test dialogue with different inputs"""
    inputs = [
        "hello there",
        "what is AI?",
        "can you help?",
        "I think this is great"
    ]
    
    for input_text in inputs:
        request = ExpertRequest(text=input_text, user_id="user1")
        result = await dialog_expert.execute(request)
        
        assert result.expert_name == "DialogExpert"
        assert not result.error
        assert len(result.result) > 0


@pytest.mark.asyncio
async def test_performance_stats_update(dialog_expert, dialog_request):
    """Test that performance stats are updated"""
    initial_stats = dialog_expert.get_performance_stats()
    initial_count = initial_stats["call_count"]
    
    await dialog_expert.execute(dialog_request)
    
    updated_stats = dialog_expert.get_performance_stats()
    assert updated_stats["call_count"] == initial_count + 1
