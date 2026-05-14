from typing import Any, Dict

from metrics.completeness import CompletenessMetric
from metrics.practical_usefulness import PracticalUsefulnessMetric
from metrics.faithfulness import FaithfulnessMetric
from metrics.conciseness import ConcisenessMetric
from metrics.safety_risk_awareness import SafetyRiskAwarenessMetric
from metrics.context_gain import ContextGainMetric
from metrics.specificity import SpecificityMetric
from metrics.comparative_winner_reasoning import ComparativeWinnerReasoningMetric


class MetricToolAgent:
    name = "metric_tool_agent"

    def __init__(self, judge_client):
        self.judge_client = judge_client

        self.metric_tools = {
            "completeness": CompletenessMetric(judge_client),
            "practical_usefulness": PracticalUsefulnessMetric(judge_client),
            "faithfulness": FaithfulnessMetric(judge_client),
            "conciseness": ConcisenessMetric(judge_client),
            "safety_risk_awareness": SafetyRiskAwarenessMetric(judge_client),
            "specificity": SpecificityMetric(judge_client),
            "context_gain": ContextGainMetric(judge_client),
            "comparative_winner_reasoning": ComparativeWinnerReasoningMetric(judge_client),
        }

    def _safe_run_single_metric(self, metric, question: str, answer: str) -> Dict[str, Any]:
        try:
            return metric.evaluate(question, answer)
        except Exception as error:
            return {
                "score": 0.0,
                "reason": f"Metric failed: {str(error)}",
            }

    def _safe_run_pairwise_metric(
        self,
        metric,
        question: str,
        minimum_context_answer: str,
        agricultural_chatbot_answer: str,
    ) -> Dict[str, Any]:
        try:
            return metric.evaluate(
                question,
                minimum_context_answer,
                agricultural_chatbot_answer,
            )
        except Exception as error:
            return {
                "score": 0.0,
                "winner": "tie",
                "reason": f"Pairwise metric failed: {str(error)}",
            }

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state["question"]
        minimum_context_answer = state["minimum_context_answer"]
        agricultural_chatbot_answer = state["agricultural_chatbot_answer"]

        selected_metrics = state.get("selected_metrics", [])

        metric_results = {}

        for metric_name in selected_metrics:
            metric = self.metric_tools.get(metric_name)

            if metric is None:
                metric_results[metric_name] = {
                    "error": f"Metric tool not found: {metric_name}"
                }
                continue

            if metric_name in ["context_gain", "comparative_winner_reasoning"]:
                metric_results[metric_name] = self._safe_run_pairwise_metric(
                    metric,
                    question,
                    minimum_context_answer,
                    agricultural_chatbot_answer,
                )
            else:
                metric_results[metric_name] = {
                    "minimum_context_answer": self._safe_run_single_metric(
                        metric,
                        question,
                        minimum_context_answer,
                    ),
                    "agricultural_chatbot_answer": self._safe_run_single_metric(
                        metric,
                        question,
                        agricultural_chatbot_answer,
                    ),
                }

        trace_entry = {
            "agent": self.name,
            "action": "executed_metric_tools",
            "selected_metrics": selected_metrics,
            "output": metric_results,
        }

        return {
            "metric_results": metric_results,
            "trace": state.get("trace", []) + [trace_entry],
        }