import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import AuditLog


class AuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        event_type: str,
        user_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str |None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            action=event_type,
            user_id=user_id,
            event_data={
                "ip_address": ip_address,
                "user_agent": user_agent,
                **(metadata or {}),
            },
        )

        self.db.add(entry)
        await self.db.flush()
        return entry