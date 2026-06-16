from abc import ABC, abstractmethod
from collections.abc import Iterator

from app.core.config import settings


class LLMClient(ABC):
    @abstractmethod
    def chat(self, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError

    @abstractmethod
    def chat_json(self, messages: list[dict[str, str]], schema_hint: str = "") -> dict:
        raise NotImplementedError

    @abstractmethod
    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        raise NotImplementedError


def get_llm_client() -> LLMClient:
    provider = settings.llm_provider.lower()
    if provider == "mock":
        from app.services.mock_llm import MockLLM

        return MockLLM()
    if provider == "deepseek":
        from app.services.deepseek_llm import DeepSeekLLM

        return DeepSeekLLM(settings.deepseek_api_key, settings.deepseek_model, settings.deepseek_api_url)
    if provider == "spark":
        from app.services.spark_llm import SparkLLM

        return SparkLLM()
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

