import logging
import time
from collections.abc import Iterator

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
    def __init__(self):
        self._spark = None

    def _client(self):
        if self._spark is None:
            from sparkai.llm.llm import ChatSparkLLM

            self._spark = ChatSparkLLM(
                spark_api_url=settings.spark_api_url,
                spark_app_id=settings.spark_app_id,
                spark_api_key=settings.spark_api_key,
                spark_api_secret=settings.spark_api_secret,
                spark_llm_domain=settings.spark_model,
                streaming=False,
                request_timeout=120,
            )
        return self._spark

    def chat(self, messages: list[dict[str, str]]) -> str:
        from sparkai.core.messages import ChatMessage

        spark_messages = [ChatMessage(role=item["role"], content=item["content"]) for item in messages]
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                result = self._client().generate([spark_messages])
                return result.generations[0][0].text
            except Exception as exc:
                last_error = exc
                logger.warning("SparkLLM attempt %d/%d failed: %s", attempt + 1, MAX_RETRIES, exc)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
        raise RuntimeError(f"SparkLLM failed after {MAX_RETRIES} retries: {last_error}")

    def chat_json(self, messages: list[dict[str, str]], schema_hint: str = "") -> dict:
        content = self.chat(messages)
        result = safe_parse_json(content)
        if schema_hint in SCHEMA_TYPES and isinstance(result, dict):
            coerce_types(result, SCHEMA_TYPES[schema_hint])
        return result

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        yield self.chat(messages)
