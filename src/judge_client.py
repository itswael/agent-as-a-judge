import json
import os
import re

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


class JudgeClient:
    def __init__(self, model: str = "gpt-oss-120b"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        # temp
        # self.client_id = os.getenv("CLIENT_ID")
        # self.client_secret = os.getenv("CLIENT_SECRET")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is missing in .env")

        # if not self.client_id:
        #     raise ValueError("CLIENT_ID is missing in .env")

        # if not self.client_secret:
        #     raise ValueError("CLIENT_SECRET is missing in .env")

        self.llm = ChatOpenAI(
            model="gpt-oss-120b",
            temperature=0.2,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base="https://api.ai.it.ufl.edu/v1",
            # temp disabled
            # default_headers={
                # "Client-ID"    : os.getenv("CLIENT_ID"),
                # "Client-Secret": os.getenv("CLIENT_SECRET"),
            # }
        )

    def evaluate(self, prompt: str) -> dict:
        full_prompt = f"""
You are a strict agricultural answer evaluation judge.

Return valid JSON only.
Do not include markdown.
Do not include explanation outside JSON.

{prompt}
"""

        response = self.llm.invoke(full_prompt)
        content = response.content.strip()

        return self._parse_json(content)

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