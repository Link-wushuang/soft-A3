"""End-to-end test: complete student learning cycle using demo_student."""

import time


def _login(client) -> str:
    resp = client.post(
        "/api/auth/login",
        json={"username": "demo_student", "password": "demo123456"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    return data["access_token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _wait_task(client, task_id: int, token: str, timeout: int = 30) -> dict:
    headers = _headers(token)
    for _ in range(timeout * 2):
        resp = client.get(f"/api/agent-tasks/{task_id}", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if data["status"] in ("completed", "failed"):
                return data
        time.sleep(0.5)
    raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")


PROFILE_DIMENSIONS = [
    "base_level",
    "learning_goal",
    "knowledge_state",
    "weak_points",
    "mastered_points",
    "learning_preference",
    "cognitive_style",
    "time_budget",
]


def test_full_student_learning_cycle(client):
    """Walk through every step a student takes, from login to analytics."""

    # 1. Login
    token = _login(client)
    h = _headers(token)

    # 2. GET /api/auth/me
    resp = client.get("/api/auth/me", headers=h)
    assert resp.status_code == 200
    me = resp.json()
    assert me["username"] == "demo_student"
    assert me["role"] == "student"

    # 3. Profile dialogue
    resp = client.post(
        "/api/profile/dialogue",
        json={
            "course_id": 1,
            "message": "我两天内想掌握文件分配方式，喜欢图解和例题，基础一般。",
        },
        headers=h,
    )
    assert resp.status_code == 200
    profile = resp.json()
    for dim in PROFILE_DIMENSIONS:
        assert dim in profile, f"Missing dimension: {dim}"
    assert profile["base_level"]
    assert isinstance(profile["weak_points"], list)
    assert isinstance(profile["learning_preference"], list)

    # 4. GET profile
    resp = client.get("/api/profile/1", headers=h)
    assert resp.status_code == 200
    stored = resp.json()
    for dim in PROFILE_DIMENSIONS:
        assert dim in stored, f"Missing dimension in stored profile: {dim}"

    # 5. Generate learning path
    resp = client.post(
        "/api/learning-path/generate",
        json={"course_id": 1},
        headers=h,
    )
    assert resp.status_code == 200
    path_data = resp.json()
    assert path_data["status"] == "active"
    assert len(path_data["nodes"]) >= 3, (
        f"Expected >= 3 path nodes, got {len(path_data['nodes'])}"
    )

    # 6. GET current learning path
    resp = client.get("/api/learning-path/current?course_id=1", headers=h)
    assert resp.status_code == 200
    current_path = resp.json()
    assert current_path["id"] == path_data["id"]
    assert len(current_path["nodes"]) == len(path_data["nodes"])

    # 7. GET knowledge points
    resp = client.get("/api/courses/1/knowledge-points", headers=h)
    assert resp.status_code == 200
    kps = resp.json()
    assert len(kps) > 0, "Expected knowledge points"
    kp_id = kps[0]["id"]

    # 8. Generate resources
    resp = client.post(
        "/api/resources/generate",
        json={"knowledge_point_id": kp_id},
        headers=h,
    )
    assert resp.status_code == 200
    gen_data = resp.json()
    assert "task_id" in gen_data
    task_id = gen_data["task_id"]
    assert task_id > 0

    # 9. Poll task until completed
    task = _wait_task(client, task_id, token)
    assert task["status"] == "completed", (
        f"Task failed: {task.get('error_message')}"
    )

    # 10. GET resources
    resp = client.get(
        f"/api/resources?knowledge_point_id={kp_id}", headers=h
    )
    assert resp.status_code == 200
    resources = resp.json()
    types = {r["resource_type"] for r in resources}
    assert len(types) >= 5, f"Expected >= 5 resource types, got {types}"

    # 11. GET exercises
    resp = client.get(
        f"/api/exercises?knowledge_point_id={kp_id}", headers=h
    )
    assert resp.status_code == 200
    exercises = resp.json()
    assert len(exercises) > 0, "Expected exercises"

    # 12. Submit answer
    ex = exercises[0]
    resp = client.post(
        f"/api/exercises/{ex['id']}/submit",
        json={"user_answer": "C"},
        headers=h,
    )
    assert resp.status_code == 200
    submit_data = resp.json()
    assert "evaluation" in submit_data
    assert "answer_record_id" in submit_data
    eval_data = submit_data["evaluation"]
    assert "is_correct" in eval_data
    assert "feedback" in eval_data

    # 13. GET analytics summary
    resp = client.get("/api/analytics/summary?course_id=1", headers=h)
    assert resp.status_code == 200
    summary = resp.json()
    assert "total_answers" in summary
    assert summary["total_answers"] >= 1
    assert "correctness_rate" in summary
    assert "weak_points" in summary
    assert "mastered_points" in summary
    assert "mistake_tag_counts" in summary
