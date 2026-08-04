import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from aurora.modules.auth import emails
from aurora.modules.auth.exceptions import InvalidCredentialsError, InvalidTokenError, UserNotFoundError
from aurora.modules.auth.repositories.password_reset_repository import PasswordResetRepository
from aurora.modules.auth.repositories.refresh_token_repository import RefreshTokenRepository
from aurora.modules.auth.repositories.session_repository import SessionRepository
from aurora.modules.auth.repositories.user_repository import UserRepository
from aurora.modules.auth.security.jwt import (
    generate_opaque_token,
    hash_opaque_token,
    password_reset_token_expiry,
)
from aurora.modules.auth.security.password import hash_password, verify_password
from aurora.modules.auth.services.audit_service import AuditEvent, AuditService


class PasswordService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)
        self.reset_tokens = PasswordResetRepository(db)
        self.sessions = SessionRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)
        self.audit = AuditService(db)

    async def change_password(
        self,
        *,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str,
        current_session_id: uuid.UUID,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        if not verify_password(current_password, user.hashed_password):
            raise InvalidCredentialsError("Current password is incorrect")

        await self.users.update_password(user, hashed_password=hash_password(new_password))

        # Revoke every other session's refresh tokens as a security precaution,
        # but keep the current session alive so the user isn't logged out of
        # the device they just used to change their password.
        await self.sessions.revoke_all_for_user(user.id, except_session_id=current_session_id)
        await self.refresh_tokens.revoke_all_for_user(user.id)

        await self.audit.log(
            event_type=AuditEvent.PASSWORD_CHANGED,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.db.commit()

    async def forgot_password(
        self, *, email: str, ip_address: str | None, user_agent: str | None
    ) -> None:
        user = await self.users.get_by_email(email)
        if user is None:
            # Do not reveal whether the email is registered.
            return

        await self.reset_tokens.invalidate_all_for_user(user.id)

        raw_token = generate_opaque_token()
        await self.reset_tokens.create(
            user_id=user.id,
            token_hash=hash_opaque_token(raw_token),
            expires_at=password_reset_token_expiry(),
        )
        await self.audit.log(
            event_type=AuditEvent.PASSWORD_RESET_REQUESTED,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.db.commit()
        await emails.send_password_reset_email(to=user.email, token=raw_token)

    async def reset_password(
        self, *, token: str, new_password: str, ip_address: str | None, user_agent: str | None
    ) -> None:
        token_hash = hash_opaque_token(token)
        reset_token = await self.reset_tokens.get_by_hash(token_hash)

        if reset_token is None or not reset_token.is_valid:
            raise InvalidTokenError("Invalid or expired password reset token")

        user = await self.users.get_by_id(reset_token.user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        await self.users.update_password(user, hashed_password=hash_password(new_password))
        await self.reset_tokens.mark_used(reset_token)

        # A password reset invalidates all existing sessions everywhere.
        await self.sessions.revoke_all_for_user(user.id)
        await self.refresh_tokens.revoke_all_for_user(user.id)

        await self.audit.log(
            event_type=AuditEvent.PASSWORD_RESET_COMPLETED,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.db.commit()
