"""
Path-Oriented AgentJudgeGraph for optimized evaluation.

This graph implements three execution paths based on question complexity:
- Fast Path: 2 metrics (specificity, comparative) - ~18s total
- Medium Path: 4 metrics (add actionability, conciseness) - ~30s total  
- Full Path: 5 metrics + evidence check + context impact - ~45s total

The routing decision is made by PathRouterAgent based on risk level and question complexity.
"""

import concurrent.futures
from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from src.agents.planner_agent import EvaluationPlannerAgent
from src.agents.claim_extractor_agent import ClaimExtractorAgent
from src.agents.evidence_checker_agent import EvidenceCheckerAgent
from src.agents.metric_tool_agent import MetricToolAgent
from src.agents.context_impact_agent import ContextImpactAgent
from src.agents.final_decision_agent import FinalDecisionAgent
from src.agents.path_router_agent import PathRouterAgent
from src.graph.agent_state import AgentJudgeState


class PathOrientedAgentJudgeGraph:
    """Graph with path-based execution for optimized performance."""
    
    def __init__(self, judge_client, parallelize: bool = True):
        self.judge_client = judge_client
        self.parallelize = parallelize

        # Initialize all agents
        self.planner_agent = EvaluationPlannerAgent(judge_client)
        self.claim_extractor_agent = ClaimExtractorAgent(judge_client)
        self.evidence_checker_agent = EvidenceCheckerAgent(judge_client)
        self.metric_tool_agent = MetricToolAgent(judge_client)
        self.context_impact_agent = ContextImpactAgent(judge_client)
        self.final_decision_agent = FinalDecisionAgent(judge_client)
        self.path_router_agent = PathRouterAgent(judge_client)

    def planner_node(self, state: AgentJudgeState) -> AgentJudgeState:
        """Run the evaluation planner."""
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

    def path_router_node(self, state: AgentJudgeState) -> AgentJudgeState:
        """Determine which evaluation path to take."""
        try:
            return self.path_router_agent.run(state)
        except Exception as error:
            return {
                "errors": state.get("errors", []) + [f"Path routing failed: {str(error)}"],
                "trace": state.get("trace", []) + [{
                    "agent": "path_router_agent",
                    "action": "error",
                    "error": str(error),
                }],
            }

    def evidence_checker_node(self, state: AgentJudgeState) -> AgentJudgeState:
        """Check evidence for claims."""
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

    def claim_extractor_node(self, state: AgentJudgeState) -> AgentJudgeState:
        """Extract claims from answers."""
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

    def fast_path_metrics_node(self, state: AgentJudgeState) -> AgentJudgeState:
        """Execute fast path: specificity + comparative_winner_reasoning only."""
        try:
            # Create a copy of state to avoid modifying original
            modified_state = state.copy()
            modified_state["selected_metrics"] = ["specificity", "comparative_winner_reasoning"]
            
            result = self.metric_tool_agent.run(modified_state)
            
            # Merge the result with state to preserve routing_path and other fields
            merged_state = state.copy()
            for key, value in result.items():
                if key not in ("trace", "errors"):
                    merged_state[key] = value
            
            # Add trace and errors from result
            merged_state["trace"] = merged_state.get("trace", []) + result.get("trace", [])
            merged_state["errors"] = merged_state.get("errors", []) + result.get("errors", [])
            
            return merged_state
        except Exception as error:
            return {
                "errors": state.get("errors", []) + [f"Fast path metrics failed: {str(error)}"],
                "trace": state.get("trace", []) + [{
                    "agent": "fast_path_metric_agent",
                    "action": "error",
                    "error": str(error),
                }],
            }

    def medium_path_metrics_node(self, state: AgentJudgeState) -> AgentJudgeState:
        """Execute medium path: specificity + actionability + conciseness + comparative."""
        try:
            # Create a copy of state to avoid modifying original
            modified_state = state.copy()
            modified_state["selected_metrics"] = ["specificity", "actionability", "conciseness", "comparative_winner_reasoning"]
            
            result = self.metric_tool_agent.run(modified_state)
            
            # Merge the result with state to preserve routing_path and other fields
            merged_state = state.copy()
            for key, value in result.items():
                if key not in ("trace", "errors"):
                    merged_state[key] = value
            
            # Add trace and errors from result
            merged_state["trace"] = merged_state.get("trace", []) + result.get("trace", [])
            merged_state["errors"] = merged_state.get("errors", []) + result.get("errors", [])
            
            return merged_state
        except Exception as error:
            return {
                "errors": state.get("errors", []) + [f"Medium path metrics failed: {str(error)}"],
                "trace": state.get("trace", []) + [{
                    "agent": "medium_path_metric_agent",
                    "action": "error",
                    "error": str(error),
                }],
            }

    def full_path_analysis_node(self, state: AgentJudgeState) -> AgentJudgeState:
        """Execute full path: all metrics + evidence check + context impact (in parallel)."""
        try:
            # Run evidence_checker, metric_tool, and context_impact in parallel
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
            
        except Exception as error:
            return {
                "errors": state.get("errors", []) + [f"Full path analysis failed: {str(error)}"],
                "trace": state.get("trace", []) + [{
                    "agent": "full_path_analysis_agent",
                    "action": "error",
                    "error": str(error),
                }],
            }

    def metric_tool_node(self, state: AgentJudgeState) -> AgentJudgeState:
        """Run all metrics."""
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
        """Run context impact analysis."""
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
        """Make final decision."""
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
        """Build the path-oriented graph."""
        graph = StateGraph(AgentJudgeState)

        # Common nodes
        graph.add_node("planner", self.planner_node)
        graph.add_node("claim_extractor", self.claim_extractor_node)
        graph.add_node("path_router", self.path_router_node)
        
        # Path-specific nodes
        graph.add_node("fast_path_metrics", self.fast_path_metrics_node)
        graph.add_node("medium_path_metrics", self.medium_path_metrics_node)
        graph.add_node("full_path_analysis", self.full_path_analysis_node)
        
        graph.add_node("final_decision", self.final_decision_node)

        # Build the graph with routing
        graph.add_edge(START, "planner")
        graph.add_edge("planner", "claim_extractor")
        graph.add_edge("claim_extractor", "path_router")
        
        # Route to appropriate path based on routing_path
        graph.add_conditional_edges(
            "path_router",
            self._route_to_path,
            {
                "fast": "fast_path_metrics",
                "medium": "medium_path_metrics",
                "full": "full_path_analysis",
            },
        )
        
        # All paths converge to final decision
        graph.add_edge("fast_path_metrics", "final_decision")
        graph.add_edge("medium_path_metrics", "final_decision")
        graph.add_edge("full_path_analysis", "final_decision")
        
        graph.add_edge("final_decision", END)

        return graph.compile()

    def _route_to_path(self, state: AgentJudgeState) -> str:
        """Determine which path to take based on routing_path."""
        return state.get("routing_path", "medium")  # Default to medium if not set


def create_path_oriented_graph(judge_client):
    """Create a path-oriented graph for optimized evaluation."""
    return PathOrientedAgentJudgeGraph(judge_client, parallelize=True).build()
