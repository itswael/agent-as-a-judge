class PracticalUsefulnessMetric:
    name = "practical_usefulness"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(self, question: str, answer: str) -> dict:
        prompt = f"""
Evaluate the practical usefulness of the answer in an agricultural advisory setting.

Practical usefulness means:
- The answer gives clear actions the farmer can follow.
- The answer includes useful timing, method, dosage, or next steps when relevant.
- The answer helps the farmer make a real field-level decision.
- The answer avoids being only theoretical or generic.
- The answer considers realistic farming constraints when possible.

Question:
{question}

Answer:
{answer}

Scoring guide:
1.0 = highly actionable and directly useful in the field
0.8 = mostly actionable with useful guidance
0.5 = somewhat useful but missing important practical details
0.2 = mostly generic or difficult to apply
0.0 = not useful for farmer decision-making

Return JSON only:
{{
  "score": 0.0,
  "reason": "short explanation"
}}
"""
        return self.judge_client.evaluate(prompt)