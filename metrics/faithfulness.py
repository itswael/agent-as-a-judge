class FaithfulnessMetric:
    name = "faithfulness"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(self, question: str, answer: str) -> dict:
        prompt = f"""
Evaluate the faithfulness of the answer in an agricultural advisory setting.

Faithfulness means:
- The answer avoids unsupported agricultural claims.
- The answer does not invent facts, crop conditions, soil values, weather details, or pesticide/fertilizer recommendations.
- The answer does not exaggerate certainty.
- The answer stays grounded in the farmer's question.

Question:
{question}

Answer:
{answer}

Scoring guide:
1.0 = fully faithful, no unsupported claims
0.8 = mostly faithful, minor unsupported assumptions
0.5 = partially faithful, some unsupported claims
0.2 = weak faithfulness, many unsupported or questionable claims
0.0 = fabricated, misleading, or unsafe claims

Return JSON only:
{{
  "score": 0.0,
  "reason": "short explanation"
}}
"""
        return self.judge_client.evaluate(prompt)