import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import PasswordReset



class PasswordResetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at,
    ) -> PasswordReset:
        token = PasswordReset(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(token)
        await self.db.flush()
        return token

    async def get_by_hash(self, token_hash: str) -> PasswordReset | None:
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def mark_used(self, token: PasswordReset) -> None:
        token.used = True
        await self.db.flush()

    async def invalidate_all_for_user(self, user_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.user_id == user_id,
                PasswordReset.used.is_(False),
            )
        )

        for token in result.scalars().all():
            token.used = True

        await self.db.flush()