"""Health check test."""

from fastapi.testclient import TestClient

from deephold_api.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "deephold-api"
