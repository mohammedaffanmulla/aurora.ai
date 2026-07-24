from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from aurora.database.base import Base
from aurora.database.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .user import User


class PasswordReset(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "password_resets"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="password_resets",
    )

    def __repr__(self) -> str:
        return (
            f"PasswordReset("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"used={self.used})"
        )