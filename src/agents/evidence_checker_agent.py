from typing import Any, Dict


class EvidenceCheckerAgent:
    name = "evidence_checker_agent"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state["question"]
        context_information = state.get("context_information", "")
        claims = state.get("claims", {})
        planner_output = state.get("planner_output", {})

        prompt = f"""
You are an Evidence Checker Agent in an agricultural Agent-as-a-Judge framework.

Your task is to examine extracted claims from two chatbot answers.

IMPORTANT CONTEXT-GROUNDED EVALUATION RULE:
The agricultural chatbot answer was generated using additional agricultural context.
Do NOT mark soil, weather, seasonal, location, crop-stage, date, or nutrient-related claims as unsupported if they are supported by the provided Context Information.

Minimum-context answer only had access to:
- latitude
- longitude
- crop name
- today's date

Agricultural chatbot answer had access to:
- latitude
- longitude
- crop name
- today's date
- OpenMeteo short-term weather forecast
- ECMWF seasonal forecast
- ISDA soil information
- predicted soil type
- predicted crop growth stage

Your job is to identify:
- claims supported by the provided context
- claims supported by general agronomic reasoning
- weakly supported claims
- unsupported claims
- risky claims
- vague claims
- missing context
- context-grounding strengths

Do not decide the final winner.
Do not assign final metric scores.
Only perform evidence-oriented checking.

Question:
{question}

Context Information:
{context_information}

Planner Output:
{planner_output}

Extracted Claims:
{claims}

Return valid JSON only in this exact structure:
{{
  "minimum_context_answer": {{
    "supported_claims": [
      "claim text"
    ],
    "context_supported_claims": [
      "claim text"
    ],
    "weakly_supported_claims": [
      "claim text"
    ],
    "unsupported_claims": [
      "claim text"
    ],
    "risky_claims": [
      "claim text"
    ],
    "vague_claims": [
      "claim text"
    ],
    "missing_context": [
      "missing detail"
    ],
    "context_grounding_summary": "how well this answer uses only minimum context",
    "evidence_summary": "short evidence-based assessment"
  }},
  "agricultural_chatbot_answer": {{
    "supported_claims": [
      "claim text"
    ],
    "context_supported_claims": [
      "claim text supported by weather/soil/seasonal/crop-stage context"
    ],
    "weakly_supported_claims": [
      "claim text"
    ],
    "unsupported_claims": [
      "claim text"
    ],
    "risky_claims": [
      "claim text"
    ],
    "vague_claims": [
      "claim text"
    ],
    "missing_context": [
      "missing detail"
    ],
    "context_grounding_summary": "how well this answer is grounded in provided agricultural context",
    "evidence_summary": "short evidence-based assessment"
  }},
  "comparative_evidence_summary": "short comparison of which answer has stronger evidence support and fewer risks",
  "context_grounded_faithfulness_summary": "explain whether the agricultural chatbot's added soil/weather/context details are supported by the Context Information"
}}
"""

        result = self.judge_client.evaluate(prompt)

        trace_entry = {
            "agent": self.name,
            "action": "checked_context_grounded_evidence",
            "output": result,
        }

        return {
            "evidence_check": result,
            "trace": state.get("trace", []) + [trace_entry],
        }