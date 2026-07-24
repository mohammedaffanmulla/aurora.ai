from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import Session


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, session: Session) -> Session:
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_by_id(self, session_id: UUID) -> Session | None:
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_user_sessions(self, user_id: UUID) -> list[Session]:
        result = await self.db.execute(
            select(Session).where(Session.user_id == user_id)
        )
        return list(result.scalars().all())

    async def delete(self, session: Session) -> None:
        await self.db.delete(session)
        await self.db.commit()

    async def delete_by_user(self, user_id: UUID) -> None:
        await self.db.execute(
            delete(Session).where(Session.user_id == user_id)
        )
        await self.db.commit()

    async def update(self, session: Session) -> Session:
        await self.db.commit()
        await self.db.refresh(session)
        return session