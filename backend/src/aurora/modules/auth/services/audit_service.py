import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from aurora.modules.auth.repositories.audit_log_repository import AuditLogRepository


class AuditEvent:
    REGISTER = "user.register"
    LOGIN_SUCCESS = "user.login.success"
    LOGIN_FAILURE = "user.login.failure"
    TOKEN_REFRESH = "token.refresh"
    LOGOUT = "user.logout"
    LOGOUT_ALL = "user.logout_all"
    PASSWORD_CHANGED = "password.changed"
    PASSWORD_RESET_REQUESTED = "password.reset_requested"
    PASSWORD_RESET_COMPLETED = "password.reset_completed"
    EMAIL_VERIFIED = "email.verified"
    EMAIL_VERIFICATION_RESENT = "email.verification_resent"


class AuditService:
    def __init__(self, db: AsyncSession):
        self.repo = AuditLogRepository(db)

    async def log(
        self,
        *,
        event_type: str,
        user_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        await self.repo.create(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )
