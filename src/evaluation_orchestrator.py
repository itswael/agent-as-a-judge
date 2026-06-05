from metrics.faithfulness import FaithfulnessMetric
from metrics.conciseness import ConcisenessMetric
from metrics.context_gain import ContextGainMetric
from metrics.actionability import ActionabilityMetric
from metrics.specificity import SpecificityMetric
from metrics.safety_risk_awareness import SafetyRiskAwarenessMetric
from metrics.comparative_winner_reasoning import ComparativeWinnerReasoningMetric


class EvaluationOrchestrator:
    def __init__(self, judge_client, n_repeats: int = 1):
        self.judge_client = judge_client
        self.n_repeats = n_repeats

        self.single_answer_metrics = [
            FaithfulnessMetric(self.judge_client),
            ConcisenessMetric(self.judge_client),
            ActionabilityMetric(self.judge_client),
            SpecificityMetric(self.judge_client),
            SafetyRiskAwarenessMetric(self.judge_client),
        ]

        self.context_gain_metric = ContextGainMetric(self.judge_client)
        self.comparative_winner_metric = ComparativeWinnerReasoningMetric(
            self.judge_client
        )

    def evaluate_single_answer_metric(self, metric, question, answer):
        try:
            if self.n_repeats > 1:
                # For scoring metrics, run multiple times and average
                results = []
                for _ in range(self.n_repeats):
                    result = metric.evaluate(question, answer)
                    results.append(result)
                
                score_sums = {"minimum_context_answer": 0.0, "agricultural_chatbot_answer": 0.0}
                count_min = 0
                count_agro = 0
                
                for r in results:
                    if isinstance(r, dict):
                        min_data = r.get("minimum_context_answer", {})
                        agro_data = r.get("agricultural_chatbot_answer", {})
                        if isinstance(min_data, dict) and "score" in min_data:
                            score_sums["minimum_context_answer"] += min_data["score"]
                            count_min += 1
                        if isinstance(agro_data, dict) and "score" in agro_data:
                            score_sums["agricultural_chatbot_answer"] += agro_data["score"]
                            count_agro += 1
                
                averaged = dict(results[-1])
                if count_min > 0:
                    avg_min = round(score_sums["minimum_context_answer"] / count_min, 4)
                    if "minimum_context_answer" in averaged and isinstance(averaged["minimum_context_answer"], dict):
                        averaged["minimum_context_answer"]["score"] = avg_min
                if count_agro > 0:
                    avg_agro = round(score_sums["agricultural_chatbot_answer"] / count_agro, 4)
                    if "agricultural_chatbot_answer" in averaged and isinstance(averaged["agricultural_chatbot_answer"], dict):
                        averaged["agricultural_chatbot_answer"]["score"] = avg_agro
                averaged["_repetition_count"] = self.n_repeats
                return averaged
            else:
                return metric.evaluate(question, answer)
        except Exception as error:
            return {
                "score": 0.0,
                "reason": f"Metric evaluation failed: {str(error)}",
            }

    def evaluate_pairwise_metric(
        self,
        metric,
        question,
        minimum_context_answer,
        agricultural_chatbot_answer,
    ):
        try:
            # Pairwise/reasoning metrics keep temperature=0.2, no repetition
            return metric.evaluate(
                question,
                minimum_context_answer,
                agricultural_chatbot_answer,
            )
        except Exception as error:
            return {
                "score": 0.0,
                "winner": "tie",
                "reason": f"Pairwise metric evaluation failed: {str(error)}",
            }

    def evaluate_row(self, record):
        question = record["question"]
        minimum_context_answer = record["minimum_context_answer"]
        agricultural_chatbot_answer = record["agricultural_chatbot_answer"]

        row_result = {
            "id": record["id"],
            "question": question,
            "minimum_context_answer": minimum_context_answer,
            "agricultural_chatbot_answer": agricultural_chatbot_answer,
            "metrics": {},
        }

        for metric in self.single_answer_metrics:
            row_result["metrics"][metric.name] = {
                "minimum_context_answer": self.evaluate_single_answer_metric(
                    metric,
                    question,
                    minimum_context_answer,
                ),
                "agricultural_chatbot_answer": self.evaluate_single_answer_metric(
                    metric,
                    question,
                    agricultural_chatbot_answer,
                ),
            }

        row_result["metrics"]["context_gain"] = self.evaluate_pairwise_metric(
            self.context_gain_metric,
            question,
            minimum_context_answer,
            agricultural_chatbot_answer,
        )

        row_result["metrics"]["comparative_winner_reasoning"] = (
            self.evaluate_pairwise_metric(
                self.comparative_winner_metric,
                question,
                minimum_context_answer,
                agricultural_chatbot_answer,
            )
        )

        return row_result

    def evaluate_dataset(self, records, limit=None):
        if limit is not None:
            records = records[:limit]

        results = []

        for record in records:
            try:
                result = self.evaluate_row(record)
                results.append(result)
                print(f"Evaluated record {record['id']}")
            except Exception as error:
                results.append(
                    {
                        "id": record.get("id"),
                        "error": str(error),
                    }
                )

        return results