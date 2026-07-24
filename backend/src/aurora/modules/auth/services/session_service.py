from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import Session
from aurora.modules.auth.repositories.session_repository import SessionRepository


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sessions = SessionRepository(db)

    async def create_session(
        self,
        user_id: UUID,
        refresh_token_id: UUID | None,
        device_name: str | None,
        ip_address: str | None,
        user_agent: str | None,
        expires_at: datetime,
    ) -> Session:
        session = Session(
            user_id=user_id,
            refresh_token_id=refresh_token_id,
            device_name=device_name,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        return await self.sessions.create(session)

    async def get_session(
        self,
        session_id: UUID,
    ) -> Session | None:
        return await self.sessions.get_by_id(session_id)

    async def get_user_sessions(
        self,
        user_id: UUID,
    ) -> list[Session]:
        return await self.sessions.get_user_sessions(user_id)

    async def revoke_session(
        self,
        session_id: UUID,
    ) -> None:
        session = await self.sessions.get_by_id(session_id)

        if session:
            await self.sessions.delete(session)

    async def revoke_all_sessions(
        self,
        user_id: UUID,
    ) -> None:
        await self.sessions.delete_by_user(user_id)

    async def cleanup_expired_sessions(
        self,
        user_id: UUID,
    ) -> None:
        sessions = await self.sessions.get_user_sessions(user_id)

        now = datetime.now(UTC)

        for session in sessions:
            if session.expires_at <= now:
                await self.sessions.delete(session)