"""FastAPI route handlers for profile management."""

from fastapi import APIRouter, status, Request
from src.api.dependencies import DbSession, CurrentUser
from src.schemas.profile import (
    ProfileResponse,
    UpdateProfileRequest,
    PublicProfileResponse,
)
from src.services.profile_service import ProfileService, resolve_avatar_url

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _to_profile_response(profile, request: Request | None = None) -> ProfileResponse:
    """Helper to convert ORM UserProfile into ProfileResponse schema."""
    base_url = str(request.base_url).rstrip("/") if request else ""
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        username=profile.username,
        display_name=profile.display_name,
        bio=profile.bio,
        avatar_url=resolve_avatar_url(profile.active_avatar_id, base_url),
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get(
    "/me",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user profile",
)
def get_my_profile(
    current_user: CurrentUser,
    db: DbSession,
    request: Request,
) -> ProfileResponse:
    """Retrieve profile for the currently authenticated user."""
    profile = ProfileService.get_or_create_profile(
        db=db,
        user_id=current_user.user_id,
        username=current_user.username,
    )
    return _to_profile_response(profile, request)


@router.put(
    "/me",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update authenticated user profile",
)
@router.patch(
    "/me",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Patch authenticated user profile",
)
def update_my_profile(
    payload: UpdateProfileRequest,
    current_user: CurrentUser,
    db: DbSession,
    request: Request,
) -> ProfileResponse:
    """Update display name and bio for the authenticated user."""
    # Ensure profile exists first
    ProfileService.get_or_create_profile(
        db=db,
        user_id=current_user.user_id,
        username=current_user.username,
    )
    updated = ProfileService.update_profile(
        db=db,
        user_id=current_user.user_id,
        display_name=payload.display_name,
        bio=payload.bio,
    )
    return _to_profile_response(updated, request)


@router.get(
    "/{username}",
    response_model=PublicProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get public profile by username",
)
def get_public_profile(
    username: str,
    db: DbSession,
    request: Request,
) -> PublicProfileResponse:
    """Retrieve public profile view for any user by their username."""
    profile = ProfileService.get_public_profile(db=db, username=username)
    base_url = str(request.base_url).rstrip("/") if request else ""
    return PublicProfileResponse(
        username=profile.username,
        display_name=profile.display_name,
        bio=profile.bio,
        avatar_url=resolve_avatar_url(profile.active_avatar_id, base_url),
    )
