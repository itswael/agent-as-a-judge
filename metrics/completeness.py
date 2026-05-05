class CompletenessMetric:
    name = "completeness"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(self, question: str, answer: str) -> dict:
        prompt = f"""
Evaluate the completeness of the answer in an agricultural advisory setting.

Completeness means:
- The answer covers all important parts of the farmer's question.
- The answer includes enough information for the farmer to understand what to do.
- The answer does not omit important steps, cautions, or conditions.
- The answer addresses timing, method, risk, and next steps when relevant.
- The answer is not just a partial or surface-level response.

Question:
{question}

Answer:
{answer}

Scoring guide:
1.0 = fully complete and covers all important aspects
0.8 = mostly complete with minor missing details
0.5 = partially complete but missing important guidance
0.2 = incomplete and leaves out major decision-making information
0.0 = does not meaningfully answer the question

Return JSON only:
{{
  "score": 0.0,
  "reason": "short explanation"
}}
"""
        return self.judge_client.evaluate(prompt)