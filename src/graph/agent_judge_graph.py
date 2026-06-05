import concurrent.futures
from typing import Any, Dict, List

from langgraph.graph import END, START, StateGraph

from src.agents.planner_agent import EvaluationPlannerAgent
from src.agents.claim_extractor_agent import ClaimExtractorAgent
from src.agents.evidence_checker_agent import EvidenceCheckerAgent
from src.agents.metric_tool_agent import MetricToolAgent
from src.agents.context_impact_agent import ContextImpactAgent
from src.agents.final_decision_agent import FinalDecisionAgent
from src.graph.agent_state import AgentJudgeState


class AgentJudgeGraph:
    def __init__(self, judge_client, parallelize: bool = True):
        self.judge_client = judge_client
        self.parallelize = parallelize

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

    def parallel_evidence_metrics_context(self, state: AgentJudgeState) -> AgentJudgeState:
        """Run evidence_checker, metric_tool, and context_impact in parallel."""
        nodes_to_run = [
            ("evidence_checker", self.evidence_checker_node),
            ("metric_tool", self.metric_tool_node),
            ("context_impact", self.context_impact_node),
        ]

        results = {}
        errors = state.get("errors", [])
        trace = state.get("trace", [])

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_node = {
                executor.submit(node_func, state): node_name
                for node_name, node_func in nodes_to_run
            }

            for future in concurrent.futures.as_completed(future_to_node):
                node_name = future_to_node[future]
                try:
                    result = future.result()
                    results[node_name] = result
                except Exception as error:
                    errors.append(f"{node_name} failed: {str(error)}")
                    trace.append({
                        "agent": f"{node_name}_agent",
                        "action": "error",
                        "error": str(error),
                    })

        # Merge results sequentially
        merged_state = state.copy()
        for node_name, result in results.items():
            if result:
                # Merge trace and errors
                merged_state["trace"] = merged_state.get("trace", []) + result.get("trace", [])
                merged_state["errors"] = merged_state.get("errors", []) + result.get("errors", [])

                # Merge output data
                for key, value in result.items():
                    if key not in ("trace", "errors"):
                        merged_state[key] = value

        return merged_state

    def build(self):
        graph = StateGraph(AgentJudgeState)

        graph.add_node("planner", self.planner_node)
        graph.add_node("claim_extractor", self.claim_extractor_node)
        
        # Parallel execution node for independent agents
        graph.add_node("parallel_block", self.parallel_evidence_metrics_context)
        
        graph.add_node("final_decision", self.final_decision_node)

        graph.add_edge(START, "planner")
        graph.add_edge("planner", "claim_extractor")
        graph.add_edge("claim_extractor", "parallel_block")
        graph.add_edge("parallel_block", "final_decision")
        graph.add_edge("final_decision", END)

        return graph.compile()