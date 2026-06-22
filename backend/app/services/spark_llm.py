import logging
import time
from collections.abc import Iterator

import requests

from app.core.config import settings
from app.services.json_utils import coerce_types, safe_parse_json
from app.services.llm_client import LLMClient

logger = logging.getLogger(__name__)

SCHEMA_TYPES: dict[str, dict] = {
    "verifier": {"consistent": bool},
    "content_guard": {"blocked": bool, "safe": bool},
    "evaluation": {"score": float, "is_correct": bool},
    "profile": {"weak_points": list, "mastered_points": list, "learning_preference": list},
}

MAX_RETRIES = 3


class SparkLLM(LLMClient):
    def _call_api(self, messages: list[dict[str, str]], max_tokens: int = 2048) -> str:
        resp = requests.post(
            settings.spark_api_url,
            headers={
                "Authorization": f"Bearer {settings.spark_api_key}:{settings.spark_api_secret}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.spark_model,
                "messages": messages,
                "max_tokens": max_tokens,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def chat(self, messages: list[dict[str, str]]) -> str:
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                return self._call_api(messages)
            except Exception as exc:
                last_error = exc
                logger.warning("SparkLLM attempt %d/%d failed: %s", attempt + 1, MAX_RETRIES, exc)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(min(2 * (2 ** attempt), 10))

        logger.error("SparkLLM exhausted retries, falling back to MockLLM")
        try:
            from app.services.mock_llm import MockLLM
            return MockLLM().chat(messages)
        except Exception:
            raise RuntimeError(f"SparkLLM failed after {MAX_RETRIES} retries: {last_error}")

    def chat_json(self, messages: list[dict[str, str]], schema_hint: str = "") -> dict:
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                content = self._call_api(messages)
                parsed = safe_parse_json(content)
                if schema_hint in SCHEMA_TYPES and isinstance(parsed, dict):
                    coerce_types(parsed, SCHEMA_TYPES[schema_hint])
                return parsed
            except Exception as exc:
                last_error = exc
                logger.warning("SparkLLM attempt %d/%d failed: %s", attempt + 1, MAX_RETRIES, exc)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(min(2 * (2 ** attempt), 10))

        logger.error("SparkLLM exhausted retries for chat_json, falling back to MockLLM")
        try:
            from app.services.mock_llm import MockLLM
            return MockLLM().chat_json(messages, schema_hint)
        except Exception:
            raise RuntimeError(f"SparkLLM failed after {MAX_RETRIES} retries: {last_error}")

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        yield self.chat(messages)
