import concurrent.futures
from typing import Any, Dict

from metrics.specificity import SpecificityMetric
from metrics.actionability import ActionabilityMetric
from metrics.conciseness import ConcisenessMetric
from metrics.safety_risk_awareness import SafetyRiskAwarenessMetric
from metrics.comparative_winner_reasoning import ComparativeWinnerReasoningMetric


class MetricToolAgent:
    name = "metric_tool_agent"

    def __init__(self, judge_client):
        self.judge_client = judge_client

        self.metric_tools = {
            "specificity": SpecificityMetric(judge_client),
            "actionability": ActionabilityMetric(judge_client),
            "conciseness": ConcisenessMetric(judge_client),
            "safety_risk_awareness": SafetyRiskAwarenessMetric(judge_client),
            "comparative_winner_reasoning": ComparativeWinnerReasoningMetric(
                judge_client
            ),
        }

    def _safe_run_single_metric(
        self,
        metric,
        question: str,
        answer: str,
        latitude=None,
        longitude=None,
        date=None,
    ) -> Dict[str, Any]:
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

    def _run_single_metric_parallel(self, metric_name: str, answer_type: str) -> tuple:
        """Helper to run a single metric evaluation (for parallel execution)."""
        metric = self.metric_tools[metric_name]
        question = self._question
        answer = self._answers[answer_type]
        
        if metric_name == "comparative_winner_reasoning":
            result = self._safe_run_pairwise_metric(
                metric,
                question,
                self._answers["minimum_context_answer"],
                self._answers["agricultural_chatbot_answer"],
            )
        else:
            result = {
                "minimum_context_answer": self._safe_run_single_metric(
                    metric, question, self._answers["minimum_context_answer"],
                    latitude=self._latitude, longitude=self._longitude, date=self._date,
                ),
                "agricultural_chatbot_answer": self._safe_run_single_metric(
                    metric, question, self._answers["agricultural_chatbot_answer"],
                    latitude=self._latitude, longitude=self._longitude, date=self._date,
                ),
            }
        
        return (metric_name, result)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state["question"]
        minimum_context_answer = state["minimum_context_answer"]
        agricultural_chatbot_answer = state["agricultural_chatbot_answer"]

        selected_metrics = state.get("selected_metrics", [])

        latitude = state.get("latitude")
        longitude = state.get("longitude")
        date = state.get("date")

        metric_results = {}

        for metric_name in selected_metrics:
            metric = self.metric_tools.get(metric_name)

            if metric is None:
                metric_results[metric_name] = {
                    "error": f"Metric tool not found: {metric_name}"
                }
                continue

            if metric_name == "comparative_winner_reasoning":
                metric_results[metric_name] = (
                    self._safe_run_pairwise_metric(
                        metric,
                        question,
                        minimum_context_answer,
                        agricultural_chatbot_answer,
                    )
                )

            else:
                metric_results[metric_name] = {
                    "minimum_context_answer": self._safe_run_single_metric(
                        metric,
                        question,
                        minimum_context_answer,
                        latitude=latitude,
                        longitude=longitude,
                        date=date,
                    ),
                    "agricultural_chatbot_answer": self._safe_run_single_metric(
                        metric,
                        question,
                        agricultural_chatbot_answer,
                        latitude=latitude,
                        longitude=longitude,
                        date=date,
                    ),
                }

        # Parallelize metric evaluations
        if len(selected_metrics) > 1 and self.judge_client.parallelize:
            metric_results = self._run_metrics_parallel(
                selected_metrics, question, minimum_context_answer, 
                agricultural_chatbot_answer, latitude, longitude, date
            )
        else:
            # Sequential execution for single metric or when parallelization disabled
            for metric_name in selected_metrics:
                metric = self.metric_tools.get(metric_name)

                if metric is None:
                    metric_results[metric_name] = {
                        "error": f"Metric tool not found: {metric_name}"
                    }
                    continue

                if metric_name == "comparative_winner_reasoning":
                    metric_results[metric_name] = (
                        self._safe_run_pairwise_metric(
                            metric,
                            question,
                            minimum_context_answer,
                            agricultural_chatbot_answer,
                        )
                    )

                else:
                    metric_results[metric_name] = {
                        "minimum_context_answer": self._safe_run_single_metric(
                            metric,
                            question,
                            minimum_context_answer,
                            latitude=latitude,
                            longitude=longitude,
                            date=date,
                        ),
                        "agricultural_chatbot_answer": self._safe_run_single_metric(
                            metric,
                            question,
                            agricultural_chatbot_answer,
                            latitude=latitude,
                            longitude=longitude,
                            date=date,
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

    def _run_metrics_parallel(
        self,
        selected_metrics: list[str],
        question: str,
        minimum_context_answer: str,
        agricultural_chatbot_answer: str,
        latitude=None,
        longitude=None,
        date=None,
    ) -> Dict[str, Any]:
        """Run multiple metrics in parallel."""
        metric_results = {}
        
        def run_metric(metric_name: str) -> tuple:
            """Run a single metric and return (metric_name, result)."""
            metric = self.metric_tools.get(metric_name)
            
            if metric is None:
                return (metric_name, {"error": f"Metric tool not found: {metric_name}"})
            
            try:
                if metric_name == "comparative_winner_reasoning":
                    result = self._safe_run_pairwise_metric(
                        metric,
                        question,
                        minimum_context_answer,
                        agricultural_chatbot_answer,
                    )
                else:
                    result = {
                        "minimum_context_answer": self._safe_run_single_metric(
                            metric, question, minimum_context_answer,
                            latitude=latitude, longitude=longitude, date=date,
                        ),
                        "agricultural_chatbot_answer": self._safe_run_single_metric(
                            metric, question, agricultural_chatbot_answer,
                            latitude=latitude, longitude=longitude, date=date,
                        ),
                    }
                return (metric_name, result)
            except Exception as error:
                return (metric_name, {"error": f"Metric failed: {str(error)}"})
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(3, len(selected_metrics))) as executor:
            futures = [executor.submit(run_metric, metric_name) for metric_name in selected_metrics]
            
            for future in concurrent.futures.as_completed(futures):
                metric_name, result = future.result()
                metric_results[metric_name] = result
        
        return metric_results