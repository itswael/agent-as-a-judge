class SpecificityMetric:
    name = "specificity"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(self, question: str, answer: str) -> dict:
        prompt = f"""
Evaluate the specificity of the answer in an agricultural advisory setting.

Specificity means:
- The answer includes concrete agricultural details.
- The answer avoids vague or generic advice.
- The answer includes timing, method, dosage, crop stage, soil condition, weather condition, or field condition when relevant.
- The answer gives enough detail to support a farmer's decision.
- The answer is specific to the question being asked.

Question:
{question}

Answer:
{answer}

Scoring guide:
1.0 = highly specific with strong agricultural details
0.8 = mostly specific with useful details
0.5 = somewhat specific but missing important details
0.2 = mostly vague or generic
0.0 = no useful specificity

Return JSON only:
{{
  "score": 0.0,
  "reason": "short explanation"
}}
"""
        return self.judge_client.evaluate(prompt)