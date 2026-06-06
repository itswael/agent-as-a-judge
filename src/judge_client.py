import json
import os
import re

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


class JudgeClient:
    def __init__(
        self,
        model: str = "gpt-oss-120b",
        scoring_temperature: float = 0.0,
        reasoning_temperature: float = 0.2,
        seed: int = None,
        api_base: str = None,
        parallelize: bool = True,
    ):
        self.api_key = os.getenv("OPENAI_API_KEY", "ollama")
        self.scoring_temperature = scoring_temperature
        self.reasoning_temperature = reasoning_temperature
        self.seed = seed
        self.parallelize = parallelize

        # Default to local Ollama if no api_base provided
        if api_base is None:
            api_base = "http://10.242.84.63:11434/v1"

        self.llm_scoring = ChatOpenAI(
            model=model,
            temperature=scoring_temperature,
            openai_api_key=self.api_key,
            openai_api_base=api_base,
            seed=seed,
        )

        self.llm_reasoning = ChatOpenAI(
            model=model,
            temperature=reasoning_temperature,
            openai_api_key=self.api_key,
            openai_api_base=api_base,
            seed=seed,
        )

    def evaluate(self, prompt: str, use_reasoning: bool = False) -> dict:
        """Evaluate a prompt.

        Args:
            prompt: The prompt text to send to the judge.
            use_reasoning: If True, uses reasoning temperature (0.2).
                           If False, uses scoring temperature (0.0).
        """
        llm = self.llm_reasoning if use_reasoning else self.llm_scoring
        full_prompt = f"""
You are a strict agricultural answer evaluation judge.

Return valid JSON only.
Do not include markdown.
Do not include explanation outside JSON.

{prompt}
"""

        response = llm.invoke(full_prompt)
        content = response.content.strip()

        return self._parse_json(content)

    def evaluate_repeated(self, prompt: str, n_runs: int = 3) -> dict:
        """Run scoring evaluation multiple times and average numeric scores.

        Args:
            prompt: The prompt text to send to the judge.
            n_runs: Number of times to run the evaluation (default 3).
        """
        results = [self.evaluate(prompt, use_reasoning=False) for _ in range(n_runs)]

        # Average numeric scores per answer type
        score_sums = {"minimum_context_answer": 0.0, "agricultural_chatbot_answer": 0.0}
        count_min = 0
        count_agro = 0

        for r in results:
            if isinstance(r, dict):
                min_data = r.get("minimum_context_answer", {})
                agro_data = r.get("agricultural_chatbot_answer", {})
                if isinstance(min_data, dict) and "score" in min_data:
                    score_sums["minimum_context_answer"] += min_data["score"]
                    count_min += 1
                if isinstance(agro_data, dict) and "score" in agro_data:
                    score_sums["agricultural_chatbot_answer"] += agro_data["score"]
                    count_agro += 1

        averaged = dict(results[-1])  # start from last raw result

        if count_min > 0:
            avg_min = round(score_sums["minimum_context_answer"] / count_min, 4)
            if "minimum_context_answer" in averaged and isinstance(averaged["minimum_context_answer"], dict):
                averaged["minimum_context_answer"]["score"] = avg_min
            else:
                averaged["minimum_context_answer"] = {"score": avg_min}

        if count_agro > 0:
            avg_agro = round(score_sums["agricultural_chatbot_answer"] / count_agro, 4)
            if "agricultural_chatbot_answer" in averaged and isinstance(averaged["agricultural_chatbot_answer"], dict):
                averaged["agricultural_chatbot_answer"]["score"] = avg_agro
            else:
                averaged["agricultural_chatbot_answer"] = {"score": avg_agro}

        averaged["_repetition_count"] = n_runs
        return averaged

    def _parse_json(self, content: str) -> dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        json_match = re.search(r"\{.*\}", content, re.DOTALL)

        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {
            "score": 0.0,
            "reason": "Invalid JSON response from judge.",
            "raw_response": content,
        }