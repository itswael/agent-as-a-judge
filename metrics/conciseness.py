class ConcisenessMetric:
    name = "conciseness"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(self, question: str, answer: str) -> dict:
        prompt = f"""
Evaluate the conciseness of the answer in an agricultural advisory setting.

Conciseness means:
- The answer is clear and focused.
- The answer avoids unnecessary repetition.
- The answer does not include unrelated agricultural information.
- The answer is not overly long for the farmer's question.
- Useful agricultural details should NOT be penalized if they help the farmer act.

Question:
{question}

Answer:
{answer}

Scoring guide:
1.0 = concise, clear, and complete
0.8 = mostly concise with minor extra detail
0.5 = understandable but somewhat verbose or repetitive
0.2 = overly long, repetitive, or unfocused
0.0 = confusing, bloated, or mostly unnecessary content

Return JSON only:
{{
  "score": 0.0,
  "reason": "short explanation"
}}
"""
        return self.judge_client.evaluate(prompt)