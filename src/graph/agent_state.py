from typing import Any, Dict, List, Optional, TypedDict


class AgentJudgeState(TypedDict, total=False):
    id: int
    question: str
    minimum_context_answer: str
    agricultural_chatbot_answer: str

    planner_output: Dict[str, Any]

    selected_metrics: List[str]
    question_type: str
    risk_level: str
    evaluation_plan: List[str]

    claims: Dict[str, Any]
    evidence_check: Dict[str, Any]
    metric_results: Dict[str, Any]
    context_impact_analysis: Dict[str, Any]
    final_decision: Dict[str, Any]

    trace: List[Dict[str, Any]]
    errors: List[str]