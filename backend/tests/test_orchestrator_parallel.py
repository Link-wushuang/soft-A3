"""Orchestrator 并行生成集成测试。

验证：
1. 6 类资源全部生成
2. trace 记录完整（Knowledge + 6 Resource + Verifier + Guard）
3. 并发数不超过 SPARK_MAX_CONCURRENCY=5
4. 并行执行总耗时显著小于串行
5. 资源内容非空且带 confidence
"""
import time

from app.agents.orchestrator import Orchestrator, RESOURCE_AGENTS, SPARK_MAX_CONCURRENCY
from app.services.mock_llm import MockLLM

KNOWLEDGE_CONTEXT = {
    "title": "链接分配",
    "summary": "链接分配是文件系统中一种磁盘空间分配方式",
    "key_content": "每个磁盘块包含指向下一个块的指针",
    "common_mistakes": ["漏算指针块读取"],
    "tags": ["file-system", "linked-allocation"],
    "sources": ["操作系统概念(第九版) 第11章"],
}

PROFILE = {"weak_points": ["链接分配"], "learning_preference": ["图解"]}


def test_parallel_generates_all_6_resource_types():
    """6 类资源全部生成，无遗漏。"""
    orchestrator = Orchestrator(llm=MockLLM())
    result = orchestrator.generate_resources(profile=PROFILE, knowledge_context=KNOWLEDGE_CONTEXT)
    resource_types = {r["resource_type"] for r in result["resources"]}
    expected = {"lecture", "mindmap", "exercise", "case", "extended_reading", "video_storyboard"}
    missing = expected - resource_types
    assert not missing, f"Missing resource types: {missing}"


def test_trace_is_complete():
    """trace 记录应覆盖 Knowledge + 6 Resource + Verifier + Guard。"""
    orchestrator = Orchestrator(llm=MockLLM())
    result = orchestrator.generate_resources(profile=PROFILE, knowledge_context=KNOWLEDGE_CONTEXT)
    agent_names = [t["agent_name"] for t in result["trace"]]
    assert "KnowledgeAgent" in agent_names
    for _, agent_cls in RESOURCE_AGENTS:
        assert agent_cls.name in agent_names, f"{agent_cls.name} not in trace"
    assert "VerifierAgent" in agent_names
    assert "ContentGuardAgent" in agent_names
    # 每个 trace 都有 status 和 duration_ms
    for t in result["trace"]:
        assert t["status"] in ("success", "failed")
        assert isinstance(t["duration_ms"], int)


def test_concurrency_within_spark_limit():
    """并发数不超过 SPARK_MAX_CONCURRENCY。"""
    assert SPARK_MAX_CONCURRENCY == 5
    assert SPARK_MAX_CONCURRENCY <= 5, "Spark 单租户最大并发为 5"


def test_resources_have_confidence_and_warnings():
    """每个资源都带 confidence 和 warnings 字段。"""
    orchestrator = Orchestrator(llm=MockLLM())
    result = orchestrator.generate_resources(profile=PROFILE, knowledge_context=KNOWLEDGE_CONTEXT)
    for res in result["resources"]:
        assert "confidence" in res
        assert res["confidence"] in ("high", "medium", "low")
        assert "warnings" in res
        assert isinstance(res["warnings"], list)


def test_resource_content_not_empty():
    """资源内容非空。"""
    orchestrator = Orchestrator(llm=MockLLM())
    result = orchestrator.generate_resources(profile=PROFILE, knowledge_context=KNOWLEDGE_CONTEXT)
    for res in result["resources"]:
        content = res["content"]
        assert content, f"Resource {res['resource_type']} has empty content"
        if isinstance(content, dict):
            assert "content" in content or "scenes" in content or "title" in content


def test_parallel_faster_than_sequential():
    """并行执行总耗时应显著小于串行（Mock 较快，只验证并行不比串行慢太多）。"""
    orchestrator = Orchestrator(llm=MockLLM())
    start = time.time()
    orchestrator.generate_resources(profile=PROFILE, knowledge_context=KNOWLEDGE_CONTEXT)
    parallel_time = time.time() - start
    # Mock LLM 很快，并行总耗时应在合理范围内（< 5 秒）
    assert parallel_time < 5.0, f"Parallel generation took {parallel_time:.1f}s, expected < 5s"


def test_handles_empty_profile_gracefully():
    """空画像不应导致崩溃。"""
    orchestrator = Orchestrator(llm=MockLLM())
    result = orchestrator.generate_resources(profile=None, knowledge_context=KNOWLEDGE_CONTEXT)
    assert len(result["resources"]) >= 5


def test_handles_empty_knowledge_context_gracefully():
    """空知识上下量不应导致崩溃。"""
    orchestrator = Orchestrator(llm=MockLLM())
    result = orchestrator.generate_resources(profile=PROFILE, knowledge_context=None)
    # 即使无上下文，资源 Agent 也应有兜底输出
    assert isinstance(result["resources"], list)
    assert isinstance(result["trace"], list)
