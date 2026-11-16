"""Integration tests for User Story 2 (P2): Avatar Upload, Validation, and Removal Flow."""

import io
import pytest
from PIL import Image
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


def _make_image_file(format="JPEG", size=(300, 300), color=(100, 150, 200)):
    """Generate in-memory image for multipart upload."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf


def test_avatar_upload_unauthorized_fails(client):
    """Scenario: Uploading avatar without auth returns 401."""
    buf = _make_image_file()
    res = client.post("/api/profile/me/avatar", files={"file": ("test.jpg", buf, "image/jpeg")})
    assert res.status_code == 401


def test_avatar_upload_and_delete_flow(client):
    """Scenario: Authenticated user uploads an avatar, verifies profile update, then removes it."""
    headers = {"Authorization": "Bearer test_elena"}
    buf = _make_image_file("PNG", size=(600, 400))

    # 1. Upload Avatar
    upload_res = client.post(
        "/api/profile/me/avatar",
        headers=headers,
        files={"file": ("avatar.png", buf, "image/png")},
    )
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    assert upload_data["width"] == 256
    assert upload_data["height"] == 256
    assert "/media/avatars/" in upload_data["avatarUrl"]
    assert upload_data["avatarUrl"].endswith(".webp")

    # 2. Verify Profile reflect new avatarUrl
    profile_res = client.get("/api/profile/me", headers=headers)
    assert profile_res.status_code == 200
    assert profile_res.json()["avatarUrl"] == upload_data["avatarUrl"]

    # 3. Verify Static Serving
    relative_path = upload_data["avatarUrl"].split("http://testserver")[-1]
    media_res = client.get(relative_path)
    assert media_res.status_code == 200
    assert len(media_res.content) > 0

    # 4. Remove Avatar
    delete_res = client.delete("/api/profile/me/avatar", headers=headers)
    assert delete_res.status_code == 200
    assert "/static/avatars/default.svg" in delete_res.json()["avatarUrl"]

    # 5. Re-check profile is back to default
    check_res = client.get("/api/profile/me", headers=headers)
    assert check_res.status_code == 200
    assert "/static/avatars/default.svg" in check_res.json()["avatarUrl"]


def test_avatar_upload_corrupt_file_fails(client):
    """Scenario: Uploading non-image file returns 400 Bad Request."""
    headers = {"Authorization": "Bearer test_frank"}
    fake_buf = io.BytesIO(b"This is definitely not an image")
    res = client.post(
        "/api/profile/me/avatar",
        headers=headers,
        files={"file": ("fake.jpg", fake_buf, "image/jpeg")},
    )
    assert res.status_code == 400
    assert res.json()["error"] == "invalid_image"
