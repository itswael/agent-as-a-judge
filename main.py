from src.dataset_loader import DatasetLoader
from src.judge_client import JudgeClient
from src.graph.agent_judge_graph import AgentJudgeGraph
from src.export_results import ResultExporter


def main():

    loader = DatasetLoader("data/sample.xlsx")
    records = loader.load()

    judge_client = JudgeClient()

    graph = AgentJudgeGraph(
        judge_client
    ).build()

    exporter = ResultExporter()

    clean_summaries = []

    for record in records:

        location_context = record.get(
            "location_context", {}
        ) or {}

        initial_state = {

            "id": record["id"],

            "question": record["question"],

            "minimum_context_answer":
                record["minimum_context_answer"],

            "agricultural_chatbot_answer":
                record["agricultural_chatbot_answer"],

            "latitude":
                location_context.get("latitude"),

            "longitude":
                location_context.get("longitude"),

            "date":
                location_context.get("date"),

            "trace": [],

            "errors": [],
        }

        result = graph.invoke(initial_state)

        full_trace = exporter.build_full_trace_record(
            result
        )

        clean_summary = (
            exporter.build_clean_summary_record(
                result
            )
        )

        context_question_record = (
            exporter.build_context_question_record(
                result
            )
        )

        exporter.save_json(
            full_trace,
            f"trace_row_{record['id']}.json",
        )

        exporter.save_json(
            clean_summary,
            f"summary_row_{record['id']}.json",
        )

        exporter.save_json(
            context_question_record,
            f"context_questions_row_{record['id']}.json",
        )

        clean_summaries.append(clean_summary)

        final_decision = (
            clean_summary.get(
                "final_decision", {}
            ) or {}
        )

        context_impact = (
            clean_summary.get(
                "context_impact", {}
            ) or {}
        )

        print(f"Completed row {record['id']}")

        print(
            f"Winner: "
            f"{final_decision.get('winner')}"
        )

        print(
            f"Confidence: "
            f"{final_decision.get('confidence')}"
        )

        print(
            f"Context Value Score: "
            f"{context_impact.get('overall_context_value_score')}"
        )

        print(
            f"Most Valuable Context: "
            f"{(context_impact.get('most_valuable_gate_context', {}) or {}).get('category')}"
        )

        print(
            f"Summary file: "
            f"outputs/summary_row_{record['id']}.json"
        )

        print(
            f"Context file: "
            f"outputs/context_questions_row_{record['id']}.json"
        )

        print(
            f"Trace file: "
            f"outputs/trace_row_{record['id']}.json"
        )

        print("-" * 60)

    if clean_summaries:

        paths = exporter.save_summary_table(
            clean_summaries
        )

        print("\nSUMMARY FILES CREATED")

        print(paths["csv_path"])

        print(paths["excel_path"])

    else:

        print("\nNo successful rows to export.")


if __name__ == "__main__":
    main()