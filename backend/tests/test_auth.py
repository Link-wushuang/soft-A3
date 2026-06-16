def test_register_and_me(client):
    resp = client.post(
        "/api/auth/register",
        json={"username": "new_student", "password": "pass123456", "display_name": "新学生"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    data = me.json()
    assert data["username"] == "new_student"
    assert data["role"] == "student"


def test_login_demo_user(client):
    resp = client.post("/api/auth/login", json={"username": "demo_student", "password": "demo123456"})
    assert resp.status_code == 200
    assert resp.json()["token_type"] == "bearer"
    assert resp.json()["access_token"]


def test_login_rejects_wrong_password(client):
    resp = client.post("/api/auth/login", json={"username": "demo_student", "password": "wrong"})
    assert resp.status_code == 401
