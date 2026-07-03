class ActionabilityMetric:
    name = "actionability"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(self, question: str, answer: str) -> dict:
        prompt = f"""
Evaluate the ACTIONABILITY of the answer in an agricultural advisory setting.

Actionability means:
- The answer helps the farmer make a real field-level decision.
- The answer provides clear, practical, implementable farming guidance.
- The answer provides enough implementation guidance for the farmer to carry out the recommendation when relevant.
- The answer considers realistic farming constraints and field conditions.
- The answer is understandable and easy to follow for practical agricultural use.
- The answer avoids vague advice that cannot be implemented.
- The answer uses available context effectively when that context improves the farmer's decision.

Important context rule:
- Reward context-rich answers only when the added context improves timing, safety, field relevance, operational feasibility, or decision quality AND is supported by available Context Information when present.
- Do NOT penalize an answer merely because it uses more context.
- Penalize added context when it is irrelevant, speculative (unsupported by Context Information), unrealistic, unsafe, off-scope, repetitive, or disconnected from the farmer's decision.
- Context should make the recommendation easier to apply, not just longer.

Evaluate the 4R agricultural decision components when relevant:
- Right Source: Does the answer specify the correct type or source of input, such as fertilizer, pesticide, seed, irrigation, or management action?
- Right Rate/Amount: Does the answer mention the correct amount, dosage, rate, threshold, or quantity when needed?
- Right Time: Does the answer specify the appropriate timing, crop stage, date window, weather window, or application timing?
- Right Place: Does the answer indicate where or how the input/action should be applied, such as soil placement, foliar spray, root zone, field location, or affected crop area?

Do not require all 4Rs when they are not relevant to the question.
If an R is relevant and missing, reduce the score.

Check:
- Can the farmer understand what action to take?
- Can the farmer understand when to take the action?
- Can the farmer understand how much to apply or what threshold to use when relevant?
- Can the farmer understand how or where to apply the recommendation when relevant?
- Does the answer include relevant follow-up actions when needed?
- Does any added context improve practical decision-making?
- Does the answer avoid adding unnecessary recommendations that distract from the farmer's question?

Question:
{question}

Answer:
{answer}

Scoring guide:
1.0 = highly actionable, practical, context-aware when useful, and covers all relevant 4Rs
0.8 = mostly actionable with good practical guidance and minor missing implementation detail
0.5 = somewhat useful but missing important practical clarity, relevant 4Rs, or effective context use
0.2 = generic, difficult to apply, weakly actionable, or poorly connected to field conditions
0.0 = not practically useful for farmer decision-making

Return JSON only:
{{
  "score": 0.0,
  "reason": "short explanation including actionability, relevant 4Rs, and whether context improved practical decision-making"
}}
"""
        return self.judge_client.evaluate(prompt)