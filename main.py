from src.judge_client import JudgeClient
from metrics.practical_usefulness import PracticalUsefulnessMetric


def main():
    judge = JudgeClient()
    metric = PracticalUsefulnessMetric(judge)

    question = "Should I apply urea to my rice crop before rain?"
    answer = (
        "Apply urea before light rain so it dissolves into the soil and reaches the root zone. "
        "Do not apply before heavy rain because nitrogen may leach or run off. "
        "If the field is already saturated, wait until water drains before applying."
    )

    result = metric.evaluate(question, answer)
    print(result)


if __name__ == "__main__":
    main()