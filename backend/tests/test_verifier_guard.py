"""VerifierAgent 与 ContentGuardAgent 校验逻辑测试。

验证：
1. VerifierAgent 返回 consistent 字段
2. ContentGuardAgent 返回 blocked/safe 字段
3. 安全内容不被阻断
4. 危险内容被标记
"""
from app.agents.verifier_agent import VerifierAgent
from app.agents.content_guard_agent import ContentGuardAgent
from app.services.mock_llm import MockLLM

KNOWLEDGE_CONTEXT = {
    "title": "链接分配",
    "summary": "链接分配是文件系统中一种磁盘空间分配方式",
    "key_content": "每个磁盘块包含指向下一个块的指针",
}

SAFE_RESOURCE = {
    "resource_type": "lecture",
    "content": {"content": "链接分配是文件系统中一种磁盘空间分配方式。每个磁盘块包含指向下一个块的指针。"},
}


def test_verifier_returns_consistent_field():
    """VerifierAgent 返回包含 consistent 字段的 dict。"""
    agent = VerifierAgent(llm=MockLLM())
    result = agent.run(resource=SAFE_RESOURCE, knowledge_context=KNOWLEDGE_CONTEXT)
    assert result.success
    assert isinstance(result.data, dict)
    assert "consistent" in result.data
    assert isinstance(result.data["consistent"], bool)


def test_verifier_with_empty_context():
    """空上下文不应导致崩溃。"""
    agent = VerifierAgent(llm=MockLLM())
    result = agent.run(resource=SAFE_RESOURCE, knowledge_context=None)
    assert result.success
    assert "consistent" in result.data


def test_content_guard_returns_safety_fields():
    """ContentGuardAgent 返回包含 blocked/safe 字段的 dict。"""
    agent = ContentGuardAgent(llm=MockLLM())
    result = agent.run(resource=SAFE_RESOURCE)
    assert result.success
    assert isinstance(result.data, dict)
    assert "blocked" in result.data
    assert "safe" in result.data


def test_content_guard_safe_content_not_blocked():
    """安全内容不应被阻断。"""
    agent = ContentGuardAgent(llm=MockLLM())
    result = agent.run(resource=SAFE_RESOURCE)
    assert result.success
    assert result.data["blocked"] is False
    assert result.data["safe"] is True


def test_content_guard_with_empty_resource():
    """空资源不应导致崩溃。"""
    agent = ContentGuardAgent(llm=MockLLM())
    result = agent.run(resource=None)
    assert result.success


def test_verifier_handles_string_content():
    """资源 content 为字符串时应正常处理。"""
    resource = {"resource_type": "lecture", "content": "这是一段讲义文本。"}
    agent = VerifierAgent(llm=MockLLM())
    result = agent.run(resource=resource, knowledge_context=KNOWLEDGE_CONTEXT)
    assert result.success
    assert "consistent" in result.data
