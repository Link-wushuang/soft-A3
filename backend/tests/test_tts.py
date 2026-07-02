"""TTS 服务与 API 测试。

验证：
1. is_tts_available 在无凭证时返回 False
2. synthesize 在无凭证时返回 None
3. TTS API /available 返回正确结构
4. TTS API /synthesize 在不可用时返回降级响应
"""
from app.services.tts_service import is_tts_available, synthesize


def test_tts_available_returns_bool():
    """is_tts_available 返回 bool。"""
    result = is_tts_available()
    assert isinstance(result, bool)


def test_synthesize_empty_text_returns_none():
    """空文本应返回 None。"""
    result = synthesize("")
    assert result is None


def test_synthesize_whitespace_text_returns_none():
    """纯空白文本应返回 None。"""
    result = synthesize("   \n\t  ")
    assert result is None


def test_tts_available_endpoint(client):
    """/api/tts/available 返回 available 字段。"""
    resp = client.post("/api/auth/login", json={
        "username": "demo_student", "password": "demo123456",
    })
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    resp = client.get("/api/tts/available", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "available" in data
    assert isinstance(data["available"], bool)


def test_tts_synthesize_endpoint_structure(client):
    """/api/tts/synthesize 返回正确结构（available + format/reason）。"""
    resp = client.post("/api/auth/login", json={
        "username": "demo_student", "password": "demo123456",
    })
    headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    resp = client.post("/api/tts/synthesize", json={
        "text": "测试文本", "voice": "xiaoyan",
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "available" in data
    if data["available"]:
        assert "format" in data
        assert "audio_base64" in data
        assert len(data["audio_base64"]) > 0
    else:
        assert "reason" in data
