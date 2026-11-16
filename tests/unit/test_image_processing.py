"""Unit tests for avatar image validation, resizing, and WebP processing."""

import io
import pytest
from PIL import Image
from fastapi import HTTPException
from src.services.image_service import ImageService, MAX_AVATAR_BYTES


def _create_test_image_bytes(format="JPEG", size=(400, 300), color=(255, 0, 0)) -> bytes:
    """Helper to generate in-memory valid image bytes."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def test_process_and_save_avatar_valid_jpeg():
    """Verify standard JPEG is resized to 256x256 WebP."""
    img_bytes = _create_test_image_bytes("JPEG", size=(500, 300))
    asset_id, filename, file_size, width, height = ImageService.process_and_save_avatar(img_bytes)

    assert asset_id is not None
    assert filename.endswith(".webp")
    assert width == 256
    assert height == 256
    assert file_size > 0

    # Cleanup
    ImageService.delete_avatar_file(filename)


def test_process_and_save_avatar_valid_png_with_transparency():
    """Verify PNG with RGBA transparency is processed properly."""
    img = Image.new("RGBA", (200, 200), color=(0, 255, 0, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    asset_id, filename, file_size, width, height = ImageService.process_and_save_avatar(img_bytes)
    assert filename.endswith(".webp")
    assert width == 256
    assert height == 256

    # Cleanup
    ImageService.delete_avatar_file(filename)


def test_process_avatar_empty_file_fails():
    """Verify empty byte stream raises 400."""
    with pytest.raises(HTTPException) as exc_info:
        ImageService.process_and_save_avatar(b"")
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"] == "empty_file"


def test_process_avatar_corrupt_or_non_image_fails():
    """Verify non-image text payload raises 400."""
    with pytest.raises(HTTPException) as exc_info:
        ImageService.process_and_save_avatar(b"Not an image at all, just plain text")
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"] == "invalid_image"


def test_process_avatar_unsupported_format_fails():
    """Verify unsupported formats (e.g., GIF, BMP) raise 400."""
    img = Image.new("RGB", (100, 100), color=(0, 0, 255))
    buf = io.BytesIO()
    img.save(buf, format="BMP")
    bmp_bytes = buf.getvalue()

    with pytest.raises(HTTPException) as exc_info:
        ImageService.process_and_save_avatar(bmp_bytes)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"] == "unsupported_format"


def test_process_avatar_file_too_large_fails():
    """Verify images exceeding 5MB raise 400."""
    oversized_bytes = b"0" * (MAX_AVATAR_BYTES + 1)
    with pytest.raises(HTTPException) as exc_info:
        ImageService.process_and_save_avatar(oversized_bytes)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"] == "file_too_large"
