from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import AuditLog


class AuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        audit_log: AuditLog,
    ) -> AuditLog:
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log

    async def get_by_id(
        self,
        audit_id: UUID,
    ) -> AuditLog | None:
        result = await self.db.execute(
            select(AuditLog).where(
                AuditLog.id == audit_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: UUID,
    ) -> list[AuditLog]:
        result = await self.db.execute(
            select(AuditLog).where(
                AuditLog.user_id == user_id
            )
        )
        return list(result.scalars().all())

    async def get_all(self) -> list[AuditLog]:
        result = await self.db.execute(
            select(AuditLog).order_by(
                AuditLog.created_at.desc()
            )
        )
        return list(result.scalars().all())

    async def delete(
        self,
        audit_log: AuditLog,
    ) -> None:
        await self.db.delete(audit_log)
        await self.db.commit()