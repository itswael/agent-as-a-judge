from metrics.faithfulness import FaithfulnessMetric
from metrics.conciseness import ConcisenessMetric
from metrics.context_gain import ContextGainMetric
from metrics.practical_usefulness import PracticalUsefulnessMetric
from metrics.completeness import CompletenessMetric
from metrics.specificity import SpecificityMetric
from metrics.safety_risk_awareness import SafetyRiskAwarenessMetric
from metrics.comparative_winner_reasoning import ComparativeWinnerReasoningMetric


class EvaluationOrchestrator:
    def __init__(self, judge_client):
        self.judge_client = judge_client

        self.single_answer_metrics = [
            FaithfulnessMetric(self.judge_client),
            ConcisenessMetric(self.judge_client),
            PracticalUsefulnessMetric(self.judge_client),
            CompletenessMetric(self.judge_client),
            SpecificityMetric(self.judge_client),
            SafetyRiskAwarenessMetric(self.judge_client),
        ]

        self.context_gain_metric = ContextGainMetric(self.judge_client)
        self.comparative_winner_metric = ComparativeWinnerReasoningMetric(
            self.judge_client
        )

    def evaluate_single_answer_metric(self, metric, question, answer):
        try:
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