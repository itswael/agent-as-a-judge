from typing import Any, Dict


class ContextImpactAgent:
    name = "context_impact_agent"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state["question"]
        minimum_context_answer = state["minimum_context_answer"]
        agricultural_chatbot_answer = state["agricultural_chatbot_answer"]
        claims = state.get("claims", {})
        evidence_check = state.get("evidence_check", {})
        metric_results = state.get("metric_results", {})

        prompt = f"""
You are a Context Impact Analyzer Agent in an agricultural Agent-as-a-Judge framework.

Your task is to analyze how added agricultural context changes the chatbot response.

Main objective:
1. Identify how the agricultural chatbot answer differs from the minimum-context answer.
2. Identify which added context improves the response.
3. Determine how much the added context improves specificity and practical usefulness.
4. Identify any added context that is unnecessary, unsupported, vague, or risky.

Context categories to look for:
- soil_context
- weather_context
- crop_stage_context
- location_context
- timing_context
- dosage_context
- application_method_context
- risk_safety_context
- resource_availability_context
- economic_context
- pest_disease_context
- water_moisture_context
- nutrient_management_context

Question:
{question}

Answer A - Minimum Context Answer:
{minimum_context_answer}

Answer B - Agricultural Chatbot Answer:
{agricultural_chatbot_answer}

Extracted Claims:
{claims}

Evidence Check:
{evidence_check}

Metric Results:
{metric_results}

Return valid JSON only in this exact structure:
{{
  "response_change_summary": "explain how added context changed the agricultural chatbot answer compared to the minimum-context answer",
  "added_contexts": [
    {{
      "context_type": "soil_context/weather_context/crop_stage_context/location_context/timing_context/dosage_context/application_method_context/risk_safety_context/resource_availability_context/economic_context/pest_disease_context/water_moisture_context/nutrient_management_context",
      "context_detail": "specific context added in the agricultural chatbot answer",
      "used_effectively": true,
      "value_score": 0.0,
      "value_reason": "why this context adds or does not add value"
    }}
  ],
  "most_valuable_contexts": [
    {{
      "context_type": "context type",
      "reason": "why this context is most valuable"
    }}
  ],
  "specificity_improvement": {{
    "minimum_context_specificity": "short description",
    "agricultural_chatbot_specificity": "short description",
    "improvement_summary": "how context improved specificity",
    "specificity_gain_score": 0.0
  }},
  "practical_usefulness_improvement": {{
    "minimum_context_usefulness": "short description",
    "agricultural_chatbot_usefulness": "short description",
    "improvement_summary": "how context improved field-level usefulness",
    "usefulness_gain_score": 0.0
  }},
  "weak_or_unhelpful_contexts": [
    {{
      "context_detail": "context that is weak/unhelpful/risky/vague",
      "issue": "why it is weak or problematic"
    }}
  ],
  "overall_context_value_score": 0.0,
  "context_value_conclusion": "final conclusion about whether context improved the response and why"
}}
"""

        result = self.judge_client.evaluate(prompt)

        trace_entry = {
            "agent": self.name,
            "action": "analyzed_context_impact",
            "output": result,
        }

        return {
            "context_impact_analysis": result,
            "trace": state.get("trace", []) + [trace_entry],
        }