from sqlalchemy.ext.asyncio import AsyncSession

from aurora.modules.auth import emails
from aurora.modules.auth.exceptions import (
    EmailAlreadyVerifiedError,
    InvalidTokenError,
    UserNotFoundError,
)
from aurora.modules.auth.repositories.email_verification_repository import (
    EmailVerificationRepository,
)
from aurora.modules.auth.repositories.user_repository import UserRepository
from aurora.modules.auth.security.jwt import (
    email_verification_token_expiry,
    generate_opaque_token,
    hash_opaque_token,
)
from aurora.modules.auth.services.audit_service import AuditEvent, AuditService


class EmailService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)
        self.verification_tokens = EmailVerificationRepository(db)
        self.audit = AuditService(db)

    async def send_verification_for_new_user(self, *, user_id, email: str) -> None:
        """Called right after registration to kick off the verification flow."""
        raw_token = generate_opaque_token()

        await self.verification_tokens.create(
            user_id=user_id,
            token_hash=hash_opaque_token(raw_token),
            expires_at=email_verification_token_expiry(),
        )

        await self.db.commit()
        await emails.send_verification_email(
            to=email,
            token=raw_token,
        )

    async def resend_verification(
        self,
        *,
        email: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        user = await self.users.get_by_email(email)

        if user is None:
            # Don't leak whether the email exists.
            return

        if user.is_verified:
            return

        await self.verification_tokens.invalidate_all_for_user(user.id)

        raw_token = generate_opaque_token()

        await self.verification_tokens.create(
            user_id=user.id,
            token_hash=hash_opaque_token(raw_token),
            expires_at=email_verification_token_expiry(),
        )

        await self.audit.log(
            event_type=AuditEvent.EMAIL_VERIFICATION_RESENT,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        await self.db.commit()

        await emails.send_verification_email(
            to=user.email,
            token=raw_token,
        )

    async def verify_email(
        self,
        *,
        token: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        token_hash = hash_opaque_token(token)

        verification = await self.verification_tokens.get_by_hash(token_hash)

        if verification is None or not verification.is_valid:
            raise InvalidTokenError("Invalid or expired verification token")

        user = await self.users.get_by_id(verification.user_id)

        if user is None:
            raise UserNotFoundError("User not found")

        if user.is_verified:
            raise EmailAlreadyVerifiedError("Email is already verified")

        await self.users.mark_email_verified(user)
        await self.verification_tokens.mark_used(verification)

        await self.audit.log(
            event_type=AuditEvent.EMAIL_VERIFIED,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        await self.db.commit()