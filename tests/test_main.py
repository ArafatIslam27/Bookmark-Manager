import pytest
from fastapi.testclient import TestClient
from bookmark_manager.main import app


@pytest.fixture
def client():
    # Using TestClient as a context manager triggers the app's lifespan
    # (startup/shutdown) events — without this, init_db() never runs and
    # your tables never get created, which is what caused the
    # "no such table: user" error.
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "Bookmark Manager"}


def test_create_and_read_bookmark(client):
    # Register a user
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpass123"},
    )

    # Log in to get a token
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a new bookmark
    payload = {"title": "Test Bookmark", "url": "https://example.com"}
    post_response = client.post("/bookmarks/", json=payload, headers=headers)
    assert post_response.status_code == 201

    data = post_response.json()
    assert data["title"] == "Test Bookmark"
    assert "id" in data

    # Read the bookmarks
    get_response = client.get("/bookmarks/", headers=headers)
    assert get_response.status_code == 200
    assert len(get_response.json()) >= 1