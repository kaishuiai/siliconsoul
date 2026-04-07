"""Decision Expert - Aggregate expert results into unified decisions"""
import time
import logging
from typing import List, Dict, Any
from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult

logger = logging.getLogger(__name__)

class DecisionExpert(Expert):
    """Aggregates results from multiple experts into unified decisions."""
    
    def __init__(self):
        super().__init__(name="DecisionExpert", version="1.0")
        self.logger.info("DecisionExpert initialized")
    
    def get_supported_tasks(self) -> List[str]:
        return ["decision_making", "result_aggregation", "recommendation"]
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """Analyze and aggregate expert results into unified decision."""
        start_time = time.time()
        try:
            self.logger.info(f"Making decision for user: {request.user_id}")
            
            # Extract context with aggregated results
            expert_results = request.extra_params.get("expert_results", []) if request.extra_params else []
            
            # Aggregate confidence scores
            avg_confidence = sum(r.get("confidence", 0.5) for r in expert_results) / max(1, len(expert_results))
            
            # Generate decision
            decision = self._make_decision(expert_results, avg_confidence)
            
            # Build result
            result_data = {
                "aggregated_results": len(expert_results),
                "decision": decision["action"],
                "confidence": round(avg_confidence, 3),
                "reasoning": decision["reasoning"],
                "risk_level": decision["risk_level"]
            }
            
            end_time = time.time()
            return ExpertResult(
                expert_name=self.name,
                result=result_data,
                confidence=avg_confidence,
                metadata={"version": self.version},
                timestamp_start=start_time,
                timestamp_end=end_time
            )
        except Exception as e:
            return self._error_result(start_time, str(e))
    
    def _make_decision(self, results: List[Dict], confidence: float) -> Dict[str, Any]:
        """Make final decision based on expert results."""
        return {
            "action": "BUY" if confidence > 0.6 else "HOLD" if confidence > 0.4 else "SELL",
            "reasoning": f"Decision based on {len(results)} expert analyses with {confidence:.0%} confidence",
            "risk_level": "HIGH" if confidence < 0.5 else "MEDIUM" if confidence < 0.8 else "LOW"
        }
    
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
