"""
Demo Expert 2 - Text Analysis

A demo expert that analyzes text characteristics.
Demonstrates a slightly more complex expert implementation.

Characteristics:
- Moderate execution (300ms)
- Variable confidence based on input length
- Returns text statistics
"""

import asyncio
from datetime import datetime
from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult


class DemoExpert2(Expert):
    """
    Demo Expert 2: Text Analysis Expert
    
    This expert demonstrates a slightly more complex implementation:
    - Analyzes text characteristics
    - Variable confidence based on analysis
    - Returns structured text metrics
    - Takes longer to compute (300ms)
    
    Purpose: Framework testing with realistic complexity
    
    Supported Tasks:
    - text_analysis: Text statistics and analysis
    - content_review: Content quality assessment
    - demo: General demonstration
    """
    
    def __init__(self):
        """Initialize Demo Expert 2."""
        super().__init__(name="DemoExpert2", version="1.0")
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        Analyze text characteristics.
        
        Performs text analysis including:
        - Word count
        - Sentence count
        - Average word length
        - Text complexity score
        
        Args:
            request: ExpertRequest with user input
        
        Returns:
            ExpertResult with text analysis
        """
        timestamp_start = datetime.now().timestamp()
        
        try:
            text = request.text
            
            # Simulate processing (300ms)
            await asyncio.sleep(0.3)
            
            # Text analysis
            words = text.split()
            word_count = len(words)
            
            sentences = text.split('.')
            sentence_count = len([s for s in sentences if s.strip()])
            
            avg_word_length = (
                sum(len(w) for w in words) / len(words)
                if words else 0
            )
            
            # Calculate text complexity (0-1)
            # Higher complexity = longer words and sentences
            if sentence_count > 0:
                words_per_sentence = word_count / sentence_count
            else:
                words_per_sentence = 0
            
            complexity = min(1.0, (avg_word_length / 10.0) * (words_per_sentence / 15.0))
            
            # Confidence based on text length
            # More text = more confidence in analysis
            if word_count < 5:
                confidence = 0.4
            elif word_count < 20:
                confidence = 0.7
            else:
                confidence = 0.9
            
            # Build analysis result
            analysis = {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_word_length": round(avg_word_length, 2),
                "words_per_sentence": round(words_per_sentence, 2),
                "complexity_score": round(complexity, 3),
                "text_category": (
                    "short" if word_count < 10 else
                    "medium" if word_count < 50 else
                    "long"
                ),
            }
            
            timestamp_end = datetime.now().timestamp()
            
            return ExpertResult(
                expert_name=self.name,
                result=analysis,
                confidence=confidence,
                metadata={
                    "version": self.version,
                    "model": "text_analyzer_v1",
                    "analysis_type": "content_analysis",
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
        return ["text_analysis", "content_review", "demo"]
