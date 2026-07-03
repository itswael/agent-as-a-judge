class SpecificityMetric:
    name = "specificity"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def evaluate(self, question: str, answer: str) -> dict:
        prompt = f"""
Evaluate the SPECIFICITY of the answer in an agricultural advisory setting.

Specificity means:
- The answer directly addresses the farmer's exact question.
- The answer covers all important parts of the question.
- The answer includes concrete agricultural details instead of vague or generic guidance.
- The answer provides specific values, names, ranges, thresholds, stages, conditions, or examples when relevant.
- The answer makes clear which crop, problem, input, condition, or management issue it is referring to.
- The answer avoids broad statements that could apply to almost any crop, location, season, or farming situation.
- The answer does not leave important values or conditions vague when the question requires precision.

Focus ONLY on specificity and question coverage.
Do NOT evaluate full practical implementation here.
Do NOT judge whether the answer gives the best action plan.
Do NOT over-penalize missing implementation steps unless their absence makes the answer vague or incomplete for the specific question.

Evaluate whether the answer includes specific details such as:
- crop name or crop stage when relevant
- pest, disease, nutrient, soil, water, or management issue when relevant
- fertilizer, pesticide, seed, irrigation, or management input name when relevant
- dosage, rate, amount, threshold, or range when relevant
- timing, season, or application window when the question requires a specific time reference
- soil, weather, location, or field condition when relevant
- expected yield, quality, or outcome estimate when relevant
- specific conditions or constraints when they are needed to answer the question precisely

Context rule:
- Reward added context only when it makes the answer more specific to the farmer's question AND is supported by available Context Information when present.
- Do NOT reward context merely because it is present.
- Penalize context if it is vague, unrelated, speculative (unsupported by Context Information), excessive, or does not improve specificity.

Question:
{question}

Answer:
{answer}

Scoring guide:
1.0 = highly specific, covers the exact question, and includes precise relevant values/details
0.8 = mostly specific with minor missing detail
0.5 = partially specific but missing important values, conditions, or question components
0.2 = mostly vague, generic, incomplete, or weakly connected to the question
0.0 = does not meaningfully answer the question or is too generic to evaluate

Return JSON only:
{{
  "score": 0.0,
  "reason": "short explanation focusing only on specificity, concrete details, and coverage of the question"
}}
"""
        return self.judge_client.evaluate(prompt)