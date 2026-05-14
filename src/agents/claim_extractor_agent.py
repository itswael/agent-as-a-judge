from typing import Any, Dict


class ClaimExtractorAgent:
    name = "claim_extractor_agent"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state["question"]
        minimum_context_answer = state["minimum_context_answer"]
        agricultural_chatbot_answer = state["agricultural_chatbot_answer"]

        prompt = f"""
You are a Claim Extractor Agent in an agricultural Agent-as-a-Judge framework.

Your task is to extract clear, checkable agricultural claims from two chatbot answers.

A claim is a statement that can be evaluated for correctness, usefulness, specificity, safety, or support.

Extract claims related to:
- fertilizer recommendations
- crop stage
- timing
- dosage or quantity
- method of application
- soil or water conditions
- pest or disease risks
- safety precautions
- expected crop outcome
- economic or yield impact
- any agricultural reasoning

Do not score the answers.
Do not decide the winner.
Only extract claims.

Question:
{question}

Answer A - Minimum Context Answer:
{minimum_context_answer}

Answer B - Agricultural Chatbot Answer:
{agricultural_chatbot_answer}

Return valid JSON only in this exact structure:
{{
  "minimum_context_claims": [
    {{
      "claim": "clear checkable claim",
      "claim_type": "fertilizer/timing/dosage/method/safety/crop_stage/soil/water/pest_disease/yield/general",
      "importance": "low/medium/high"
    }}
  ],
  "agricultural_chatbot_claims": [
    {{
      "claim": "clear checkable claim",
      "claim_type": "fertilizer/timing/dosage/method/safety/crop_stage/soil/water/pest_disease/yield/general",
      "importance": "low/medium/high"
    }}
  ],
  "claim_summary": "short comparison of the type and richness of claims in both answers"
}}
"""

        result = self.judge_client.evaluate(prompt)

        trace_entry = {
            "agent": self.name,
            "action": "extracted_claims",
            "output": result,
        }

        return {
            "claims": result,
            "trace": state.get("trace", []) + [trace_entry],
        }