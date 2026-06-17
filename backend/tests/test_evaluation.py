from app.agents.evaluation_agent import EvaluationAgent
from app.agents.reflection_agent import ReflectionAgent
from app.services.mock_llm import MockLLM


def test_evaluation_agent_scores_choice_correct():
    agent = EvaluationAgent(llm=MockLLM())
    result = agent.run(
        question="链接分配中读取第n个块需要几次I/O？",
        correct_answer="B",
        user_answer="B",
        question_type="choice",
    )
    assert result.success
    assert result.data["is_correct"] is True
    assert result.data["score"] == 1.0


def test_evaluation_agent_scores_choice_wrong():
    agent = EvaluationAgent(llm=MockLLM())
    result = agent.run(
        question="链接分配中读取第n个块需要几次I/O？",
        correct_answer="B",
        user_answer="A",
        question_type="choice",
    )
    assert result.success
    assert "is_correct" in result.data
    assert "feedback" in result.data
    assert "mistake_tags" in result.data


def test_evaluation_agent_short_answer_uses_llm():
    agent = EvaluationAgent(llm=MockLLM())
    result = agent.run(
        question="简述链接分配与索引分配的区别。",
        correct_answer="链接分配只能顺序访问，索引分配支持随机访问。",
        user_answer="索引分配使用索引块。",
        question_type="short_answer",
    )
    assert result.success
    assert "score" in result.data


def test_reflection_agent_updates_profile():
    agent = ReflectionAgent(llm=MockLLM())
    result = agent.run(
        evaluation_result={"is_correct": False, "mistake_tags": ["链接分配I/O计算"]},
        current_profile={"weak_points": [], "mastered_points": ["文件目录基础"]},
    )
    assert result.success
    assert "profile_changes" in result.data
    assert "change_reason" in result.data


def test_submit_answer_endpoint(client):
    resp = client.post("/api/auth/login", json={
        "username": "demo_student", "password": "demo123456",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/exercises?knowledge_point_id=1", headers=headers)
    assert resp.status_code == 200
    exercises = resp.json()
    assert len(exercises) > 0

    resp = client.post(
        f"/api/exercises/{exercises[0]['id']}/submit",
        json={"user_answer": "C"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "evaluation" in data
    assert "answer_record_id" in data
    assert data["evaluation"]["is_correct"] is True  # Mock returns True for correct choice answers


def test_answer_records_endpoint(client):
    resp = client.post("/api/auth/login", json={
        "username": "demo_student", "password": "demo123456",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/exercises/answer-records", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
