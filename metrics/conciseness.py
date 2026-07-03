class ConcisenessMetric:
    name = "conciseness"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(self, question: str, answer: str) -> dict:
        prompt = f"""
Evaluate the conciseness and parsimony of the answer in an agricultural advisory setting.

Conciseness does NOT mean the shortest answer is always best.
It means the answer should be efficient, practical, and not unnecessarily complicated.

Important context rule:
- Do NOT penalize context-rich details when they are necessary for the farmer's decision and supported by available Context Information when present.
- Useful, supported context should be rewarded when it helps the farmer make a better decision.
- Penalize context that is irrelevant, repetitive, distracting, speculative (unsupported by Context Information), or not decision-supportive.

Evaluate whether the answer:
- Gives the necessary information without excessive length.
- Avoids repetition.
- Avoids unnecessary extra advice beyond the farmer's question.
- Avoids making the recommendation overly complicated.
- Keeps the guidance practical and easy to follow.
- Includes only the detail needed to make the answer understandable and useful.
- Does not remove important safety, timing, dosage, or context details just to be shorter.
- Prioritizes the most relevant actions instead of listing too many loosely related options.
- Avoids distracting context that does not improve the farmer's decision.
- Uses context efficiently rather than dumping all possible information.

Parsimony means:
- The recommendation should be as simple as possible while still being useful.
- The answer should not overload the farmer with too many unnecessary options.
- The answer should prioritize the most useful actions instead of listing everything possible.
- The answer should balance brevity with practical completeness.
- The answer should be readable and decision-focused.
- The answer should include rich context only when that context improves the advisory decision.

Question:
{question}

Answer:
{answer}

Scoring guide:
1.0 = concise, efficient, practical, context-aware when useful, and complete enough
0.8 = mostly concise with minor extra detail that does not reduce usability
0.5 = somewhat verbose, repetitive, or overly complicated but still useful
0.2 = very verbose, unfocused, overloaded, or includes distracting/non-actionable context
0.0 = confusing, bloated, repetitive, or difficult to act on

Return JSON only:
{{
  "score": 0.0,
  "reason": "short explanation"
}}
"""
        return self.judge_client.evaluate(prompt)