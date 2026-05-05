class ContextGainMetric:
    name = "context_gain"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(
        self,
        question: str,
        minimum_context_answer: str,
        agricultural_chatbot_answer: str,
    ) -> dict:
        prompt = f"""
Evaluate the context gain between two agricultural answers.

Context Gain means the agricultural chatbot answer provides more useful agricultural context than the minimum-context answer.

Compare the two answers with respect to:
- crop-specific guidance
- soil-aware reasoning
- weather-aware reasoning
- growth-stage awareness
- local or field-specific recommendations
- timing, dosage, method, or practical constraints
- whether added context improves farmer decision-making

Question:
{question}

Answer A - Minimum Context Answer:
{minimum_context_answer}

Answer B - Agricultural Chatbot Answer:
{agricultural_chatbot_answer}

Scoring guide:
1.0 = Answer B provides significantly better context and decision support
0.8 = Answer B provides clearly better context
0.5 = Answer B provides some additional context, but improvement is limited
0.2 = Answer B provides very little useful context beyond Answer A
0.0 = Answer B provides no context gain or is worse than Answer A

Return JSON only:
{{
  "score": 0.0,
  "winner": "minimum_context_answer/agricultural_chatbot_answer/tie",
  "reason": "short comparison explanation"
}}
"""
        return self.judge_client.evaluate(prompt)