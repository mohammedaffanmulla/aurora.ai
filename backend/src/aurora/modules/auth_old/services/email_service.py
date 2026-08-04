from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import EmailVerification, User
from aurora.modules.auth.repositories.email_verification_repository import (
    EmailVerificationRepository,
)


class EmailService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.verifications = EmailVerificationRepository(db)

    async def create_verification(
        self,
        user: User,
    ) -> EmailVerification:
        token = secrets.token_urlsafe(32)

        verification = EmailVerification(
            user_id=user.id,
            token=token,
            expires_at=datetime.now(UTC) + timedelta(hours=24),
            used=False,
        )

        return await self.verifications.create(verification)

    async def verify_token(
        self,
        token: str,
    ) -> EmailVerification | None:
        verification = await self.verifications.get_by_token(token)

        if verification is None:
            return None

        if verification.used:
            return None

        if verification.expires_at < datetime.now(UTC):
            return None

        return verification

    async def mark_used(
        self,
        verification: EmailVerification,
    ) -> EmailVerification:
        return await self.verifications.mark_used(verification)

    async def resend_verification(
        self,
        user: User,
    ) -> EmailVerification:
        await self.verifications.delete_by_user(user.id)
        return await self.create_verification(user)