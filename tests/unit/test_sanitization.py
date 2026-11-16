"""Unit tests for bio sanitization and boundary constraints."""

import pytest
from fastapi import HTTPException
from src.services.profile_service import sanitize_bio, MAX_BIO_LENGTH


def test_sanitize_bio_normal_text():
    """Verify standard text is preserved."""
    bio = "Hello! I am a full-stack engineer building AI tools."
    result = sanitize_bio(bio)
    assert result == bio


def test_sanitize_bio_trims_whitespace():
    """Verify leading and trailing whitespace is stripped."""
    bio = "   Leading and trailing whitespace   \n\t"
    result = sanitize_bio(bio)
    assert result == "Leading and trailing whitespace"


def test_sanitize_bio_empty_and_none():
    """Verify empty or None bio returns empty string."""
    assert sanitize_bio("") == ""
    assert sanitize_bio(None) == ""
    assert sanitize_bio("   ") == ""


def test_sanitize_bio_strips_html_tags():
    """Verify HTML and script tags are completely stripped."""
    bio = "Hello <script>alert('pwned')</script><b>World</b>!"
    result = sanitize_bio(bio)
    assert result == "Hello alert('pwned')World!"
    assert "<" not in result
    assert ">" not in result


def test_sanitize_bio_collapses_excess_newlines():
    """Verify 3+ consecutive line breaks are collapsed down to 2."""
    bio = "Line 1\n\n\n\n\nLine 2\n\n\nLine 3"
    result = sanitize_bio(bio)
    assert result == "Line 1\n\nLine 2\n\nLine 3"


def test_sanitize_bio_supports_emojis_and_multilingual():
    """Verify UTF-8 multilingual characters and emojis are supported."""
    bio = "🚀 Building in public! こんにちは世界 💻 ⚡"
    result = sanitize_bio(bio)
    assert "🚀" in result
    assert "こんにちは世界" in result


def test_sanitize_bio_max_length_boundary():
    """Verify bio at exactly 500 characters is accepted."""
    bio = "A" * MAX_BIO_LENGTH
    result = sanitize_bio(bio)
    assert len(result) == MAX_BIO_LENGTH


def test_sanitize_bio_exceeding_max_length_raises_400():
    """Verify bio exceeding 500 characters raises 400 Bad Request."""
    bio = "A" * (MAX_BIO_LENGTH + 1)
    with pytest.raises(HTTPException) as exc_info:
        sanitize_bio(bio)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"] == "validation_error"
