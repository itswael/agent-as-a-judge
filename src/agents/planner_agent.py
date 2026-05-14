from typing import Any, Dict


class EvaluationPlannerAgent:
    name = "evaluation_planner_agent"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state["question"]
        minimum_context_answer = state["minimum_context_answer"]
        agricultural_chatbot_answer = state["agricultural_chatbot_answer"]

        prompt = f"""
You are an Evaluation Planner Agent for an agricultural Agent-as-a-Judge framework.

Your task is to plan how two agricultural chatbot answers should be evaluated.

You must decide:
1. The type of agricultural question.
2. The risk level of the question.
3. Which evaluation metrics are needed.
4. Why each metric is needed.
5. The ordered evaluation plan.

Available metrics:
- completeness
- practical_usefulness
- faithfulness
- conciseness
- safety_risk_awareness
- context_gain
- specificity
- comparative_winner_reasoning

Metric selection policy:
- Always include completeness, practical_usefulness, faithfulness, context_gain, and comparative_winner_reasoning.
- Include safety_risk_awareness if the question involves fertilizer, pesticide, disease, chemicals, dosage, weather risk, pest control, irrigation risk, animal health, crop damage, or economic risk.
- Include specificity if the question asks about timing, amount, crop stage, method, location, soil, irrigation, pest, disease, fertilizer, or treatment details.
- Include conciseness if the question is simple, direct, or if either answer may be unnecessarily long.
- Do not include metrics outside the available metrics list.

Question:
{question}

Answer A - Minimum Context Answer:
{minimum_context_answer}

Answer B - Agricultural Chatbot Answer:
{agricultural_chatbot_answer}

Return valid JSON only in this exact structure:
{{
  "question_type": "short label",
  "risk_level": "low/medium/high",
  "selected_metrics": [
    "metric_name"
  ],
  "metric_rationale": {{
    "metric_name": "why this metric is needed"
  }},
  "evaluation_plan": [
    "step 1",
    "step 2",
    "step 3"
  ],
  "planner_reason": "short explanation of the overall evaluation strategy"
}}
"""

        result = self.judge_client.evaluate(prompt)

        selected_metrics = result.get("selected_metrics", [])
        question_type = result.get("question_type", "unknown")
        risk_level = result.get("risk_level", "medium")
        evaluation_plan = result.get("evaluation_plan", [])

        trace_entry = {
            "agent": self.name,
            "action": "planned_evaluation",
            "output": result,
        }

        return {
            "planner_output": result,
            "selected_metrics": selected_metrics,
            "question_type": question_type,
            "risk_level": risk_level,
            "evaluation_plan": evaluation_plan,
            "trace": state.get("trace", []) + [trace_entry],
        }