from src.dataset_loader import DatasetLoader
from src.judge_client import JudgeClient
from src.graph.agent_judge_graph import AgentJudgeGraph
from src.export_results import ResultExporter


def main():
    loader = DatasetLoader("data/sample.xlsx")
    records = loader.load()

    judge_client = JudgeClient()
    graph = AgentJudgeGraph(judge_client).build()
    exporter = ResultExporter()

    clean_summaries = []

    for record in records[:3]:
        initial_state = {
            "id": record["id"],
            "question": record["question"],
            "minimum_context_answer": record["minimum_context_answer"],
            "agricultural_chatbot_answer": record["agricultural_chatbot_answer"],
            "trace": [],
            "errors": [],
        }

        result = graph.invoke(initial_state)

        full_trace = exporter.build_full_trace_record(result)
        clean_summary = exporter.build_clean_summary_record(result)

        exporter.save_json(full_trace, f"trace_row_{record['id']}.json")
        exporter.save_json(clean_summary, f"summary_row_{record['id']}.json")

        clean_summaries.append(clean_summary)

        print(f"Completed row {record['id']}")
        print(f"Winner: {clean_summary.get('winner')}")
        print(f"Confidence: {clean_summary.get('confidence')}")
        print(f"Context Value Score: {clean_summary.get('context_value_score')}")
        print("-" * 60)

    paths = exporter.save_summary_table(clean_summaries)

    print("\nSUMMARY FILES CREATED")
    print(paths["csv_path"])
    print(paths["excel_path"])


if __name__ == "__main__":
    main()