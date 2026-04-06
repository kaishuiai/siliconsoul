"""
Dialog Expert - 对话专家

This expert handles natural language understanding and dialogue generation:
- Intent recognition from user input
- Context management and conversation history
- Response generation using dialogue strategies
- Multi-turn conversation support
- Emotion detection and sentiment analysis

The expert maintains conversation context and generates contextually
appropriate responses following conversation rules and best practices.

Supported Tasks:
- dialog_generation: Generate natural responses
- intent_recognition: Identify user intent
- context_management: Manage conversation context
- emotion_detection: Detect user emotions
- response_ranking: Rank candidate responses
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult


class DialogExpert(Expert):
    """
    Dialog Expert - Natural language dialogue and conversation management
    
    This expert handles multi-turn conversations with context awareness,
    intent recognition, and natural response generation.
    
    Features:
    - Intent classification (greeting, question, statement, request)
    - Sentiment and emotion detection
    - Context tracking across multiple turns
    - Response generation with various strategies
    - Conversation flow management
    
    Conversation Strategies:
    - Clarification: Ask for more details
    - Empathy: Show understanding
    - Information: Provide relevant info
    - Action: Suggest actions
    
    Example:
        >>> expert = DialogExpert()
        >>> request = ExpertRequest(
        ...     text="Hi, how are you?",
        ...     user_id="user_123",
        ...     context={"conversation_id": "conv_1"}
        ... )
        >>> result = await expert.execute(request)
    """
    
    def __init__(self):
        """Initialize Dialog Expert"""
        super().__init__(name="DialogExpert", version="1.0")
        
        # Intent patterns
        self.intent_patterns = {
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon"],
            "question": ["what", "how", "why", "when", "where", "who", "?"],
            "request": ["please", "can you", "could you", "would you", "help"],
            "statement": ["i think", "i believe", "i feel", "it seems"]
        }
        
        # Sentiment keywords
        self.positive_words = ["good", "great", "excellent", "happy", "love", "awesome"]
        self.negative_words = ["bad", "terrible", "sad", "hate", "angry", "awful"]
        
        # Conversation context
        self.conversation_memory = {}
        
        self.logger.info("DialogExpert initialized")
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        Analyze dialogue input and generate response.
        
        Args:
            request: ExpertRequest containing user message
        
        Returns:
            ExpertResult with dialogue response and analysis
        """
        timestamp_start = datetime.now().timestamp()
        
        try:
            text = request.text.lower()
            user_id = request.user_id
            
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            # Recognize intent
            intent = self._recognize_intent(text)
            
            # Detect sentiment
            sentiment, emotion = self._detect_sentiment(text)
            
            # Manage context
            context = self._manage_context(user_id, text, intent)
            
            # Generate response
            response = self._generate_response(text, intent, sentiment, context)
            
            # Rank and select response
            final_response = response
            confidence = self._calculate_confidence(intent, sentiment)
            
            # Build result
            analysis_result = {
                "user_message": request.text,
                "intent": intent,
                "sentiment": sentiment,
                "emotion": emotion,
                "response": final_response,
                "response_strategy": self._get_response_strategy(intent),
                "context": {
                    "conversation_turn": context.get("turn", 1),
                    "topics_mentioned": self._extract_topics(text),
                    "entities": self._extract_entities(text)
                },
                "confidence": round(confidence, 2),
                "follow_up_options": self._generate_follow_ups(intent, context)
            }
            
            timestamp_end = datetime.now().timestamp()
            
            return ExpertResult(
                expert_name=self.name,
                result=analysis_result,
                confidence=confidence,
                metadata={
                    "version": self.version,
                    "dialogue_strategy": "context_aware",
                    "timestamp": datetime.now().isoformat()
                },
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
            )
        
        except Exception as e:
            timestamp_end = datetime.now().timestamp()
            self.logger.error(f"Dialogue processing failed: {str(e)}", exc_info=True)
            
            return ExpertResult(
                expert_name=self.name,
                result={},
                confidence=0.0,
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
                error=f"Dialogue error: {str(e)}",
            )
    
    def _recognize_intent(self, text: str) -> str:
        """
        Recognize user intent from text.
        
        Args:
            text: User message (lowercase)
        
        Returns:
            Intent type: greeting, question, request, statement, other
        """
        for intent, keywords in self.intent_patterns.items():
            if any(keyword in text for keyword in keywords):
                return intent
        
        return "other"
    
    def _detect_sentiment(self, text: str) -> Tuple[str, str]:
        """
        Detect sentiment and emotion from text.
        
        Args:
            text: User message
        
        Returns:
            Tuple of (sentiment, emotion)
        """
        positive_count = sum(1 for word in self.positive_words if word in text)
        negative_count = sum(1 for word in self.negative_words if word in text)
        
        if positive_count > negative_count:
            sentiment = "positive"
            emotion = "happy"
        elif negative_count > positive_count:
            sentiment = "negative"
            emotion = "sad"
        else:
            sentiment = "neutral"
            emotion = "neutral"
        
        return sentiment, emotion
    
    def _manage_context(self, user_id: str, text: str, intent: str) -> Dict[str, Any]:
        """
        Manage conversation context.
        
        Args:
            user_id: User identifier
            text: Current message
            intent: Recognized intent
        
        Returns:
            Context dictionary
        """
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = {
                "turn": 0,
                "topics": [],
                "history": []
            }
        
        context = self.conversation_memory[user_id]
        context["turn"] += 1
        context["history"].append(text)
        
        return context
    
    def _generate_response(
        self,
        text: str,
        intent: str,
        sentiment: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate dialogue response.
        
        Args:
            text: User message
            intent: Recognized intent
            sentiment: User sentiment
            context: Conversation context
        
        Returns:
            Generated response
        """
        response_templates = {
            "greeting": "Hello! Nice to talk with you. How can I help?",
            "question": "That's a great question! Let me think about it...",
            "request": "I'd be happy to help! Here's what I can do...",
            "statement": "I understand what you mean. That makes sense.",
            "other": "Tell me more about that. I'm interested."
        }
        
        base_response = response_templates.get(intent, response_templates["other"])
        
        # Adjust tone based on sentiment
        if sentiment == "negative":
            base_response = "I understand your concern. " + base_response
        elif sentiment == "positive":
            base_response = "Great! " + base_response
        
        # Add context awareness
        if context["turn"] > 2:
            base_response += " (Based on our conversation so far)"
        
        return base_response
    
    def _calculate_confidence(self, intent: str, sentiment: str) -> float:
        """
        Calculate confidence in dialogue response.
        
        Args:
            intent: Recognized intent
            sentiment: Detected sentiment
        
        Returns:
            Confidence score 0-1
        """
        base_confidence = 0.75
        
        # Higher confidence for clear intents
        if intent != "other":
            base_confidence += 0.15
        
        # Slight boost for detected sentiment
        if sentiment != "neutral":
            base_confidence += 0.05
        
        return min(1.0, base_confidence)
    
    def _get_response_strategy(self, intent: str) -> str:
        """Get the dialogue strategy used"""
        strategies = {
            "greeting": "friendly_acknowledgment",
            "question": "informative_answer",
            "request": "helpful_action",
            "statement": "empathetic_response",
            "other": "exploratory"
        }
        return strategies.get(intent, "exploratory")
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics mentioned in text"""
        # Simple keyword extraction
        keywords = text.split()
        # Filter out short common words
        topics = [w for w in keywords if len(w) > 3]
        return topics[:3]  # Top 3 topics
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text"""
        # Simplified entity extraction
        entities = []
        
        # Look for capitalized words (potential proper nouns)
        words = text.split()
        for word in words:
            if word[0].isupper():
                entities.append(word)
        
        return entities[:3]
    
    def _generate_follow_ups(self, intent: str, context: Dict[str, Any]) -> List[str]:
        """
        Generate suggested follow-up questions/responses.
        
        Args:
            intent: Current intent
            context: Conversation context
        
        Returns:
            List of follow-up suggestions
        """
        follow_ups = {
            "greeting": [
                "What brings you here?",
                "How can I assist you?"
            ],
            "question": [
                "Would you like more details?",
                "Any other questions?"
            ],
            "request": [
                "Is there anything else?",
                "Would you like me to elaborate?"
            ],
            "statement": [
                "Tell me more about that",
                "How does that affect you?"
            ]
        }
        
        return follow_ups.get(intent, ["What else?", "Continue..."])
    
    def get_supported_tasks(self) -> List[str]:
        """
        Return supported task types.
        
        Returns:
            List of supported task types
        """
        return [
            "dialog_generation",
            "intent_recognition",
            "context_management",
            "emotion_detection",
            "response_ranking"
        ]
