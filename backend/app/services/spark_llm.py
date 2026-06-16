import json
from collections.abc import Iterator

from app.core.config import settings
from app.services.llm_client import LLMClient


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
            )
        return self._spark

    def chat(self, messages: list[dict[str, str]]) -> str:
        from sparkai.core.messages import ChatMessage

        spark_messages = [ChatMessage(role=item["role"], content=item["content"]) for item in messages]
        result = self._client().generate([spark_messages])
        return result.generations[0][0].text

    def chat_json(self, messages: list[dict[str, str]], schema_hint: str = "") -> dict:
        return json.loads(self.chat(messages))

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        yield self.chat(messages)
