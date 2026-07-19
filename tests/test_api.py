import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth.jwt import get_current_user
from unittest.mock import patch

# Mock auth dependency
def override_get_current_user():
    return {"uid": "test_uid_123", "email": "test@test.com"}

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_list_places():
    response = client.get("/api/walkthrough/places")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_unauthenticated_protected_routes():
    # Clear overrides just in case
    app.dependency_overrides.clear()
    
    routes = [
        ("GET", "/api/walkthrough/mine"),
        ("POST", "/api/walkthrough/dummy_id/save"),
        ("POST", "/api/walkthrough/dummy_id/share")
    ]
    for method, path in routes:
        if method == "GET":
            response = client.get(path)
        else:
            response = client.post(path)
        # Auth dependency throws 403 or 401 (HTTPBearer default)
        assert response.status_code in [401, 403]

@pytest.fixture
def auth_client():
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client
    app.dependency_overrides.clear()

def test_my_walkthroughs_bloat_issue(auth_client):
    # This test asserts that the 'mine' endpoint only returns summary fields.
    # We will mock the database return to return a full bloated document, 
    # and expect the endpoint to have stripped it.
    from backend.database.crud import get_db
    import asyncio
    
    # We must be careful not to block the event loop in tests, but since TestClient is sync,
    # we can't easily insert into the real async mongo here without a wrapper.
    # Instead, we will mock `list_walkthroughs_for_user`.
    from unittest.mock import patch
    
    bloated_doc = {
        "walkthrough_id": "wt_1",
        "user_uid": "test_uid_123",
        "place": "P",
        "era": "E",
        "created_at": 1234,
        "stops": [
            {"image_url": "data:image/jpeg;base64,massive_base64_string_here", "narration_script": "Long text"}
        ]
    }
    
    with patch("backend.api.walkthrough.list_walkthroughs_for_user", return_value=[bloated_doc]):
        response = auth_client.get("/api/walkthrough/mine")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        item = data[0]
        # Assert NO full stop/image data is present (lightweight summary only)
        assert "stops" not in item, "My Walkthroughs endpoint is returning bloated stop/image data instead of summaries!"

def test_share_slug_collision_bug(auth_client):
    # Test that share_slug doesn't check for collision.
    # The prompt asks: "do not write a passing test for the unfixed My Walkthroughs bloat issue, 
    # or for share_slug's missing collision check — write tests that correctly fail against current known-broken behavior".
    # So we assert that it *should* handle collisions by retrying or returning a unique one, 
    # and it will fail because it just blindly updates the DB and ignores MongoDB duplicate key errors 
    # (actually MongoDB will raise an exception and 500).
    
    with patch("backend.api.walkthrough.get_walkthrough_by_id", return_value={"user_uid": "test_uid_123", "walkthrough_id": "wt_1"}):
        with patch("backend.api.walkthrough.update_share_slug", side_effect=[Exception("DuplicateKeyError"), None]):
            # It should handle the duplicate key and retry gracefully, returning a 200 with a new slug.
            # Currently it will crash with a 500.
            response = auth_client.post("/api/walkthrough/wt_1/share")
            assert response.status_code == 200, "Share endpoint crashed on slug collision without retrying!"

def test_missing_get_by_id_route():
    # Test that GET /api/walkthrough/{id} exists. It currently doesn't.
    with patch("backend.api.walkthrough.get_walkthrough_by_id", return_value={"walkthrough_id": "some_id"}):
        response = client.get("/api/walkthrough/some_id")
    # Will fail with 404 because the route is completely missing (not wired)
    # The requirement is that this route exists and returns 200 for a valid ID.
    # We just assert it doesn't return 404 (Not Found).
    assert response.status_code != 404, "GET /api/walkthrough/{id} route is missing!"
