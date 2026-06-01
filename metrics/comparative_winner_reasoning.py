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
- Answer B: agricultural chatbot answer with more agricultural context

Use ONLY these four evaluation dimensions:
1. Specificity
2. Actionability
3. Safety and risk awareness
4. Conciseness and parsimony

Important:
- Do NOT choose the longer answer just because it has more context.
- Do NOT penalize a context-rich answer if the added context improves agricultural decision-making.
- Reward context-rich reasoning when it improves actionability, timing, safety, specificity, or field relevance.
- Penalize context only when it is irrelevant, speculative, unsafe, off-scope, repetitive, or not decision-supportive.
- Prefer the answer that gives the farmer the better final decision support.

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
  "reason": "short explanation comparing completeness, actionability, safety, and conciseness"
}}

Scoring guide:
1.0 = winner is clearly better across the four dimensions
0.8 = winner is better with minor limitations
0.5 = both answers are similar or mixed
0.2 = weak difference between answers
0.0 = no meaningful comparison possible
"""
        return self.judge_client.evaluate(prompt)