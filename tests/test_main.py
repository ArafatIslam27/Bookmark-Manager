from fastapi.testclient import TestClient
from bookmark_manager.main import app

client = TestClient(app)

def test_read_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "Bookmark Manager"}

def test_create_and_read_bookmark():
    # Create a new bookmark (post request)
    payload = {
        "title": "Test Bookmark",
        "url": "https://example.com"
    }
    post_response = client.post("/bookmarks/", json=payload)
    assert post_response.status_code == 201

    data = post_response.json()
    assert data["title"] == "Test Bookmark"
    assert "id" in data

    # Read the bookmarks (get request)
    get_response = client.get("/bookmarks/")
    assert get_response.status_code == 200
    assert len(get_response.json()) >= 1