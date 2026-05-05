from src.judge_client import JudgeClient
from metrics.comparative_winner_reasoning import ComparativeWinnerReasoningMetric


def main():
    judge = JudgeClient()
    metric = ComparativeWinnerReasoningMetric(judge)

    question = "Should I apply urea to my rice crop before rain?"

    minimum_context_answer = (
        "Yes, you can apply urea before rain, but avoid heavy rain."
    )

    agricultural_chatbot_answer = (
        "Apply urea before light rain so it dissolves into the soil and reaches the rice root zone. "
        "Avoid applying before heavy rain because nitrogen may leach or run off. "
        "If the field is already saturated, wait until standing water drains before applying."
    )

    result = metric.evaluate(
        question,
        minimum_context_answer,
        agricultural_chatbot_answer,
    )

    print(result)


if __name__ == "__main__":
    main()