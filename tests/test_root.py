"""
Tests for the root endpoint
"""
from fastapi.testclient import TestClient


def test_root_redirects_to_index(client: TestClient):
    """Test that GET / redirects to /static/index.html"""
    response = client.get("/", follow_redirects=False)
    
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_root_redirect_with_follow(client: TestClient):
    """Test that following the redirect from / leads to the static page"""
    response = client.get("/", follow_redirects=True)
    
    # The final URL should be the static page
    assert response.status_code == 200
