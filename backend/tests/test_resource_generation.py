import time


def _get_token(client) -> str:
    resp = client.post("/api/auth/login", json={
        "username": "demo_student", "password": "demo123456",
    })
    return resp.json()["access_token"]


def _wait_for_task(client, task_id: int, token: str, timeout: int = 30) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    for _ in range(timeout * 2):
        resp = client.get(f"/api/agent-tasks/{task_id}", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if data["status"] in ("completed", "failed"):
                return data
        time.sleep(0.5)
    raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")


def test_generate_resources_returns_task_id(client):
    token = _get_token(client)
    resp = client.post(
        "/api/resources/generate",
        json={"knowledge_point_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "task_id" in data
    assert data["task_id"] > 0
    # Wait for background thread to finish so teardown doesn't race
    _wait_for_task(client, data["task_id"], token)


def test_get_resources_by_knowledge_point(client):
    token = _get_token(client)
    resp = client.post(
        "/api/resources/generate",
        json={"knowledge_point_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = resp.json()["task_id"]
    task = _wait_for_task(client, task_id, token)
    assert task["status"] == "completed", (
        f"Task failed: {task.get('error_message')}"
    )

    resp = client.get(
        "/api/resources?knowledge_point_id=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    resources = resp.json()
    types = {r["resource_type"] for r in resources}
    assert len(types) >= 5, f"Expected >=5 resource types, got {len(types)}: {types}"


def test_agent_task_trace_is_recorded(client):
    token = _get_token(client)
    resp = client.post(
        "/api/resources/generate",
        json={"knowledge_point_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = resp.json()["task_id"]
    _wait_for_task(client, task_id, token)

    resp = client.get(
        f"/api/agent-tasks/{task_id}/trace",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    traces = resp.json()
    assert len(traces) >= 7, f"Expected >=7 traces, got {len(traces)}"
    agent_names = {t["agent_name"] for t in traces}
    assert "KnowledgeAgent" in agent_names
    assert "LectureAgent" in agent_names
    assert "VerifierAgent" in agent_names
    assert "ContentGuardAgent" in agent_names
