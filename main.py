from src.judge_client import JudgeClient
from metrics.farmer_friendliness import FarmerFriendlinessMetric


def main():
    judge = JudgeClient()
    metric = FarmerFriendlinessMetric(judge)

    question = "Should I apply urea to my rice crop before rain?"
    answer = (
        "Apply urea before light rain so it can dissolve into the soil. "
        "Avoid applying before heavy rain because the fertilizer may wash away. "
        "If the field is already full of water, wait until it drains."
    )

    result = metric.evaluate(question, answer)
    print(result)


if __name__ == "__main__":
    main()