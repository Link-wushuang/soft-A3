def _login(client, username: str, password: str = "demo123456") -> dict[str, str]:
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_teacher_summary_includes_correctness_trend(client):
    student_headers = _login(client, "demo_student")
    exercises = client.get("/api/exercises?knowledge_point_id=1", headers=student_headers).json()
    assert exercises

    client.post(
        f"/api/exercises/{exercises[0]['id']}/submit",
        json={"user_answer": "C"},
        headers=student_headers,
    )

    teacher_headers = _login(client, "demo_teacher", "teacher123456")
    resp = client.get("/api/analytics/teacher-summary", headers=teacher_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "correctness_rate_trend" in data
    assert data["correctness_rate_trend"]
    first = data["correctness_rate_trend"][0]
    assert {"date", "correctness_rate", "total_answers"} <= set(first)


def test_student_cannot_access_teacher_summary(client):
    student_headers = _login(client, "demo_student")
    resp = client.get("/api/analytics/teacher-summary", headers=student_headers)
    assert resp.status_code == 403
