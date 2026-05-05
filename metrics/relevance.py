class RelevanceMetric:
    name = "relevance"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(self, question: str, answer: str) -> dict:
        prompt = f"""
Evaluate the relevance of the answer in an agricultural advisory setting.

Relevance means:
- The answer directly addresses the farmer's question.
- The answer stays focused on the crop, problem, or management decision asked.
- The answer avoids unrelated agricultural information.
- The answer does not give generic advice when the question asks for a specific action.

Question:
{question}

Answer:
{answer}

Scoring guide:
1.0 = fully relevant and directly answers the question
0.8 = mostly relevant with minor extra information
0.5 = partially relevant but misses part of the question
0.2 = weakly relevant or mostly generic
0.0 = off-topic or does not answer the question

Return JSON only:
{{
  "score": 0.0,
  "reason": "short explanation"
}}
"""
        return self.judge_client.evaluate(prompt)