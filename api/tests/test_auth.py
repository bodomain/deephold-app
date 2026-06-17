"""Auth API tests."""

from fastapi.testclient import TestClient

from deephold_api.main import app

client = TestClient(app)


def test_login_invalid_credentials() -> None:
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrong",
        },
    )
    assert response.status_code == 401


def test_login_and_me() -> None:
    # First create an admin user via CLI

    from deephold_api.create_admin import main as create_admin

    create_admin(["testadmin@example.com", "testpass123", "--name", "Test Admin"])

    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "testadmin@example.com",
            "password": "testpass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "testadmin@example.com"
    assert data["user"]["is_admin"] is True
    token = data["token"]

    # Get current user
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testadmin@example.com"

    # Cleanup
    from sqlalchemy import delete

    from deephold_api.db_session import get_sessionmaker
    from deephold_api.models import User

    session = get_sessionmaker()()
    session.execute(delete(User).where(User.email == "testadmin@example.com"))
    session.commit()
    session.close()


def test_me_without_token() -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_invalid_token() -> None:
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalidtoken123"},
    )
    assert response.status_code == 401
