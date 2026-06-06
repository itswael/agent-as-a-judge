import time
from typing import List, Dict, Any

from src.graph.agent_judge_graph import AgentJudgeGraph
from src.export_results import ResultExporter


class FullDatasetEvaluator:
    def __init__(self, judge_client, delay_seconds: int = 2, n_repeats: int = 1):
        self.judge_client = judge_client
        self.delay_seconds = delay_seconds
        self.n_repeats = n_repeats
        self.graph = AgentJudgeGraph(judge_client).build()
        self.exporter = ResultExporter()

    def evaluate_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        initial_state = {
            "id": record["id"],
            "question": record["question"],
            "minimum_context_answer": record["minimum_context_answer"],
            "agricultural_chatbot_answer": record["agricultural_chatbot_answer"],
            "trace": [],
            "errors": [],
        }

        result = self.graph.invoke(initial_state)
        export_record = self.exporter.build_export_record(result)

        filename = f"trace_row_{record['id']}.json"
        output_path = self.exporter.save_json(export_record, filename)

        print(f"Completed row {record['id']} -> {output_path}")

        return export_record

    def evaluate_dataset(self, records: List[Dict[str, Any]], limit=None) -> List[Dict[str, Any]]:
        if limit is not None:
            records = records[:limit]

        all_results = []

        for record in records:
            try:
                result = self.evaluate_record(record)
                all_results.append(result)
                time.sleep(self.delay_seconds)

            except Exception as error:
                error_result = {
                    "id": record.get("id"),
                    "question": record.get("question"),
                    "error": str(error),
                }
                all_results.append(error_result)
                print(f"Failed row {record.get('id')}: {error}")

        self.exporter.save_json(
            {"results": all_results},
            "full_dataset_results.json"
        )

        return all_results