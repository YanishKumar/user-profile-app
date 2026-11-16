"""Integration tests for User Story 1 (P1 MVP): Profile View and Update Flow."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.main import app
from src.models.base import Base, get_db

# Use in-memory SQLite database with StaticPool for thread-safe test client access
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create all tables before each test and drop after."""
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Synchronous test client."""
    with TestClient(app) as test_client:
        yield test_client


def test_get_profile_unauthorized_fails(client):
    """Scenario: Requesting profile without auth returns 401."""
    response = client.get("/api/profile/me")
    assert response.status_code == 401


def test_get_or_create_profile_flow(client):
    """Scenario: First-time authenticated user fetches profile and receives initial defaults."""
    headers = {"Authorization": "Bearer test_alice"}
    response = client.get("/api/profile/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["userId"] == "user_test_alice"
    assert data["username"] == "test_alice"
    assert data["displayName"] == "test_alice"
    assert data["bio"] == ""
    assert "/static/avatars/default.svg" in data["avatarUrl"]


def test_update_profile_and_verify_persistence(client):
    """Scenario: Authenticated user updates bio and display name, then verifies persistence."""
    headers = {"Authorization": "Bearer test_bob"}
    update_payload = {
        "displayName": "Bob The Builder",
        "bio": "Can we build it? Yes we can! 🛠️",
    }
    update_res = client.put("/api/profile/me", headers=headers, json=update_payload)
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["displayName"] == "Bob The Builder"
    assert updated_data["bio"] == "Can we build it? Yes we can! 🛠️"

    # Re-fetch profile to confirm persistence
    get_res = client.get("/api/profile/me", headers=headers)
    assert get_res.status_code == 200
    fetched_data = get_res.json()
    assert fetched_data["displayName"] == "Bob The Builder"
    assert fetched_data["bio"] == "Can we build it? Yes we can! 🛠️"


def test_update_profile_bio_exceeding_limit_fails(client):
    """Scenario: Updating profile with bio > 500 characters returns 400 Bad Request."""
    headers = {"Authorization": "Bearer test_charlie"}
    invalid_payload = {
        "displayName": "Charlie",
        "bio": "X" * 501,
    }
    res = client.put("/api/profile/me", headers=headers, json=invalid_payload)
    assert res.status_code == 400
    data = res.json()
    assert data["error"] == "validation_error"


def test_update_profile_empty_display_name_fails(client):
    """Scenario: Updating profile with empty display name returns 400."""
    headers = {"Authorization": "Bearer test_dave"}
    invalid_payload = {
        "displayName": "",
        "bio": "Valid bio",
    }
    res = client.put("/api/profile/me", headers=headers, json=invalid_payload)
    assert res.status_code == 400


def test_serve_frontend_index_html(client):
    """Scenario: GET / serves frontend UI index.html with 200 OK."""
    res = client.get("/")
    assert res.status_code == 200
    assert "Personal Profile" in res.text
    assert "<form id=\"profileForm\"" in res.text
