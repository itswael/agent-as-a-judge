from src.judge_client import JudgeClient
from metrics.relevance import RelevanceMetric


def main():
    judge = JudgeClient()
    metric = RelevanceMetric(judge)

    question = "Should I apply urea to my rice crop before rain?"
    answer = (
        "Apply urea before light rain so it can dissolve into the soil, "
        "but avoid applying before heavy rain because nitrogen may leach or run off."
    )

    result = metric.evaluate(question, answer)
    print(result)


if __name__ == "__main__":
    main()