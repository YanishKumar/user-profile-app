"""API dependencies for database session injection and mock authentication."""

import re
from typing import Annotated, Generator
from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from src.models.base import get_db


class AuthenticatedUser:
    """Represents the currently authenticated user in request scope."""

    def __init__(self, user_id: str, username: str):
        self.user_id = user_id
        self.username = username

    def __repr__(self) -> str:
        return f"<AuthenticatedUser id={self.user_id} username={self.username}>"


def get_current_user(
    authorization: Annotated[str | None, Header()] = None
) -> AuthenticatedUser:
    """Extract and validate bearer authorization token.

    Supports:
    - Bearer mock-test-token -> default test user
    - Bearer <custom_user_id> -> test user with custom ID
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "message": "Missing or invalid authentication token"},
        )

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "unauthorized", "message": "Empty authorization bearer token"},
        )

    # Normalize token to user identity
    if token == "mock-test-token":
        user_id = "user_default_123"
        username = "alex_dev"
    else:
        # Sanitize token to create predictable username and user_id
        clean_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", token)[:32]
        user_id = f"user_{clean_name}"
        username = clean_name.lower()

    return AuthenticatedUser(user_id=user_id, username=username)


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]
