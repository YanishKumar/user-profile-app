"""Pydantic schemas for avatar upload and processing."""

from pydantic import Field
from src.schemas.profile import BaseSchema


class AvatarUploadResponse(BaseSchema):
    """Response returned upon successful avatar upload and normalization."""

    asset_id: str
    avatar_url: str
    file_size_bytes: int
    width: int = Field(default=256, json_schema_extra={"example": 256})
    height: int = Field(default=256, json_schema_extra={"example": 256})
