from typing import Any, Dict


class ContextImpactAgent:
    name = "context_impact_agent"

    def __init__(self, judge_client):
        self.judge_client = judge_client

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state["question"]
        minimum_context_answer = state["minimum_context_answer"]
        agricultural_chatbot_answer = state["agricultural_chatbot_answer"]

        claims = state.get("claims", {})
        evidence_check = state.get("evidence_check", {})
        metric_results = state.get("metric_results", {})

        prompt = f"""
You are a GATE Context Impact Analyzer Agent in an agricultural Agent-as-a-Judge framework.

Your task is to analyze how the context-rich agricultural chatbot answer differs from the minimum-context answer.

IMPORTANT:
- Do NOT rely on an explicit context information field.
- Do NOT require exact API values.
- Do NOT separately evaluate soil nitrogen, pH, sand, clay, daily rain, or seasonal rain values.
- Infer which broad GATE context category appears to have influenced the agricultural chatbot answer based on the answer content itself.
- Do not assume more context is always better.
- Penalize unnecessary, weak, speculative, distracting, or off-scope context usage.
- Evaluate whether context genuinely improves agricultural decision quality.
- Do NOT say context is missing just because it is not shown explicitly.
- The goal is to evaluate whether the answer appropriately uses available or inferred context, not whether the dataset exposes every context value.

GATE framework:

G = Ground-truth context:
- soil information as one whole block
- crop type
- latitude/longitude/location if mentioned
- seasonal weather information if mentioned

A = Action context:
- socioeconomic factors
- small-scale or large-scale farming
- resource availability
- affordability
- operational constraints

T = Temporal context:
- daily weather forecast
- today's date
- crop phenology
- crop growth stage
- timing-sensitive advice

E = End-value context:
- farmer goal
- biodiversity
- maximizing yield
- sustainability
- organic farming
- profit/cost reduction

Context utilization analysis:
- Check whether the agricultural chatbot appears to use available or inferred context properly.
- Identify which GATE categories were used well.
- Identify which GATE categories were underused.
- Identify which context usage appears overextended, speculative, vague, or off-scope.
- Do not treat the use of context as hallucination by default.
- Context use should be penalized only when it is irrelevant, unsupported by the answer, unsafe, speculative, or outside the farmer's question.
- If a context category is not relevant to the question, mark it as not needed rather than missing.

Your goals:
1. Compare the answer without rich context vs the answer with inferred GATE context.
2. Identify which GATE category appears to add the most value.
3. Explain how context changes:
  - specificity
  - practical usefulness
  - safety
  - agricultural decision quality
4. Identify weak, vague, unnecessary, speculative, or off-scope context usage.
5. Determine whether the answer would become weaker without this context.
6. Evaluate whether the context improves real agricultural decision support.
7. Evaluate whether context was appropriately utilized, underused, or overused.

Question:
{question}

Answer A - Minimum Context Answer:
{minimum_context_answer}

Answer B - Agricultural Chatbot Answer:
{agricultural_chatbot_answer}

Extracted Claims:
{claims}

Evidence Check:
{evidence_check}

Metric Results:
{metric_results}

For each GATE category, explain:
1. What recommendation changed because of this context?
2. Did this context improve:
   - specificity
   - practical usefulness
   - safety
   - faithfulness
   - agricultural decision quality
3. Would the answer become weaker without this context?
4. Did the context remain relevant and within scope?
5. Was the context used properly, underused, or overused?

Rank GATE categories based on:
- contribution to specificity
- contribution to practical usefulness
- contribution to safety
- contribution to agricultural decision quality

Return valid JSON only in this exact structure:

{{
  "without_context_summary": "what the minimum-context answer does and what it misses",

  "with_context_summary": "how the agricultural chatbot answer changes by using inferred GATE context",

  "response_change_summary": "direct comparison of how context changed the response",

  "gate_context_impact": {{

    "G": {{
      "used": true,
      "value_score": 0.0,
      "impact_on_response": "how Ground-truth context appears to change the answer",
      "decision_quality_impact": "how G improved agricultural decision support",
      "utilization_quality": "high/medium/low/not_needed",
      "value_reason": "why G context was or was not valuable"
    }},

    "A": {{
      "used": true,
      "value_score": 0.0,
      "impact_on_response": "how Action context appears to change the answer",
      "decision_quality_impact": "how A improved agricultural decision support",
      "utilization_quality": "high/medium/low/not_needed",
      "value_reason": "why A context was or was not valuable"
    }},

    "T": {{
      "used": true,
      "value_score": 0.0,
      "impact_on_response": "how Temporal context appears to change the answer",
      "decision_quality_impact": "how T improved agricultural decision support",
      "utilization_quality": "high/medium/low/not_needed",
      "value_reason": "why T context was or was not valuable"
    }},

    "E": {{
      "used": true,
      "value_score": 0.0,
      "impact_on_response": "how End-value context appears to change the answer",
      "decision_quality_impact": "how E improved agricultural decision support",
      "utilization_quality": "high/medium/low/not_needed",
      "value_reason": "why E context was or was not valuable"
    }}
  }},

  "context_utilization_analysis": {{
    "available_context_used": true,
    "utilization_quality": "high/medium/low",
    "properly_used_gate_contexts": [
      "G"
    ],
    "underused_gate_contexts": [
      "A"
    ],
    "overused_or_speculative_contexts": [
      "E"
    ],
    "context_utilization_reason": "explain whether the agricultural chatbot used context appropriately and whether it improved the answer"
  }},

  "most_valuable_gate_context": {{
    "category": "G/A/T/E",
    "reason": "why this context category appears to add the most value for this question"
  }},

  "context_value_ranking": [
    {{
      "category": "G/A/T/E",
      "rank": 1,
      "reason": "why ranked here"
    }}
  ],

  "specificity_improvement": {{
    "without_context_specificity": "specificity level of minimum-context answer",
    "with_context_specificity": "specificity level of context-rich answer",
    "improvement_summary": "how inferred GATE context improved specificity",
    "specificity_gain_score": 0.0
  }},

  "actionability_improvement": {{
    "without_context_actionability": "actionability level of minimum-context answer",
    "with_context_actionability": "actionability level of context-rich answer",
    "improvement_summary": "how inferred GATE context improved actionability",
    "actionability_gain_score": 0.0
  }},

  "decision_quality_improvement": {{
    "without_context_decision_quality": "quality of decision support without context",
    "with_context_decision_quality": "quality of decision support with inferred GATE context",
    "improvement_summary": "how context improved agricultural decision-making",
    "decision_quality_gain_score": 0.0
  }},

  "weak_or_unhelpful_context_usage": [
    {{
      "gate_category": "G/A/T/E",
      "issue": "which context use was weak, unnecessary, vague, speculative, distracting, or harmful"
    }}
  ],

  "overall_context_value_score": 0.0,

  "context_value_conclusion": "final conclusion on how inferred GATE context changed the answer and which category mattered most"
}}
"""

        result = self.judge_client.evaluate(prompt)

        trace_entry = {
            "agent": self.name,
            "action": "analyzed_gate_context_utilization_without_explicit_context",
            "output": result,
        }

        return {
            "context_impact_analysis": result,
            "trace": state.get("trace", []) + [trace_entry],
        }