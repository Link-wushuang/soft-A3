import json
from collections.abc import Iterator

import httpx

from app.services.llm_client import LLMClient


class DeepSeekLLM(LLMClient):
    def __init__(self, api_key: str, model: str, api_url: str):
        self.api_key = api_key
        self.model = model
        self.api_url = api_url

    def chat(self, messages: list[dict[str, str]]) -> str:
        response = httpx.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": self.model, "messages": messages, "temperature": 0.2},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def chat_json(self, messages: list[dict[str, str]], schema_hint: str = "") -> dict:
        content = self.chat(messages)
        return json.loads(_extract_json(content))

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        yield self.chat(messages)


def _extract_json(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:]
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end >= start:
        return stripped[start : end + 1]
    return stripped

