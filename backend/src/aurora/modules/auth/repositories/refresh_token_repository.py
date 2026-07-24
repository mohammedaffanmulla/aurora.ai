from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def get_by_id(self, token_id: UUID) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.id == token_id)
        )
        return result.scalar_one_or_none()

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def get_user_tokens(
        self,
        user_id: UUID,
    ) -> list[RefreshToken]:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id
            )
        )
        return list(result.scalars().all())

    async def revoke(
        self,
        token: RefreshToken,
    ) -> RefreshToken:
        token.revoked = True
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def revoke_all(
        self,
        user_id: UUID,
    ) -> None:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id
            )
        )

        for token in result.scalars():
            token.revoked = True

        await self.db.commit()

    async def delete(self, token: RefreshToken) -> None:
        await self.db.delete(token)
        await self.db.commit()

    async def delete_by_user(self, user_id: UUID) -> None:
        await self.db.execute(
            delete(RefreshToken).where(
                RefreshToken.user_id == user_id
            )
        )
        await self.db.commit()