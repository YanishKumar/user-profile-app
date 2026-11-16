"""FastAPI route handlers for profile and avatar management."""

from fastapi import APIRouter, status, Request, UploadFile, File
from src.api.dependencies import DbSession, CurrentUser
from src.schemas.profile import (
    ProfileResponse,
    UpdateProfileRequest,
    PublicProfileResponse,
)
from src.schemas.avatar import AvatarUploadResponse
from src.services.profile_service import ProfileService, resolve_avatar_url
from src.services.image_service import ImageService

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


@router.post(
    "/me/avatar",
    response_model=AvatarUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and update avatar image",
)
async def upload_avatar(
    current_user: CurrentUser,
    db: DbSession,
    request: Request,
    file: UploadFile = File(...),
) -> AvatarUploadResponse:
    """Upload, normalize, and set custom avatar image."""
    ProfileService.get_or_create_profile(
        db=db,
        user_id=current_user.user_id,
        username=current_user.username,
    )

    image_bytes = await file.read()
    asset_id, filename, file_size_bytes, width, height = ImageService.process_and_save_avatar(
        image_bytes=image_bytes,
        filename_hint=file.filename or "",
    )

    ProfileService.set_avatar(
        db=db,
        user_id=current_user.user_id,
        asset_id=asset_id,
        filename=filename,
        file_size_bytes=file_size_bytes,
        width=width,
        height=height,
    )

    base_url = str(request.base_url).rstrip("/")
    return AvatarUploadResponse(
        asset_id=asset_id,
        avatar_url=resolve_avatar_url(asset_id, base_url),
        file_size_bytes=file_size_bytes,
        width=width,
        height=height,
    )


@router.delete(
    "/me/avatar",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove custom avatar and revert to default",
)
def delete_avatar(
    current_user: CurrentUser,
    db: DbSession,
    request: Request,
) -> ProfileResponse:
    """Remove custom avatar and restore default placeholder."""
    ProfileService.get_or_create_profile(
        db=db,
        user_id=current_user.user_id,
        username=current_user.username,
    )
    updated = ProfileService.remove_avatar(db=db, user_id=current_user.user_id)
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
