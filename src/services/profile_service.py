"""Profile business logic and biography sanitization service."""

import re
import html
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from src.models.profile import UserProfile
from src.models.avatar import AvatarAsset
from src.services.image_service import ImageService

DEFAULT_AVATAR_URL = "/static/avatars/default.svg"
MAX_BIO_LENGTH = 500


def sanitize_bio(raw_bio: str | None) -> str:
    """Sanitize biography text.

    - Strips leading and trailing whitespace
    - Collapses 3+ consecutive line breaks to max 2 (\n\n)
    - Strips HTML/script tags
    - Verifies character length <= 500 characters
    """
    if not raw_bio:
        return ""

    # Strip HTML tags
    cleaned = re.sub(r"<[^>]+>", "", raw_bio)
    # Strip dangerous characters/controls except standard whitespace/newlines
    cleaned = "".join(ch for ch in cleaned if ch.isprintable() or ch in ("\n", "\r", "\t"))
    # Normalize Windows line endings
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse 3 or more consecutive line breaks to 2
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    # Trim leading/trailing whitespace
    cleaned = cleaned.strip()

    if len(cleaned) > MAX_BIO_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "validation_error",
                "message": f"Biography exceeds maximum length of {MAX_BIO_LENGTH} characters",
                "details": {"currentLength": len(cleaned), "maxLength": MAX_BIO_LENGTH},
            },
        )

    return cleaned


def resolve_avatar_url(active_avatar_id: str | None, base_url: str = "") -> str:
    """Resolve full avatar URL from active avatar asset ID."""
    if not active_avatar_id:
        return f"{base_url}{DEFAULT_AVATAR_URL}"
    return f"{base_url}/media/avatars/{active_avatar_id}.webp"


class ProfileService:
    """Service handling profile CRUD operations and validation."""

    @staticmethod
    def get_or_create_profile(
        db: Session,
        user_id: str,
        username: str,
        default_display_name: str | None = None,
    ) -> UserProfile:
        """Fetch existing profile or initialize a new profile record."""
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        profile = db.scalar(stmt)

        if not profile:
            profile = UserProfile(
                user_id=user_id,
                username=username,
                display_name=default_display_name or username,
                bio="",
                active_avatar_id=None,
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)

        return profile

    @staticmethod
    def update_profile(
        db: Session,
        user_id: str,
        display_name: str,
        bio: str,
    ) -> UserProfile:
        """Update display name and bio for the authenticated user."""
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        profile = db.scalar(stmt)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "not_found", "message": "Profile not found"},
            )

        sanitized_display_name = display_name.strip()
        if not (1 <= len(sanitized_display_name) <= 64):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "validation_error",
                    "message": "Display name must be between 1 and 64 characters",
                },
            )

        sanitized_bio = sanitize_bio(bio)

        profile.display_name = sanitized_display_name
        profile.bio = sanitized_bio
        profile.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def get_public_profile(db: Session, username: str) -> UserProfile:
        """Retrieve public profile by username."""
        stmt = select(UserProfile).where(UserProfile.username == username.lower().strip())
        profile = db.scalar(stmt)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "not_found", "message": f"User '{username}' not found"},
            )

        return profile

    @staticmethod
    def set_avatar(
        db: Session,
        user_id: str,
        asset_id: str,
        filename: str,
        file_size_bytes: int,
        width: int,
        height: int,
    ) -> UserProfile:
        """Associate new uploaded avatar asset with the user profile."""
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        profile = db.scalar(stmt)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "not_found", "message": "Profile not found"},
            )

        # Deactivate old assets
        old_assets_stmt = select(AvatarAsset).where(
            AvatarAsset.user_id == user_id,
            AvatarAsset.is_active == True,
        )
        for old_asset in db.scalars(old_assets_stmt):
            old_asset.is_active = False

        # Create new asset record
        new_asset = AvatarAsset(
            id=asset_id,
            user_id=user_id,
            filename=filename,
            mime_type="image/webp",
            file_size_bytes=file_size_bytes,
            width=width,
            height=height,
            is_active=True,
        )
        db.add(new_asset)

        profile.active_avatar_id = asset_id
        profile.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def remove_avatar(db: Session, user_id: str) -> UserProfile:
        """Remove custom avatar and revert profile to default placeholder."""
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        profile = db.scalar(stmt)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "not_found", "message": "Profile not found"},
            )

        if profile.active_avatar_id:
            old_assets_stmt = select(AvatarAsset).where(
                AvatarAsset.user_id == user_id,
                AvatarAsset.is_active == True,
            )
            for old_asset in db.scalars(old_assets_stmt):
                old_asset.is_active = False
                ImageService.delete_avatar_file(old_asset.filename)

            profile.active_avatar_id = None
            profile.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(profile)

        return profile
