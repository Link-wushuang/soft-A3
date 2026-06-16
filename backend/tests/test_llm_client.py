import pytest

from app.core.config import settings
from app.services.llm_client import get_llm_client
from app.services.mock_llm import MockLLM


def test_default_llm_provider_is_mock_in_tests():
    assert settings.llm_provider == "mock"
    assert isinstance(get_llm_client(), MockLLM)


def test_mock_llm_returns_profile_json():
    llm = MockLLM()
    data = llm.chat_json(
        [{"role": "user", "content": "我两天内想学会文件系统，喜欢图解和例题。"}],
        schema_hint="profile",
    )
    expected_keys = {
        "base_level",
        "learning_goal",
        "knowledge_state",
        "weak_points",
        "mastered_points",
        "learning_preference",
        "cognitive_style",
        "time_budget",
        "confidence",
        "evidence",
        "profile_change_reason",
    }
    assert expected_keys <= set(data)


def test_mock_llm_stream_yields_text():
    llm = MockLLM()
    chunks = list(llm.stream([{"role": "user", "content": "讲解索引分配"}]))
    assert chunks
    assert "".join(chunks)


def test_deepseek_client_posts_chat_completion(monkeypatch):
    from app.services.deepseek_llm import DeepSeekLLM

    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": '{"ok": true}'}}]}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("httpx.post", fake_post)
    llm = DeepSeekLLM(api_key="test-key", model="deepseek-v4-pro", api_url="https://example.test/chat")
    assert llm.chat_json([{"role": "user", "content": "hi"}]) == {"ok": True}
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["json"]["model"] == "deepseek-v4-pro"


def test_unknown_provider_raises(monkeypatch):
    monkeypatch.setattr(settings, "llm_provider", "unknown")
    with pytest.raises(ValueError):
        get_llm_client()
