from src.judge_client import JudgeClient


def main():
    judge = JudgeClient()

    prompt = """
Evaluate the relevance of the answer.

Question:
What fertilizer should I use for rice?

Answer:
Use fertilizer based on soil test results and crop stage.

Return JSON only:
{
  "score": 0.0 to 1.0,
  "reason": "short explanation"
}
"""

    result = judge.evaluate(prompt)
    print(result)


if __name__ == "__main__":
    main()