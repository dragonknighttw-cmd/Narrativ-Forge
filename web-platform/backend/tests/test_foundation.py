from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_login_sets_http_only_cookie():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@narrativ.local", "password": "change-me"},
    )
    assert response.status_code == 200
    assert "nf_session" in response.cookies
    assert "httponly" in response.headers["set-cookie"].lower()

def test_me_requires_authentication():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_me_works_with_session_cookie():
    client.post(
        "/api/v1/auth/login",
        json={"email": "admin@narrativ.local", "password": "change-me"},
    )
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["role"] == "owner"
