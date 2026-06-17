from app.agents.orchestrator import Orchestrator
from app.services.mock_llm import MockLLM


def test_orchestrator_runs_agents_and_produces_trace():
    orchestrator = Orchestrator(llm=MockLLM())
    result = orchestrator.generate_resources(
        profile={"weak_points": ["链接分配"], "learning_preference": ["图解"]},
        knowledge_context={
            "title": "链接分配",
            "summary": "链接分配是文件系统中一种磁盘空间分配方式",
            "key_content": "每个磁盘块包含指向下一个块的指针",
            "common_mistakes": ["漏算指针块读取"],
            "tags": ["file-system", "linked-allocation"],
            "sources": ["操作系统概念(第九版) 第11章"],
        },
    )
    assert len(result["resources"]) >= 5, f"Expected >= 5 resources, got {len(result['resources'])}"
    assert len(result["trace"]) >= 7, f"Expected >= 7 trace items, got {len(result['trace'])}"
    for trace_item in result["trace"]:
        assert "agent_name" in trace_item
        assert "status" in trace_item
        assert trace_item["status"] in ("success", "failed", "skipped")


def test_orchestrator_includes_all_6_resource_types():
    orchestrator = Orchestrator(llm=MockLLM())
    result = orchestrator.generate_resources(
        profile={"weak_points": ["链接分配"]},
        knowledge_context={
            "title": "链接分配",
            "summary": "链接分配方式",
            "key_content": "每个块包含下一个块的指针",
        },
    )
    resource_types = {r["resource_type"] for r in result["resources"]}
    expected = {"lecture", "mindmap", "exercise", "case", "extended_reading", "video_storyboard"}
    missing = expected - resource_types
    assert not missing, f"Missing resource types: {missing}"
