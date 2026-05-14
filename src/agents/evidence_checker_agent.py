from typing import Any, Dict


class EvidenceCheckerAgent:
    name = "evidence_checker_agent"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state["question"]
        claims = state.get("claims", {})
        planner_output = state.get("planner_output", {})

        prompt = f"""
You are an Evidence Checker Agent in an agricultural Agent-as-a-Judge framework.

Your task is to examine the extracted claims from two chatbot answers and identify:
- supported claims
- weakly supported claims
- unsupported claims
- risky claims
- vague claims
- missing context
- safety concerns

Important:
There is no external ground-truth answer available.
Use agricultural reasoning, the question intent, internal consistency, and practical farming logic.
Do not decide the final winner.
Do not assign final metric scores.
Only perform evidence-oriented checking.

Question:
{question}

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
    "evidence_summary": "short evidence-based assessment"
  }},
  "agricultural_chatbot_answer": {{
    "supported_claims": [
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
    "evidence_summary": "short evidence-based assessment"
  }},
  "comparative_evidence_summary": "short comparison of which answer has stronger evidence support and fewer risks"
}}
"""

        result = self.judge_client.evaluate(prompt)

        trace_entry = {
            "agent": self.name,
            "action": "checked_evidence",
            "output": result,
        }

        return {
            "evidence_check": result,
            "trace": state.get("trace", []) + [trace_entry],
        }