"""Pydantic schemas for user profile requests and responses."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


def to_camel(snake_str: str) -> str:
    """Convert snake_case string to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.capitalize() for x in components[1:])


class BaseSchema(BaseModel):
    """Base schema configured for camelCase serialization and ORM mode."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class UpdateProfileRequest(BaseSchema):
    """Payload to update display name and biography."""

    display_name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="User display name (1-64 characters)",
    )
    bio: str = Field(
        default="",
        max_length=500,
        description="User biography (0-500 characters)",
    )


class ProfileResponse(BaseSchema):
    """Full authenticated profile view response."""

    id: str | None = None
    user_id: str
    username: str
    display_name: str
    bio: str
    avatar_url: str
    created_at: datetime | None = None
    updated_at: datetime


class PublicProfileResponse(BaseSchema):
    """Public read-only profile response."""

    username: str
    display_name: str
    bio: str
    avatar_url: str


class ErrorResponse(BaseSchema):
    """Standardized error response payload."""

    error: str
    message: str
    details: dict[str, Any] | None = None
