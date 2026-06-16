from app.agents.profile_agent import ProfileAgent
from app.models import ProfileUpdateLog, StudentProfile


def _auth_header(client):
    resp = client.post("/api/auth/login", json={"username": "demo_student", "password": "demo123456"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_profile_agent_extracts_8_dimensions():
    agent = ProfileAgent()
    result = agent.run(user_message="我两天内想掌握文件系统，喜欢图解和例题。", context={})
    assert result.status == "success"
    data = result.data
    for key in [
        "base_level",
        "learning_goal",
        "knowledge_state",
        "weak_points",
        "mastered_points",
        "learning_preference",
        "cognitive_style",
        "time_budget",
    ]:
        assert key in data
    assert "evidence" in data


def test_profile_dialogue_api_updates_profile(client, test_db):
    headers = _auth_header(client)
    course = test_db.query(StudentProfile).first()
    assert course is None

    resp = client.post(
        "/api/profile/dialogue",
        json={"course_id": 1, "message": "我想两天内学会索引分配，喜欢图解和例题。"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["base_level"]
    assert data["learning_goal"]
    assert isinstance(data["weak_points"], list)
    assert isinstance(data["learning_preference"], list)

    profile = test_db.query(StudentProfile).first()
    assert profile is not None
    assert profile.course_id == 1
    assert test_db.query(ProfileUpdateLog).count() == 1


def test_profile_logs_api_returns_history(client):
    headers = _auth_header(client)
    client.post(
        "/api/profile/dialogue",
        json={"course_id": 1, "message": "我基础一般，想复习进程同步。"},
        headers=headers,
    )

    resp = client.get("/api/profile/logs?course_id=1", headers=headers)
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 1
    assert logs[0]["updated_by"] == "ProfileAgent"
