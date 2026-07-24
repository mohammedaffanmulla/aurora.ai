from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from aurora.database.base import Base
from aurora.database.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .audit_log import AuditLog
    from .email_verification import EmailVerification
    from .password_reset import PasswordReset
    from .refresh_token import RefreshToken
    from .session import Session
    from .workspace import Workspace
    from .workspace_member import WorkspaceMember


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # -------------------------
    # Workspace Relationships
    # -------------------------

    workspaces: Mapped[list["Workspace"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    workspace_memberships: Mapped[list["WorkspaceMember"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # -------------------------
    # Authentication
    # -------------------------

    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    password_resets: Mapped[list["PasswordReset"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    email_verifications: Mapped[list["EmailVerification"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # -------------------------
    # Audit Logs
    # -------------------------

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user",
    )

    def __repr__(self) -> str:
        return (
            f"User("
            f"id={self.id}, "
            f"email='{self.email}', "
            f"is_verified={self.is_verified})"
        )