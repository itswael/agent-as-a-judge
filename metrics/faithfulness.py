class FaithfulnessMetric:
    name = "faithfulness"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(self, question: str, answer: str) -> dict:
        prompt = f"""
Evaluate the faithfulness of the answer in an agricultural advisory setting.

Faithfulness means:
- The answer remains grounded in the farmer's question.
- The answer directly addresses the agricultural problem being asked.
- The answer avoids unsupported agricultural claims.
- The answer does not invent facts, crop conditions, soil values, weather details, or pesticide/fertilizer recommendations.
- The answer avoids misleading or exaggerated certainty.
- The answer stays aligned with realistic agricultural practices and conditions.
- The answer should remain focused on the user's intent and avoid unrelated information.

Question:
{question}

Answer:
{answer}

Scoring guide:
1.0 = fully faithful, grounded, and directly aligned with the question
0.8 = mostly faithful with very minor unsupported assumptions
0.5 = partially faithful with some questionable or weakly relevant content
0.2 = many unsupported, misleading, or weakly aligned claims
0.0 = fabricated, unsafe, misleading, or unrelated advice

Return JSON only:
{{
  "score": 0.0,
  "reason": "short explanation"
}}
"""
        return self.judge_client.evaluate(prompt)