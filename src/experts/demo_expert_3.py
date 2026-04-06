"""
Demo Expert 3 - Sentiment/Tone Analysis

A demo expert that analyzes text sentiment and tone.
Demonstrates variable-speed execution.

Characteristics:
- Variable execution time (50-500ms depending on input)
- Confidence based on certainty of analysis
- Returns sentiment metrics
"""

import asyncio
import random
from datetime import datetime
from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult


class DemoExpert3(Expert):
    """
    Demo Expert 3: Sentiment/Tone Analysis Expert
    
    This expert demonstrates:
    - Variable execution time based on input characteristics
    - Probabilistic confidence scoring
    - More complex analysis logic
    - Random variation (simulating real ML models)
    
    Purpose: Testing with realistic variation and uncertainty
    
    Supported Tasks:
    - sentiment_analysis: Sentiment detection
    - tone_detection: Tone/mood analysis
    - emotion_detection: Emotional content analysis
    - demo: General demonstration
    """
    
    def __init__(self):
        """Initialize Demo Expert 3."""
        super().__init__(name="DemoExpert3", version="1.0")
        
        # Simple sentiment keywords for demo
        self.positive_keywords = {
            'good': 1.0, 'great': 1.0, 'excellent': 1.0,
            'love': 0.9, 'amazing': 0.95, 'fantastic': 0.95,
            'happy': 0.8, 'wonderful': 0.9, 'best': 1.0,
        }
        
        self.negative_keywords = {
            'bad': -1.0, 'terrible': -1.0, 'awful': -1.0,
            'hate': -0.9, 'worst': -1.0, 'horrible': -0.95,
            'sad': -0.8, 'poor': -0.7, 'wrong': -0.6,
        }
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        Analyze text sentiment and tone.
        
        Performs sentiment analysis including:
        - Positive/negative word detection
        - Sentiment score calculation
        - Tone classification
        - Confidence estimation
        
        Args:
            request: ExpertRequest with user input
        
        Returns:
            ExpertResult with sentiment analysis
        """
        timestamp_start = datetime.now().timestamp()
        
        try:
            text = request.text.lower()
            
            # Variable execution time (50-300ms)
            # Longer text takes longer
            exec_time = min(0.3, 0.05 + len(text) * 0.001)
            await asyncio.sleep(exec_time)
            
            # Detect sentiment words
            positive_score = 0.0
            negative_score = 0.0
            found_positive = 0
            found_negative = 0
            
            for word, score in self.positive_keywords.items():
                if word in text:
                    positive_score += score
                    found_positive += 1
            
            for word, score in self.negative_keywords.items():
                if word in text:
                    negative_score += abs(score)
                    found_negative += 1
            
            # Calculate overall sentiment
            total_score = positive_score - negative_score
            total_words_with_sentiment = found_positive + found_negative
            
            # Normalize sentiment (-1 to 1)
            if total_words_with_sentiment > 0:
                normalized_sentiment = total_score / max(total_words_with_sentiment, 1.0)
                normalized_sentiment = max(-1.0, min(1.0, normalized_sentiment))
            else:
                normalized_sentiment = 0.0
            
            # Classify sentiment
            if normalized_sentiment > 0.3:
                sentiment = "POSITIVE"
            elif normalized_sentiment < -0.3:
                sentiment = "NEGATIVE"
            else:
                sentiment = "NEUTRAL"
            
            # Confidence increases with more sentiment words found
            confidence = min(
                0.95,
                0.5 + (total_words_with_sentiment * 0.15)
            )
            
            # Add some randomness to simulate real ML (±0.05)
            confidence += random.uniform(-0.05, 0.05)
            confidence = max(0.3, min(0.95, confidence))
            
            # Classify tone
            if total_words_with_sentiment == 0:
                tone = "neutral"
            elif len(text.split()) < 10:
                tone = "short_" + sentiment.lower()
            else:
                tone = sentiment.lower()
            
            # Build analysis result
            analysis = {
                "sentiment": sentiment,
                "sentiment_score": round(normalized_sentiment, 3),
                "tone": tone,
                "positive_words_found": found_positive,
                "negative_words_found": found_negative,
                "total_sentiment_words": total_words_with_sentiment,
                "execution_time_ms": round(exec_time * 1000, 1),
            }
            
            timestamp_end = datetime.now().timestamp()
            
            return ExpertResult(
                expert_name=self.name,
                result=analysis,
                confidence=confidence,
                metadata={
                    "version": self.version,
                    "model": "sentiment_analyzer_v1",
                    "analysis_type": "sentiment_analysis",
                    "keywords_used": total_words_with_sentiment,
                },
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
            )
        
        except Exception as e:
            timestamp_end = datetime.now().timestamp()
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            
            return ExpertResult(
                expert_name=self.name,
                result={},
                confidence=0.0,
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
                error=f"Analysis error: {str(e)}",
            )
    
    def get_supported_tasks(self) -> list:
        """Return supported task types."""
        return ["sentiment_analysis", "tone_detection", "emotion_detection", "demo"]
