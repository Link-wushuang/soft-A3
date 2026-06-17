from app.agents.path_planner_agent import PathPlannerAgent
from app.services.mock_llm import MockLLM


def test_path_planner_returns_ordered_nodes():
    agent = PathPlannerAgent(llm=MockLLM())
    result = agent.run(
        profile={"weak_points": ["链接分配", "索引分配"], "time_budget": "2天"},
        knowledge_points=["文件系统基础", "连续分配", "链接分配", "索引分配", "文件分配方式对比"],
    )
    assert result.success
    nodes = result.data["nodes"]
    assert len(nodes) >= 3, f"Expected >= 3 nodes, got {len(nodes)}"
    for node in nodes:
        assert "knowledge_point_title" in node, f"Missing knowledge_point_title in {node}"
        assert "reason" in node, f"Missing reason in {node}"


def test_path_planner_nodes_are_ordered():
    agent = PathPlannerAgent(llm=MockLLM())
    result = agent.run(
        profile={"weak_points": ["索引分配"], "time_budget": "1天"},
        knowledge_points=["文件系统基础", "链接分配", "索引分配"],
    )
    assert result.success
    nodes = result.data["nodes"]
    titles = [n["knowledge_point_title"] for n in nodes]
    assert len(titles) == len(set(titles)), f"Duplicate titles: {titles}"
