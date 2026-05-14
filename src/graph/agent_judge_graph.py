from langgraph.graph import END, START, StateGraph

from src.agents.planner_agent import EvaluationPlannerAgent
from src.agents.claim_extractor_agent import ClaimExtractorAgent
from src.agents.evidence_checker_agent import EvidenceCheckerAgent
from src.agents.metric_tool_agent import MetricToolAgent
from src.agents.context_impact_agent import ContextImpactAgent
from src.agents.final_decision_agent import FinalDecisionAgent
from src.graph.agent_state import AgentJudgeState


class AgentJudgeGraph:
    def __init__(self, judge_client):
        self.judge_client = judge_client

        self.planner_agent = EvaluationPlannerAgent(judge_client)
        self.claim_extractor_agent = ClaimExtractorAgent(judge_client)
        self.evidence_checker_agent = EvidenceCheckerAgent(judge_client)
        self.metric_tool_agent = MetricToolAgent(judge_client)
        self.context_impact_agent = ContextImpactAgent(judge_client)
        self.final_decision_agent = FinalDecisionAgent(judge_client)

    def planner_node(self, state: AgentJudgeState) -> AgentJudgeState:
        try:
            return self.planner_agent.run(state)
        except Exception as error:
            return {
                "errors": state.get("errors", []) + [f"Planner failed: {str(error)}"],
                "trace": state.get("trace", []) + [{
                    "agent": "evaluation_planner_agent",
                    "action": "error",
                    "error": str(error),
                }],
            }

    def claim_extractor_node(self, state: AgentJudgeState) -> AgentJudgeState:
        try:
            return self.claim_extractor_agent.run(state)
        except Exception as error:
            return {
                "errors": state.get("errors", []) + [f"Claim extraction failed: {str(error)}"],
                "trace": state.get("trace", []) + [{
                    "agent": "claim_extractor_agent",
                    "action": "error",
                    "error": str(error),
                }],
            }

    def evidence_checker_node(self, state: AgentJudgeState) -> AgentJudgeState:
        try:
            return self.evidence_checker_agent.run(state)
        except Exception as error:
            return {
                "errors": state.get("errors", []) + [f"Evidence checking failed: {str(error)}"],
                "trace": state.get("trace", []) + [{
                    "agent": "evidence_checker_agent",
                    "action": "error",
                    "error": str(error),
                }],
            }

    def metric_tool_node(self, state: AgentJudgeState) -> AgentJudgeState:
        try:
            return self.metric_tool_agent.run(state)
        except Exception as error:
            return {
                "errors": state.get("errors", []) + [f"Metric tool execution failed: {str(error)}"],
                "trace": state.get("trace", []) + [{
                    "agent": "metric_tool_agent",
                    "action": "error",
                    "error": str(error),
                }],
            }

    def context_impact_node(self, state: AgentJudgeState) -> AgentJudgeState:
        try:
            return self.context_impact_agent.run(state)
        except Exception as error:
            return {
                "errors": state.get("errors", []) + [f"Context impact analysis failed: {str(error)}"],
                "trace": state.get("trace", []) + [{
                    "agent": "context_impact_agent",
                    "action": "error",
                    "error": str(error),
                }],
            }

    def final_decision_node(self, state: AgentJudgeState) -> AgentJudgeState:
        try:
            return self.final_decision_agent.run(state)
        except Exception as error:
            return {
                "errors": state.get("errors", []) + [f"Final decision failed: {str(error)}"],
                "trace": state.get("trace", []) + [{
                    "agent": "final_decision_agent",
                    "action": "error",
                    "error": str(error),
                }],
            }

    def build(self):
        graph = StateGraph(AgentJudgeState)

        graph.add_node("planner", self.planner_node)
        graph.add_node("claim_extractor", self.claim_extractor_node)
        graph.add_node("evidence_checker", self.evidence_checker_node)
        graph.add_node("metric_tool", self.metric_tool_node)
        graph.add_node("context_impact", self.context_impact_node)
        graph.add_node("final_decision", self.final_decision_node)

        graph.add_edge(START, "planner")
        graph.add_edge("planner", "claim_extractor")
        graph.add_edge("claim_extractor", "evidence_checker")
        graph.add_edge("evidence_checker", "metric_tool")
        graph.add_edge("metric_tool", "context_impact")
        graph.add_edge("context_impact", "final_decision")
        graph.add_edge("final_decision", END)

        return graph.compile()