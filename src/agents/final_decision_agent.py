import yaml
from typing import Any, Dict


class FinalDecisionAgent:
    name = "final_decision_agent"

    def __init__(self, judge_client, config_path: str = None):
        self.judge_client = judge_client
        self.config_path = config_path or "configs/metric_weights.yaml"
        self.weights = self._load_weights()

    def _load_weights(self) -> Dict[str, float]:
        """Load metric weights from YAML file."""
        with open(self.config_path, "r") as file:
            weights = yaml.safe_load(file)
        
        total = sum(weights.values())
        if round(total, 2) != 1.00:
            raise ValueError(f"Metric weights must sum to 1.0, got {total}")
        
        return weights

    def _compute_weighted_score(self, metric_results: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute weighted scores for both answers deterministically.
        Returns the weighted score and identifies winning answer.
        """
        # Extract scores from metric results
        scores = {
            "minimum_context_answer": {},
            "agricultural_chatbot_answer": {}
        }
        
        for metric_name, metric_data in metric_results.items():
            if metric_name == "comparative_winner_reasoning":
                continue  # Skip comparative metric for weighted scoring
            
            if isinstance(metric_data, dict):
                min_score = metric_data.get("minimum_context_answer", {}).get("score", 0.0)
                agro_score = metric_data.get("agricultural_chatbot_answer", {}).get("score", 0.0)
                
                scores["minimum_context_answer"][metric_name] = min_score
                scores["agricultural_chatbot_answer"][metric_name] = agro_score
        
        # Compute weighted sum for each answer
        weighted_scores = {
            "minimum_context_answer": 0.0,
            "agricultural_chatbot_answer": 0.0
        }
        
        for answer_type in ["minimum_context_answer", "agricultural_chatbot_answer"]:
            total_weighted = 0.0
            for metric_name, weight in self.weights.items():
                score = scores[answer_type].get(metric_name, 0.0)
                total_weighted += score * weight
            
            weighted_scores[answer_type] = round(total_weighted, 4)
        
        # Determine winner deterministically
        min_score = weighted_scores["minimum_context_answer"]
        agro_score = weighted_scores["agricultural_chatbot_answer"]
        
        if abs(min_score - agro_score) < 0.001:
            winner = "tie"
        elif min_score > agro_score:
            winner = "minimum_context_answer"
        else:
            winner = "agricultural_chatbot_answer"
        
        return {
            "weighted_scores": weighted_scores,
            "winner": winner
        }

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        question = state["question"]
        context_information = state.get("context_information", "")
        planner_output = state.get("planner_output", {})
        claims = state.get("claims", {})
        evidence_check = state.get("evidence_check", {})
        metric_results = state.get("metric_results", {})
        context_impact_analysis = state.get("context_impact_analysis", {})

        # Compute weighted scores deterministically
        weighted_scoring = self._compute_weighted_score(metric_results)
        
        # Get individual metric scores for reasoning
        metric_scores = {}
        for metric_name, metric_data in metric_results.items():
            if metric_name == "comparative_winner_reasoning":
                continue
            if isinstance(metric_data, dict):
                metric_scores[metric_name] = {
                    "minimum_context": metric_data.get("minimum_context_answer", {}).get("score", 0.0),
                    "agricultural_chatbot": metric_data.get("agricultural_chatbot_answer", {}).get("score", 0.0)
                }

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

IMPORTANT CONTEXT-GROUNDED DECISION RULES:
The agricultural chatbot answer may include weather, seasonal, soil, predicted soil type, and crop growth stage context.
1) Validate any added soil/weather/season/crop-stage/nutrient details against Context Information when available. Treat unverified details as speculative and do NOT reward them.
2) Reward added context only when it demonstrably improves specificity, actionability, or safety for the farmer's decision.
3) Penalize added context when it is unsupported by Context Information, contradicted, unsafe, vague, off-scope, or does not improve decision quality.
4) If both answers are similarly specific/actionable but the context-rich answer adds speculative or risky elements, prefer the minimum-context answer.
5) Use evidence from claims and evidence checking to corroborate or discount context-based assertions.

Decision criteria:
- Specificity is most important.
- Actionability is second most important.
- Conciseness is third most important.
- Context impact is central to this study.
- Prefer the answer where added context improves specificity, actionability, safety, and decision support.
- Penalize added context only if it is unsupported, vague, unsafe, unrelated, or contradicts the provided context.
- Do not choose an answer only because it is longer.
- Do not choose an answer only because it has more details.

Confidence rubric:
- ≥ 0.8 when at least three dimensions (specificity, actionability, safety, conciseness) clearly favor the winner and evidence checking shows minimal risks/speculation.
- 0.6–0.79 when most dimensions favor the winner but there are minor caveats.
- < 0.6 when dimensions conflict or speculative/unsupported context is present.

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

DETERMINISTIC WEIGHTED SCORES (computed from metric_scores using weights from metric_weights.yaml):
- Weighted Score for minimum_context_answer: {weighted_scoring['weighted_scores']['minimum_context_answer']}
- Weighted Score for agricultural_chatbot_answer: {weighted_scoring['weighted_scores']['agricultural_chatbot_answer']}
- Deterministic Winner (based on weighted scores): {weighted_scoring['winner']}

Individual Metric Scores:
{metric_scores}

Return valid JSON only in this exact structure:
{{
  "winner": "minimum_context_answer/agricultural_chatbot_answer/tie",
  "confidence": 0.0,
  "final_reason": "clear explanation of why this answer is better",
    "interpretation": "succinct, plain-language justification aligned with expected interpretation",
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