"""Avatar image validation, EXIF stripping, and WebP processing service."""

import io
import os
import uuid
from PIL import Image, ImageOps
from fastapi import HTTPException, status

MAX_AVATAR_BYTES = 5 * 1024 * 1024  # 5 Megabytes
ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}
AVATAR_DIMENSION = 256
AVATAR_UPLOAD_DIR = os.getenv("AVATAR_UPLOAD_DIR", "uploads/avatars")


class ImageService:
    """Service handling avatar image validation, normalization, and persistence."""

    @staticmethod
    def process_and_save_avatar(
        image_bytes: bytes,
        filename_hint: str = "",
    ) -> tuple[str, str, int, int, int]:
        """Validate, sanitize, resize, and convert an image to 256x256 WebP.

        Returns:
            tuple of (asset_id, filename, file_size_bytes, width, height)
        """
        # 1. Size check
        if len(image_bytes) > MAX_AVATAR_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "file_too_large",
                    "message": f"Avatar image exceeds the 5MB maximum limit ({len(image_bytes)} bytes)",
                },
            )

        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "empty_file", "message": "Uploaded file is empty"},
            )

        # 2. Decode and validate format
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()  # Verify integrity
            # Reopen because verify() closes/invalidates the image object
            image = Image.open(io.BytesIO(image_bytes))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_image",
                    "message": "File is corrupted or not a recognized image format",
                },
            )

        format_name = (image.format or "").upper()
        if format_name not in ALLOWED_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "unsupported_format",
                    "message": f"Unsupported image format '{format_name}'. Allowed: JPEG, PNG, WebP",
                },
            )

        # 3. Strip EXIF by re-creating image in fresh memory
        # Handle orientation if EXIF had orientation tags before stripping
        try:
            image = ImageOps.exif_transpose(image)
        except Exception:
            pass

        # 4. Mode normalization: keep RGBA if transparency exists, otherwise RGB
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

        # 5. Crop to square (center crop) and resize to standardized 256x256
        w, h = image.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        image = image.crop((left, top, right, bottom))
        image = image.resize((AVATAR_DIMENSION, AVATAR_DIMENSION), Image.Resampling.LANCZOS)

        # 6. Save as WebP
        os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)
        asset_id = str(uuid.uuid4())
        filename = f"{asset_id}.webp"
        destination_path = os.path.join(AVATAR_UPLOAD_DIR, filename)

        buffer = io.BytesIO()
        image.save(buffer, format="WEBP", quality=85, method=6)
        webp_bytes = buffer.getvalue()

        with open(destination_path, "wb") as f:
            f.write(webp_bytes)

        return (asset_id, filename, len(webp_bytes), AVATAR_DIMENSION, AVATAR_DIMENSION)

    @staticmethod
    def delete_avatar_file(filename: str) -> None:
        """Safely delete an avatar file from disk."""
        target_path = os.path.join(AVATAR_UPLOAD_DIR, filename)
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
            except OSError:
                pass
