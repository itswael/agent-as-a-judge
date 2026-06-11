import json
import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd


class ResultExporter:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save_json(self, result: Dict[str, Any], filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_judge_trace_{timestamp}.json"

        output_path = os.path.join(self.output_dir, filename)

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=2, ensure_ascii=False)

        return output_path

    def build_full_trace_record(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": result.get("id"),
            "question": result.get("question"),
            "minimum_context_answer": result.get("minimum_context_answer"),
            "agricultural_chatbot_answer": result.get("agricultural_chatbot_answer"),
            "question_type": result.get("question_type"),
            "risk_level": result.get("risk_level"),
            "selected_metrics": result.get("selected_metrics"),
            "agronomic_categories": result.get("agronomic_categories"),
            "benchmark_metric_mapping": result.get("benchmark_metric_mapping"),
            "planner_output": result.get("planner_output"),
            "claims": result.get("claims"),
            "evidence_check": result.get("evidence_check"),
            "metric_results": result.get("metric_results"),
            "context_impact_analysis": result.get("context_impact_analysis"),
            "final_decision": result.get("final_decision"),
            "trace": result.get("trace"),
            "errors": result.get("errors"),
        }

    def _build_metric_reasoning(
        self,
        metric_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        metric_reasoning = {}

        for metric_name, metric_value in metric_results.items():
            if metric_name in ["context_gain", "comparative_winner_reasoning"]:
                metric_reasoning[metric_name] = {
                    "score": metric_value.get("score"),
                    "winner": metric_value.get("winner"),
                    "reason": metric_value.get("reason"),
                }
            else:
                minimum_result = metric_value.get("minimum_context_answer", {})
                agricultural_result = metric_value.get(
                    "agricultural_chatbot_answer", {}
                )

                metric_reasoning[metric_name] = {
                    "minimum_context": {
                        "score": minimum_result.get("score"),
                        "reason": minimum_result.get("reason"),
                    },
                    "agricultural_chatbot": {
                        "score": agricultural_result.get("score"),
                        "reason": agricultural_result.get("reason"),
                    },
                }

        return metric_reasoning

    def build_clean_summary_record(self, result: Dict[str, Any]) -> Dict[str, Any]:
        metric_results = result.get("metric_results", {}) or {}
        context_impact = result.get("context_impact_analysis", {}) or {}
        final_decision = result.get("final_decision", {}) or {}

        return {
            "id": result.get("id"),
            "question": result.get("question"),
            "routing_path": result.get("routing_path", "unknown"),  # Include routing path

            "final_decision": {
                "winner": final_decision.get("winner"),
                "confidence": final_decision.get("confidence"),
                "reason": final_decision.get("final_reason"),
            },

            "metric_reasoning": self._build_metric_reasoning(metric_results),

            "context_impact": {
                "overall_context_value_score": context_impact.get(
                    "overall_context_value_score"
                ),
                "most_valuable_gate_context": context_impact.get(
                    "most_valuable_gate_context"
                ),
                "context_value_ranking": context_impact.get(
                    "context_value_ranking"
                ),
                "why_context_matters": context_impact.get(
                    "context_value_conclusion"
                ),
            },

            "context_change": {
                "without_context": context_impact.get(
                    "without_context_summary"
                ),
                "with_context": context_impact.get(
                    "with_context_summary"
                ),
                "response_change": context_impact.get(
                    "response_change_summary"
                ),
            },

            "specificity_and_usefulness": {
                "specificity_improvement": context_impact.get(
                    "specificity_improvement"
                ),
                "actionability_improvement": context_impact.get(
                    "actionability_improvement"
                ),
            },

            "strengths_and_weaknesses": {
                "minimum_context_strengths": final_decision.get(
                    "minimum_context_strengths"
                ),
                "minimum_context_weaknesses": final_decision.get(
                    "minimum_context_weaknesses"
                ),
                "agricultural_chatbot_strengths": final_decision.get(
                    "agricultural_chatbot_strengths"
                ),
                "agricultural_chatbot_weaknesses": final_decision.get(
                    "agricultural_chatbot_weaknesses"
                ),
            },

            "errors": result.get("errors"),
        }

    def build_context_question_record(
        self,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        context_impact = result.get("context_impact_analysis", {}) or {}
        final_decision = result.get("final_decision", {}) or {}

        return {
            "id": result.get("id"),
            "question": result.get("question"),

            "main_question_1_without_vs_with_context": {
                "without_context_summary": context_impact.get(
                    "without_context_summary"
                ),
                "with_context_summary": context_impact.get(
                    "with_context_summary"
                ),
                "response_change_summary": context_impact.get(
                    "response_change_summary"
                ),
            },

            "main_question_2_which_gate_context_added_most_value": {
                "most_valuable_gate_context": context_impact.get(
                    "most_valuable_gate_context"
                ),
                "context_value_ranking": context_impact.get(
                    "context_value_ranking"
                ),
                "overall_context_value_score": context_impact.get(
                    "overall_context_value_score"
                ),
                "context_value_conclusion": context_impact.get(
                    "context_value_conclusion"
                ),
            },

            "main_question_3_how_context_improved_specificity_and_usefulness": {
                "specificity_improvement": context_impact.get(
                    "specificity_improvement"
                ),
                "practical_usefulness_improvement": context_impact.get(
                    "practical_usefulness_improvement"
                ),
                "decision_quality_improvement": context_impact.get(
                    "decision_quality_improvement"
                ),
            },

            "main_question_4_context_utilization_quality": {
                "gate_context_impact": context_impact.get(
                    "gate_context_impact"
                ),
                "context_utilization_analysis": context_impact.get(
                    "context_utilization_analysis"
                ),
                "weak_or_unhelpful_context_usage": context_impact.get(
                    "weak_or_unhelpful_context_usage"
                ),
            },

            "final_outcome": {
                "winner": final_decision.get("winner"),
                "confidence": final_decision.get("confidence"),
                "reason": final_decision.get("final_reason"),
            },

            "errors": result.get("errors"),
        }

    def flatten_summary_for_table(
        self,
        summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        final_decision = summary.get("final_decision", {}) or {}
        context_impact = summary.get("context_impact", {}) or {}
        metric_reasoning = summary.get("metric_reasoning", {}) or {}

        row = {
            "id": summary.get("id"),
            "question": summary.get("question"),
            "path": summary.get("routing_path", "unknown"),  # Add path column
            "winner": final_decision.get("winner"),
            "confidence": final_decision.get("confidence"),
            "final_reason": final_decision.get("reason"),
            # Context impact fields - only populated in full path, use defaults otherwise
            "context_value_score": context_impact.get(
                "overall_context_value_score", 0.0
            ),
            "most_valuable_gate_context": (
                context_impact.get("most_valuable_gate_context", {}) or {}
            ).get("category", "N/A"),
            "context_reason": (
                context_impact.get("most_valuable_gate_context", {}) or {}
            ).get("reason", "Not analyzed (fast/medium path)"),
        }

        for metric_name, metric_value in metric_reasoning.items():
            if metric_name in ["context_gain", "comparative_winner_reasoning"]:
                row[f"{metric_name}_score"] = metric_value.get("score")
                row[f"{metric_name}_winner"] = metric_value.get("winner")
                row[f"{metric_name}_reason"] = metric_value.get("reason")
            else:
                minimum_context = metric_value.get("minimum_context", {}) or {}
                agricultural_chatbot = metric_value.get(
                    "agricultural_chatbot", {}
                ) or {}

                row[f"{metric_name}_minimum_score"] = minimum_context.get(
                    "score"
                )
                row[f"{metric_name}_minimum_reason"] = minimum_context.get(
                    "reason"
                )
                row[f"{metric_name}_agricultural_score"] = (
                    agricultural_chatbot.get("score")
                )
                row[f"{metric_name}_agricultural_reason"] = (
                    agricultural_chatbot.get("reason")
                )

        return row

    def save_summary_table(
        self,
        summaries: List[Dict[str, Any]],
        csv_filename: str = "summary_results.csv",
        excel_filename: str = "summary_results.xlsx",
    ) -> Dict[str, str]:
        rows = [
            self.flatten_summary_for_table(summary)
            for summary in summaries
        ]

        dataframe = pd.DataFrame(rows)

        csv_path = os.path.join(self.output_dir, csv_filename)
        excel_path = os.path.join(self.output_dir, excel_filename)

        dataframe.to_csv(csv_path, index=False)
        dataframe.to_excel(excel_path, index=False)

        return {
            "csv_path": csv_path,
            "excel_path": excel_path,
        }