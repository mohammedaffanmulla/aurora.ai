from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import PasswordReset


class PasswordResetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        password_reset: PasswordReset,
    ) -> PasswordReset:
        self.db.add(password_reset)
        await self.db.commit()
        await self.db.refresh(password_reset)
        return password_reset

    async def get_by_id(
        self,
        reset_id: UUID,
    ) -> PasswordReset | None:
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.id == reset_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_token(
        self,
        token: str,
    ) -> PasswordReset | None:
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.token == token
            )
        )
        return result.scalar_one_or_none()

    async def get_user_requests(
        self,
        user_id: UUID,
    ) -> list[PasswordReset]:
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.user_id == user_id
            )
        )
        return list(result.scalars().all())

    async def mark_used(
        self,
        password_reset: PasswordReset,
    ) -> PasswordReset:
        password_reset.used = True
        await self.db.commit()
        await self.db.refresh(password_reset)
        return password_reset

    async def delete(
        self,
        password_reset: PasswordReset,
    ) -> None:
        await self.db.delete(password_reset)
        await self.db.commit()

    async def delete_by_user(
        self,
        user_id: UUID,
    ) -> None:
        await self.db.execute(
            delete(PasswordReset).where(
                PasswordReset.user_id == user_id
            )
        )
        await self.db.commit()