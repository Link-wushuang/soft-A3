from collections.abc import Iterator

import httpx

from app.services.json_utils import safe_parse_json
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
        return safe_parse_json(content)

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        yield self.chat(messages)

