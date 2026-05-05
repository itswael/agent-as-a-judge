from src.judge_client import JudgeClient
from metrics.context_gain import ContextGainMetric


def main():
    judge = JudgeClient()
    metric = ContextGainMetric(judge)

    question = "Should I apply urea to my rice crop before rain?"

    minimum_context_answer = (
        "Yes, you can apply urea before rain, but avoid heavy rain."
    )

    agricultural_chatbot_answer = (
        "Apply urea before light rain so it dissolves into the soil and becomes available "
        "to rice roots. Avoid applying before heavy rain because nitrogen may leach or run off. "
        "If your field is already saturated, wait until water drains before application."
    )

    result = metric.evaluate(
        question,
        minimum_context_answer,
        agricultural_chatbot_answer,
    )

    print(result)


if __name__ == "__main__":
    main()