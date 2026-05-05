class ComparativeWinnerReasoningMetric:
    name = "comparative_winner_reasoning"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(
        self,
        question: str,
        minimum_context_answer: str,
        agricultural_chatbot_answer: str,
    ) -> dict:
        prompt = f"""
Compare two agricultural chatbot answers and decide which one is better overall.

You are comparing:
- Answer A: chatbot answer with minimum context
- Answer B: agricultural chatbot answer with more context

Choose the better answer based on:
- faithfulness
- relevance
- conciseness
- context gain
- practical usefulness
- completeness
- farmer friendliness
- specificity
- safety and risk awareness

Question:
{question}

Answer A - Minimum Context Answer:
{minimum_context_answer}

Answer B - Agricultural Chatbot Answer:
{agricultural_chatbot_answer}

Return JSON only:
{{
  "score": 0.0,
  "winner": "minimum_context_answer/agricultural_chatbot_answer/tie",
  "reason": "short explanation of why this answer is better"
}}

Scoring guide:
1.0 = winner is clearly better
0.8 = winner is better with minor limitations
0.5 = both answers are similar or mixed
0.2 = weak difference between answers
0.0 = no meaningful comparison possible
"""
        return self.judge_client.evaluate(prompt)