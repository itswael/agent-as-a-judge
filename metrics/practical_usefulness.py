class PracticalUsefulnessMetric:
    name = "practical_usefulness"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(self, question: str, answer: str) -> dict:
        prompt = f"""
Evaluate the practical usefulness of the answer in an agricultural advisory setting.

Practical usefulness means:
- The answer provides clear and actionable farming guidance.
- The answer helps the farmer make a real field-level decision.
- The answer includes useful timing, method, dosage, placement, precautions, or next steps when relevant.
- The answer considers realistic farming constraints and field conditions.
- The answer is understandable and easy to follow for practical agricultural use.
- The answer explains recommendations clearly without unnecessary technical complexity.
- The answer should support direct real-world agricultural application.

Question:
{question}

Answer:
{answer}

Scoring guide:
1.0 = highly actionable, practical, and easy to apply
0.8 = mostly useful with good practical guidance
0.5 = somewhat useful but missing important practical clarity
0.2 = generic, difficult to apply, or weakly actionable
0.0 = not practically useful for farmer decision-making

Return JSON only:
{{
  "score": 0.0,
  "reason": "short explanation"
}}
"""
        return self.judge_client.evaluate(prompt)