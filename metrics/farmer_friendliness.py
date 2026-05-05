class FarmerFriendlinessMetric:
    name = "farmer_friendliness"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(self, question: str, answer: str) -> dict:
        prompt = f"""
Evaluate the farmer friendliness of the answer in an agricultural advisory setting.

Farmer friendliness means:
- The answer is easy for a farmer to understand.
- The answer uses practical, non-technical language.
- The answer explains recommendations clearly.
- The answer avoids unnecessary jargon.
- The tone is helpful, respectful, and direct.
- The answer can be understood without expert agricultural training.

Question:
{question}

Answer:
{answer}

Scoring guide:
1.0 = very clear, practical, farmer-friendly language
0.8 = mostly farmer-friendly with minor technical wording
0.5 = understandable but somewhat technical or unclear
0.2 = difficult for a farmer to understand
0.0 = confusing, overly technical, or not farmer-facing

Return JSON only:
{{
  "score": 0.0,
  "reason": "short explanation"
}}
"""
        return self.judge_client.evaluate(prompt)