"""SQLAlchemy AvatarAsset ORM model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base


class AvatarAsset(Base):
    """Represents an uploaded avatar image file and its metadata."""

    __tablename__ = "avatar_assets"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    mime_type: Mapped[str] = mapped_column(
        String(32),
        default="image/webp",
        nullable=False,
    )
    file_size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    width: Mapped[int] = mapped_column(
        Integer,
        default=256,
        nullable=False,
    )
    height: Mapped[int] = mapped_column(
        Integer,
        default=256,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<AvatarAsset id={self.id} user={self.user_id} filename={self.filename}>"
