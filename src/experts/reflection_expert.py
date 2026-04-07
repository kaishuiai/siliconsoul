"""Reflection Expert - Assess decision quality and continuous learning"""
import time
import logging
from typing import List, Dict, Any
from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult

logger = logging.getLogger(__name__)

class ReflectionExpert(Expert):
    """Analyzes decision quality and provides learning feedback."""
    
    def __init__(self):
        super().__init__(name="ReflectionExpert", version="1.0")
        self.logger.info("ReflectionExpert initialized")
    
    def get_supported_tasks(self) -> List[str]:
        return ["reflection", "quality_assessment", "continuous_learning"]
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """Assess decision quality and generate learning feedback."""
        start_time = time.time()
        try:
            self.logger.info(f"Reflecting on decision for user: {request.user_id}")
            
            # Get decision context
            decision_result = request.extra_params.get("decision", {}) if request.extra_params else {}
            
            # Assess quality
            assessment = self._assess_decision_quality(decision_result)
            
            # Generate improvements
            improvements = self._generate_improvements(assessment)
            
            # Build result
            result_data = {
                "quality_score": assessment["score"],
                "assessment": assessment["assessment"],
                "improvement_suggestions": improvements,
                "confidence_level": assessment["confidence"]
            }
            
            end_time = time.time()
            return ExpertResult(
                expert_name=self.name,
                result=result_data,
                confidence=assessment["confidence"],
                metadata={"version": self.version},
                timestamp_start=start_time,
                timestamp_end=end_time
            )
        except Exception as e:
            return self._error_result(start_time, str(e))
    
    def _assess_decision_quality(self, decision: Dict) -> Dict[str, Any]:
        """Assess the quality of a decision."""
        confidence = decision.get("confidence", 0.5)
        score = min(1.0, confidence)
        return {
            "score": round(score, 3),
            "confidence": round(score, 3),
            "assessment": "Well-reasoned decision with solid supporting data" if score > 0.7 else "Moderate confidence decision"
        }
    
    def _generate_improvements(self, assessment: Dict) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        if assessment["score"] < 0.7:
            suggestions.append("Consider gathering more data before next decision")
            suggestions.append("Review recent analysis for patterns")
        suggestions.append("Document this decision for future learning")
        return suggestions
    
    def _error_result(self, start_time: float, error_message: str) -> ExpertResult:
        return ExpertResult(
            expert_name=self.name,
            result={"error": error_message},
            confidence=0.0,
            metadata={"version": self.version},
            timestamp_start=start_time,
            timestamp_end=time.time(),
            error=error_message
        )
