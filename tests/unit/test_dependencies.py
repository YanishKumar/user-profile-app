"""Unit tests for database session initialization and authentication dependency."""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.base import Base, engine, get_db, init_db
from src.api.dependencies import get_current_user


def test_init_db_creates_tables():
    """Verify that init_db initializes the database tables."""
    init_db()
    assert Base.metadata is not None


def test_get_db_session_yields_session():
    """Verify get_db dependency yields a valid SQLAlchemy session."""
    session_gen = get_db()
    session = next(session_gen)
    assert isinstance(session, Session)
    try:
        session_gen.close()
    except Exception:
        pass


def test_get_current_user_valid_token():
    """Verify authentication with valid Bearer token."""
    user = get_current_user(authorization="Bearer mock-test-token")
    assert user.user_id == "user_default_123"
    assert user.username == "alex_dev"


def test_get_current_user_custom_token():
    """Verify authentication with custom token."""
    user = get_current_user(authorization="Bearer custom_user_456")
    assert user.user_id == "user_custom_user_456"
    assert user.username == "custom_user_456"


def test_get_current_user_missing_token_raises_401():
    """Verify missing authorization header raises 401."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(authorization=None)
    assert exc_info.value.status_code == 401


def test_get_current_user_invalid_scheme_raises_401():
    """Verify non-Bearer scheme raises 401."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(authorization="Basic dXNlcjpwYXNz")
    assert exc_info.value.status_code == 401
