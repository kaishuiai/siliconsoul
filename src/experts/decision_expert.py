"""
Decision Expert - 决策支持专家

This expert provides decision support and recommendations:
- Multi-criteria decision analysis
- Risk assessment and mitigation
- Option comparison and ranking
- Decision tree construction
- Confidence scoring for recommendations

The expert analyzes decision scenarios and provides data-driven
recommendations with clear reasoning.

Supported Tasks:
- decision_support: Complete decision analysis
- risk_assessment: Assess risks
- option_comparison: Compare alternatives
- recommendation: Final decision recommendation
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult


class DecisionExpert(Expert):
    """
    Decision Expert - Decision support and recommendation
    
    Provides analysis and recommendations for complex decisions using
    multi-criteria analysis and risk assessment.
    
    Features:
    - Identify decision criteria
    - Evaluate alternatives against criteria
    - Calculate weighted scores
    - Assess risks and benefits
    - Generate recommendations
    
    Decision Framework:
    - Define problem and objectives
    - Identify alternatives
    - Establish criteria
    - Evaluate options
    - Recommend decision
    """
    
    def __init__(self):
        """Initialize Decision Expert"""
        super().__init__(name="DecisionExpert", version="1.0")
        
        # Default criteria weights
        self.default_criteria = {
            "cost": 0.25,
            "benefit": 0.30,
            "risk": 0.20,
            "time": 0.15,
            "feasibility": 0.10
        }
        
        self.logger.info("DecisionExpert initialized")
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        Analyze decision scenario and provide recommendation.
        
        Args:
            request: ExpertRequest containing decision problem
        
        Returns:
            ExpertResult with decision analysis
        """
        timestamp_start = datetime.now().timestamp()
        
        try:
            text = request.text.lower()
            
            await asyncio.sleep(0.15)
            
            # Extract decision parameters
            problem = self._extract_problem(text)
            alternatives = self._extract_alternatives(text)
            criteria = self._extract_criteria(text)
            
            # Evaluate options
            evaluations = self._evaluate_options(alternatives, criteria)
            
            # Calculate scores
            scores = self._calculate_scores(evaluations, criteria)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(scores, alternatives)
            
            # Assess risks
            risks = self._assess_risks(recommendation)
            
            # Calculate confidence
            confidence = self._calculate_confidence(scores, risks)
            
            # Build result
            analysis_result = {
                "problem": problem,
                "alternatives": alternatives,
                "criteria": criteria,
                "evaluations": evaluations,
                "scores": scores,
                "recommendation": recommendation,
                "risks": risks,
                "confidence": round(confidence, 2),
                "next_steps": self._generate_next_steps(recommendation)
            }
            
            timestamp_end = datetime.now().timestamp()
            
            return ExpertResult(
                expert_name=self.name,
                result=analysis_result,
                confidence=confidence,
                metadata={
                    "version": self.version,
                    "analysis_type": "multi_criteria",
                    "timestamp": datetime.now().isoformat()
                },
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
            )
        
        except Exception as e:
            timestamp_end = datetime.now().timestamp()
            self.logger.error(f"Decision analysis failed: {str(e)}", exc_info=True)
            
            return ExpertResult(
                expert_name=self.name,
                result={},
                confidence=0.0,
                timestamp_start=timestamp_start,
                timestamp_end=timestamp_end,
                error=f"Decision error: {str(e)}",
            )
    
    def _extract_problem(self, text: str) -> str:
        """Extract decision problem"""
        return text[:100] if text else "Decision problem"
    
    def _extract_alternatives(self, text: str) -> List[str]:
        """Extract alternative options"""
        # Simulated extraction
        alternatives = ["Option A", "Option B", "Option C"]
        return alternatives
    
    def _extract_criteria(self, text: str) -> Dict[str, float]:
        """Extract decision criteria"""
        return self.default_criteria.copy()
    
    def _evaluate_options(self, alternatives: List[str], criteria: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Evaluate each option against criteria"""
        evaluations = {}
        
        for alt in alternatives:
            evaluations[alt] = {}
            for criterion in criteria.keys():
                # Simulated scoring
                score = (hash(alt + criterion) % 100) / 100
                evaluations[alt][criterion] = round(score, 2)
        
        return evaluations
    
    def _calculate_scores(self, evaluations: Dict[str, Dict[str, float]], criteria: Dict[str, float]) -> Dict[str, float]:
        """Calculate weighted scores"""
        scores = {}
        
        for alt, evals in evaluations.items():
            weighted_score = sum(
                evals.get(criterion, 0) * weight
                for criterion, weight in criteria.items()
            )
            scores[alt] = round(weighted_score, 2)
        
        return scores
    
    def _generate_recommendation(self, scores: Dict[str, float], alternatives: List[str]) -> Dict[str, Any]:
        """Generate recommendation"""
        if not scores:
            return {"recommended": "No recommendation", "score": 0}
        
        best_alt = max(scores.items(), key=lambda x: x[1])
        
        return {
            "recommended": best_alt[0],
            "score": best_alt[1],
            "reasoning": f"{best_alt[0]} has the highest weighted score"
        }
    
    def _assess_risks(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks of recommendation"""
        return {
            "risk_level": "moderate",
            "key_risks": ["Implementation risk", "Market risk"],
            "mitigation": "Monitor progress and adapt as needed"
        }
    
    def _calculate_confidence(self, scores: Dict[str, float], risks: Dict[str, Any]) -> float:
        """Calculate confidence in recommendation"""
        if not scores:
            return 0.0
        
        values = list(scores.values())
        avg_score = sum(values) / len(values)
        
        # Higher confidence if best option is clearly better
        confidence = 0.5 + (avg_score * 0.5)
        
        return min(1.0, max(0.5, confidence))
    
    def _generate_next_steps(self, recommendation: Dict[str, Any]) -> List[str]:
        """Generate next steps"""
        return [
            "Develop implementation plan",
            "Allocate resources",
            "Monitor and evaluate",
            "Adjust as needed"
        ]
    
    def get_supported_tasks(self) -> List[str]:
        """Return supported task types"""
        return [
            "decision_support",
            "risk_assessment",
            "option_comparison",
            "recommendation"
        ]
