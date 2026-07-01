import json
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
# 重试退避：500/限流等偶发错误时快速重试，不做长退避（原 2/4/10s 过长）
RETRY_DELAYS = [1, 2, 3]


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
                    time.sleep(RETRY_DELAYS[attempt])

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
                    time.sleep(RETRY_DELAYS[attempt])

        logger.error("SparkLLM exhausted retries for chat_json, falling back to MockLLM")
        try:
            from app.services.mock_llm import MockLLM
            return MockLLM().chat_json(messages, schema_hint)
        except Exception:
            raise RuntimeError(f"SparkLLM failed after {MAX_RETRIES} retries: {last_error}")

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        """真流式输出：用 Spark OpenAI 兼容接口的 stream=true 逐 token 返回。

        失败时降级为一次性返回完整内容，保证调用方不中断。
        """
        try:
            yield from self._stream_sse(messages)
            return
        except Exception as exc:
            logger.warning("SparkLLM stream failed, fallback to one-shot: %s", exc)
        # 降级：一次性返回
        yield self.chat(messages)

    def _stream_sse(self, messages: list[dict[str, str]], max_tokens: int = 2048) -> Iterator[str]:
        """通过 SSE 逐 token 流式获取回复。

        Spark OpenAI 兼容接口支持 stream=true，响应为 SSE 格式：
        每行 `data: {json}`，json.choices[0].delta.content 为增量文本，
        结束标记 `data: [DONE]`。
        """
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
                "stream": True,
            },
            timeout=60,
            stream=True,
        )
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            # SSE 行格式：`data: {...}` 或 `data: [DONE]`
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                chunk = json.loads(data)
                choices = chunk.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta", {})
                content = delta.get("content") or ""
                if content:
                    yield content
            except json.JSONDecodeError:
                continue
