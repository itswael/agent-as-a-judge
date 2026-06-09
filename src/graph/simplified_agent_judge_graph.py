"""
Simplified AgentJudgeGraph with fewer agents for faster processing.
Uses only 3-4 agents instead of 6, combining some tasks.
"""

import concurrent.futures
from typing import Any, Dict, List

from langgraph.graph import END, START, StateGraph

from src.agents.planner_agent import EvaluationPlannerAgent
from src.agents.claim_extractor_agent import ClaimExtractorAgent
from src.agents.metric_tool_agent import MetricToolAgent
from src.agents.final_decision_agent import FinalDecisionAgent
from src.graph.agent_state import AgentJudgeState


class SimplifiedAgentJudgeGraph:
    """Simplified graph with fewer agents for faster processing."""
    
    def __init__(self, judge_client, parallelize: bool = True):
        self.judge_client = judge_client
        self.parallelize = parallelize

        self.planner_agent = EvaluationPlannerAgent(judge_client)
        self.claim_extractor_agent = ClaimExtractorAgent(judge_client)
        self.metric_tool_agent = MetricToolAgent(judge_client)
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

    def parallel_analysis_node(self, state: AgentJudgeState) -> AgentJudgeState:
        """Run evidence checking, metrics, and context impact in parallel."""
        # For simplified version, we'll just run metric_tool which includes evidence checking
        try:
            return self.metric_tool_agent.run(state)
        except Exception as error:
            return {
                "errors": state.get("errors", []) + [f"Analysis failed: {str(error)}"],
                "trace": state.get("trace", []) + [{
                    "agent": "analysis_agent",
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
        
        # Parallel analysis node (combines evidence, metrics, context impact)
        graph.add_node("parallel_analysis", self.parallel_analysis_node)
        
        graph.add_node("final_decision", self.final_decision_node)

        graph.add_edge(START, "planner")
        graph.add_edge("planner", "claim_extractor")
        graph.add_edge("claim_extractor", "parallel_analysis")
        graph.add_edge("parallel_analysis", "final_decision")
        graph.add_edge("final_decision", END)

        return graph.compile()


def create_fast_graph(judge_client):
    """Create a fast processing graph."""
    return SimplifiedAgentJudgeGraph(judge_client, parallelize=True).build()
