"""Integration tests for User Story 3 (P3): Public Read-Only Profile View."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.main import app
from src.models.base import Base, get_db

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_public_profile_view_success(client):
    """Scenario: Visitor views public profile without authentication."""
    # 1. User initializes and updates profile
    headers = {"Authorization": "Bearer sarah_connor"}
    client.put(
        "/api/profile/me",
        headers=headers,
        json={"displayName": "Sarah Connor", "bio": "No fate but what we make. 🤖"},
    )

    # 2. Public unauthenticated request
    res = client.get("/api/profile/sarah_connor")
    assert res.status_code == 200
    data = res.json()

    # Verify public fields are present
    assert data["username"] == "sarah_connor"
    assert data["displayName"] == "Sarah Connor"
    assert data["bio"] == "No fate but what we make. 🤖"
    assert "avatarUrl" in data

    # Verify private fields are NOT leaked
    assert "userId" not in data
    assert "id" not in data
    assert "createdAt" not in data
    assert "updatedAt" not in data


def test_public_profile_case_insensitive_lookup(client):
    """Scenario: Username lookup is case-insensitive."""
    headers = {"Authorization": "Bearer john_doe"}
    client.put(
        "/api/profile/me",
        headers=headers,
        json={"displayName": "John Doe", "bio": "Public bio"},
    )

    res = client.get("/api/profile/JOHN_DOE")
    assert res.status_code == 200
    assert res.json()["username"] == "john_doe"


def test_public_profile_not_found(client):
    """Scenario: Requesting a non-existent user returns 404 Not Found."""
    res = client.get("/api/profile/non_existent_ghost_user")
    assert res.status_code == 404
    data = res.json()
    assert data["error"] == "not_found"
    assert "non_existent_ghost_user" in data["message"]
