from typing import Any, Dict


class PathRouterAgent:
    """Determines which evaluation path to take based on question complexity."""
    
    name = "path_router_agent"
    
    # Risk-related keywords that trigger full path
    RISK_KEYWORDS = [
        "fertilizer", "pesticide", "disease", "chemicals", "dosage",
        "weather risk", "irrigation risk", "crop damage", "animal health",
        "human safety", "environmental risk", "economic risk", "toxic",
        "poison", "dangerous", "hazard", "risk", "unsafe"
    ]
    
    # Simple question indicators for fast path
    SIMPLE_INDICATORS = [
        "what is", "define", "explain", "how much", "when is", "where is",
        "simple", "short", "brief", "quick", "basic", "overview"
    ]
    
    def __init__(self, judge_client):
        self.judge_client = judge_client

    def _contains_risk_keywords(self, question: str) -> bool:
        """Check if question contains risk-related keywords."""
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in self.RISK_KEYWORDS)

    def _is_simple_question(self, question: str) -> bool:
        """Check if question appears to be simple/direct."""
        question_lower = question.lower()
        return any(indicator in question_lower for indicator in self.SIMPLE_INDICATORS)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the evaluation path based on question characteristics."""
        question = state["question"]
        
        # Use planner output if available
        planner_output = state.get("planner_output", {})
        risk_level = planner_output.get("risk_level", "medium")
        selected_metrics = planner_output.get("selected_metrics", [])
        
        # Determine path based on multiple factors
        has_risk = self._contains_risk_keywords(question)
        is_simple = self._is_simple_question(question)
        
        # Decision logic:
        # Fast path: simple questions with low risk (2 metrics: specificity, comparative)
        # Medium path: moderate complexity or medium risk (4 metrics: add actionability, conciseness)
        # Full path: high risk or complex questions (all 5 metrics + evidence check)
        
        if is_simple and risk_level == "low":
            routing_path = "fast"
        elif has_risk or risk_level == "high" or len(selected_metrics) >= 4:
            routing_path = "full"
        else:
            routing_path = "medium"
        
        trace_entry = {
            "agent": self.name,
            "action": "determined_evaluation_path",
            "path": routing_path,
            "reasoning": f"risk_level={risk_level}, has_risk_keywords={has_risk}, is_simple={is_simple}, metrics_count={len(selected_metrics)}"
        }
        
        return {
            "routing_path": routing_path,
            "trace": state.get("trace", []) + [trace_entry],
        }
