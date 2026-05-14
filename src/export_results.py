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
            "planner_output": result.get("planner_output"),
            "claims": result.get("claims"),
            "evidence_check": result.get("evidence_check"),
            "metric_results": result.get("metric_results"),
            "context_impact_analysis": result.get("context_impact_analysis"),
            "final_decision": result.get("final_decision"),
            "trace": result.get("trace"),
            "errors": result.get("errors"),
        }

    def _extract_metric_scores(self, metric_results: Dict[str, Any]) -> Dict[str, Any]:
        clean_scores = {}

        for metric_name, metric_value in metric_results.items():
            if metric_name in ["context_gain", "comparative_winner_reasoning"]:
                clean_scores[metric_name] = {
                    "score": metric_value.get("score"),
                    "winner": metric_value.get("winner"),
                }
            else:
                clean_scores[metric_name] = {
                    "minimum_context_answer": metric_value.get(
                        "minimum_context_answer", {}
                    ).get("score"),
                    "agricultural_chatbot_answer": metric_value.get(
                        "agricultural_chatbot_answer", {}
                    ).get("score"),
                }

        return clean_scores

    def build_clean_summary_record(self, result: Dict[str, Any]) -> Dict[str, Any]:
        claims = result.get("claims", {})
        evidence_check = result.get("evidence_check", {})
        metric_results = result.get("metric_results", {})
        context_impact_analysis = result.get("context_impact_analysis", {})
        final_decision = result.get("final_decision", {})

        return {
            "id": result.get("id"),
            "question": result.get("question"),
            "question_type": result.get("question_type"),
            "risk_level": result.get("risk_level"),
            "selected_metrics": result.get("selected_metrics"),
            "metric_scores": self._extract_metric_scores(metric_results),
            "claim_summary": claims.get("claim_summary"),
            "evidence_summary": evidence_check.get("comparative_evidence_summary"),
            "context_value_score": context_impact_analysis.get("overall_context_value_score"),
            "response_change_summary": context_impact_analysis.get("response_change_summary"),
            "most_valuable_contexts": context_impact_analysis.get("most_valuable_contexts"),
            "specificity_improvement": context_impact_analysis.get("specificity_improvement"),
            "practical_usefulness_improvement": context_impact_analysis.get(
                "practical_usefulness_improvement"
            ),
            "weak_or_unhelpful_contexts": context_impact_analysis.get(
                "weak_or_unhelpful_contexts"
            ),
            "context_value_conclusion": context_impact_analysis.get(
                "context_value_conclusion"
            ),
            "winner": final_decision.get("winner"),
            "confidence": final_decision.get("confidence"),
            "final_reason": final_decision.get("final_reason"),
            "context_impact_summary": final_decision.get("context_impact_summary"),
            "specificity_change_summary": final_decision.get(
                "specificity_change_summary"
            ),
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
            "errors": result.get("errors"),
        }

    def flatten_summary_for_table(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        metric_scores = summary.get("metric_scores", {})

        row = {
            "id": summary.get("id"),
            "question": summary.get("question"),
            "question_type": summary.get("question_type"),
            "risk_level": summary.get("risk_level"),
            "winner": summary.get("winner"),
            "confidence": summary.get("confidence"),
            "final_reason": summary.get("final_reason"),
            "context_impact_summary": summary.get("context_impact_summary"),
        }

        for metric_name, metric_value in metric_scores.items():
            if metric_name in ["context_gain", "comparative_winner_reasoning"]:
                row[f"{metric_name}_score"] = metric_value.get("score")
                row[f"{metric_name}_winner"] = metric_value.get("winner")
            else:
                row[f"{metric_name}_minimum_context"] = metric_value.get(
                    "minimum_context_answer"
                )
                row[f"{metric_name}_agricultural_chatbot"] = metric_value.get(
                    "agricultural_chatbot_answer"
                )

        return row

    def save_summary_table(
        self,
        summaries: List[Dict[str, Any]],
        csv_filename: str = "summary_results.csv",
        excel_filename: str = "summary_results.xlsx",
    ) -> Dict[str, str]:
        rows = [self.flatten_summary_for_table(summary) for summary in summaries]

        dataframe = pd.DataFrame(rows)

        csv_path = os.path.join(self.output_dir, csv_filename)
        excel_path = os.path.join(self.output_dir, excel_filename)

        dataframe.to_csv(csv_path, index=False)
        dataframe.to_excel(excel_path, index=False)

        return {
            "csv_path": csv_path,
            "excel_path": excel_path,
        }