from src.judge_client import JudgeClient
from metrics.specificity import SpecificityMetric


def main():
    judge = JudgeClient()
    metric = SpecificityMetric(judge)

    question = "Should I apply urea to my rice crop before rain?"
    answer = (
        "Apply urea before light rain so it dissolves into the soil and reaches the rice root zone. "
        "Avoid applying before heavy rain because nitrogen may leach or run off. "
        "If the field is already saturated, wait until standing water drains before applying."
    )

    result = metric.evaluate(question, answer)
    print(result)


if __name__ == "__main__":
    main()