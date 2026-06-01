from typing import Any, Dict


class FinalDecisionAgent:
    name = "final_decision_agent"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state["question"]
        context_information = state.get("context_information", "")
        planner_output = state.get("planner_output", {})
        claims = state.get("claims", {})
        evidence_check = state.get("evidence_check", {})
        metric_results = state.get("metric_results", {})
        context_impact_analysis = state.get("context_impact_analysis", {})

        prompt = f"""
You are the Final Decision Agent in an agricultural Agent-as-a-Judge framework.

Your task is to give the final comparative judgment between two chatbot answers.

You are NOT answering the farmer's question.
You are judging which answer is better.

Use the following evidence:
1. Context Information
2. Planner output
3. Extracted claims
4. Evidence checking results
5. Metric scores and reasons
6. Context impact analysis

IMPORTANT CONTEXT-GROUNDED DECISION RULE:
The agricultural chatbot answer was generated with weather, seasonal, soil, predicted soil type, and crop growth stage context.
Do NOT penalize the agricultural chatbot answer for mentioning soil, weather, seasonal, nutrient, or crop-stage information if that information is supported by the Context Information.
Only penalize added context if it is unsupported, contradicted by the context, unsafe, vague, or irrelevant.

Decision criteria:
- Specificity is most important.
- Actionability is second most important.
- Conciseness is third most important.
- Context impact is central to this study.
- Prefer the answer where added context improves specificity, actionability, safety, and decision support.
- Penalize added context only if it is unsupported, vague, unsafe, unrelated, or contradicts the provided context.
- Do not choose an answer only because it is longer.
- Do not choose an answer only because it has more details.

Question:
{question}

Context Information:
{context_information}

Planner Output:
{planner_output}

Extracted Claims:
{claims}

Evidence Check:
{evidence_check}

Metric Results:
{metric_results}

Context Impact Analysis:
{context_impact_analysis}

Return valid JSON only in this exact structure:
{{
  "winner": "minimum_context_answer/agricultural_chatbot_answer/tie",
  "confidence": 0.0,
  "final_reason": "clear explanation of why this answer is better",
  "minimum_context_strengths": [
    "strength"
  ],
  "minimum_context_weaknesses": [
    "weakness"
  ],
  "agricultural_chatbot_strengths": [
    "strength"
  ],
  "agricultural_chatbot_weaknesses": [
    "weakness"
  ],
  "most_influential_metrics": [
    "metric_name"
  ],
  "most_valuable_contexts": [
    "context type or context detail"
  ],
  "context_impact_summary": "explain how added context changed answer quality",
  "specificity_change_summary": "explain how specificity changed between the two answers",
  "final_judgement_summary": "short final summary"
}}
"""

        result = self.judge_client.evaluate(prompt)

        trace_entry = {
            "agent": self.name,
            "action": "generated_context_grounded_final_decision",
            "output": result,
        }

        return {
            "final_decision": result,
            "trace": state.get("trace", []) + [trace_entry],
        }