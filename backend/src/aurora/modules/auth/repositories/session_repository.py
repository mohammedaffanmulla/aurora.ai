import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import Session


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        user_agent: str | None,
        ip_address: str | None,
    ) -> Session:
        session = Session(
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address,
            last_seen_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            revoked=False,
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_by_id(self, session_id: uuid.UUID) -> Session | None:
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    async def list_active_for_user(
        self,
        user_id: uuid.UUID,
    ) -> list[Session]:
        result = await self.db.execute(
            select(Session).where(
                Session.user_id == user_id,
                Session.revoked.is_(False),
                Session.expires_at > datetime.now(timezone.utc),
            )
        )
        return list(result.scalars().all())

    async def touch_last_used(self, session: Session) -> None:
        session.last_seen_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def revoke(self, session: Session) -> None:
        session.revoked = True
        await self.db.flush()

    async def revoke_all_for_user(
        self,
        user_id: uuid.UUID,
        *,
        except_session_id: uuid.UUID | None = None,
    ) -> None:
        stmt = (
            update(Session)
            .where(
                Session.user_id == user_id,
                Session.revoked.is_(False),
            )
            .values(revoked=True)
        )

        if except_session_id is not None:
            stmt = stmt.where(Session.id != except_session_id)

        await self.db.execute(stmt)
        await self.db.flush()