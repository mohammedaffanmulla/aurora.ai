from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from aurora.database.base import Base
from aurora.database.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .user import User


class AuditLog(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    resource_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    event_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="audit_logs",
    )

    def __repr__(self) -> str:
        return (
            f"AuditLog("
            f"id={self.id}, "
            f"action='{self.action}', "
            f"user_id={self.user_id})"
        )