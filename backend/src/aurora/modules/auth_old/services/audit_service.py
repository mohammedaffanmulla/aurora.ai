from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import AuditLog
from aurora.modules.auth.repositories.audit_log_repository import (
    AuditLogRepository,
)


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_logs = AuditLogRepository(db)

    async def log(
        self,
        action: str,
        user_id: UUID | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        event_data: dict | None = None,
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            event_data=event_data,
        )

        return await self.audit_logs.create(log)

    async def get_user_logs(
        self,
        user_id: UUID,
    ) -> list[AuditLog]:
        return await self.audit_logs.get_by_user(user_id)