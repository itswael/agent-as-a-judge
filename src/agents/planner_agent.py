from typing import Any, Dict


class EvaluationPlannerAgent:
    name = "evaluation_planner_agent"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state["question"]
        context_information = state.get("context_information", "")
        minimum_context_answer = state["minimum_context_answer"]
        agricultural_chatbot_answer = state["agricultural_chatbot_answer"]

        prompt = f"""
You are an Evaluation Planner Agent for a context-grounded agricultural Agent-as-a-Judge framework.

Your task is to plan how two agricultural chatbot answers should be evaluated.

You must decide:
1. The agricultural question type.
2. The agronomic categories involved.
3. The risk level.
4. Which evaluation metrics are needed.
5. How the selected metrics map to benchmark-style agricultural evaluation dimensions.
6. The ordered evaluation plan.

Agronomic categories:
- Nutrition
- Soils
- Weather
- Water
- Pests
- Diseases
- Weeds
- Horticulture
- Seed Hybrids
- Crop Management
- General Agronomy



Available internal metrics:
- specificity
- actionability
- conciseness
- safety_risk_awareness
- comparative_winner_reasoning

B

Benchmark-style metric mapping:
- agronomic_specificity maps to specificity
- field_actionability maps to actionability
- information_efficiency maps to conciseness
- agronomic_risk_awareness maps to safety_risk_awareness
- comparative_decision_quality maps to comparative_winner_reasoning


Metric selection policy:
- Always include specificity, actionability, and comparative_winner_reasoning.
- Include safety_risk_awareness if the question involves fertilizer, pesticide, disease, chemicals, dosage, weather risk, irrigation risk, crop damage, animal health, human safety, environmental risk, or economic risk.
- Include conciseness if the question is simple/direct or either answer may be unnecessarily long.
- Do not include metrics outside the available internal metrics list.

Important:
The agricultural chatbot may have access to extra agricultural context such as soil information, weather forecast, seasonal forecast, location, crop stage, and date.
Do not treat use of this context as unsupported if it is present in Context Information.

Question:
{question}

Context Information:
{context_information}

Answer A - Minimum Context Answer:
{minimum_context_answer}

Answer B - Agricultural Chatbot Answer:
{agricultural_chatbot_answer}

Return valid JSON only in this exact structure:
{{
  "question_type": "short label",
  "agronomic_categories": [
    "Nutrition"
  ],
  "risk_level": "low/medium/high",
  "selected_metrics": [
    "metric_name"
  ],
  "benchmark_metric_mapping": {{
    "agronomic_specificity": "specificity",
    "field_actionability": "actionability",
    "information_efficiency": "conciseness",
    "agronomic_risk_awareness": "safety_risk_awareness",
    "comparative_decision_quality": "comparative_winner_reasoning"
  }},
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
        agronomic_categories = result.get("agronomic_categories", [])
        benchmark_metric_mapping = result.get("benchmark_metric_mapping", {})

        trace_entry = {
            "agent": self.name,
            "action": "planned_benchmark_aligned_evaluation",
            "output": result,
        }

        return {
            "planner_output": result,
            "selected_metrics": selected_metrics,
            "question_type": question_type,
            "risk_level": risk_level,
            "evaluation_plan": evaluation_plan,
            "agronomic_categories": agronomic_categories,
            "benchmark_metric_mapping": benchmark_metric_mapping,
            "trace": state.get("trace", []) + [trace_entry],
        }