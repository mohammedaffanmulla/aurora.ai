from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import EmailVerification


class EmailVerificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        verification: EmailVerification,
    ) -> EmailVerification:
        self.db.add(verification)
        await self.db.commit()
        await self.db.refresh(verification)
        return verification

    async def get_by_id(
        self,
        verification_id: UUID,
    ) -> EmailVerification | None:
        result = await self.db.execute(
            select(EmailVerification).where(
                EmailVerification.id == verification_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_token(
        self,
        token: str,
    ) -> EmailVerification | None:
        result = await self.db.execute(
            select(EmailVerification).where(
                EmailVerification.token == token
            )
        )
        return result.scalar_one_or_none()

    async def get_user_verifications(
        self,
        user_id: UUID,
    ) -> list[EmailVerification]:
        result = await self.db.execute(
            select(EmailVerification).where(
                EmailVerification.user_id == user_id
            )
        )
        return list(result.scalars().all())

    async def mark_used(
        self,
        verification: EmailVerification,
    ) -> EmailVerification:
        verification.used = True
        await self.db.commit()
        await self.db.refresh(verification)
        return verification

    async def delete(
        self,
        verification: EmailVerification,
    ) -> None:
        await self.db.delete(verification)
        await self.db.commit()

    async def delete_by_user(
        self,
        user_id: UUID,
    ) -> None:
        await self.db.execute(
            delete(EmailVerification).where(
                EmailVerification.user_id == user_id
            )
        )
        await self.db.commit()