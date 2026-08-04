import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from aurora.modules.auth.config import settings
from aurora.modules.auth.exceptions import (
    EmailAlreadyRegisteredError,
    InactiveUserError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from aurora.database.models import User
from aurora.modules.auth.repositories.user_repository import UserRepository
from aurora.modules.auth.security.jwt import create_access_token
from aurora.modules.auth.security.password import hash_password, verify_password
from aurora.modules.auth.services.audit_service import AuditEvent, AuditService
from aurora.modules.auth.services.email_service import EmailService
from aurora.modules.auth.services.session_service import SessionService


class AuthTokens:
    """Simple carrier for the pair returned to the client after login/refresh."""

    def __init__(self, access_token: str, refresh_token: str, expires_in: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)
        self.sessions = SessionService(db)
        self.emails = EmailService(db)
        self.audit = AuditService(db)

    async def register(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> User:
        existing = await self.users.get_by_email(email)
        if existing is not None:
            raise EmailAlreadyRegisteredError("An account with this email already exists")

        user = await self.users.create(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
        )
        await self.audit.log(
            event_type=AuditEvent.REGISTER, user_id=user.id, ip_address=ip_address, user_agent=user_agent
        )
        await self.db.commit()
        await self.db.refresh(user)

        # Fire off the verification email in its own transaction/session state.
        await self.emails.send_verification_for_new_user(user_id=user.id, email=user.email)

        return user

    async def login(
        self, *, email: str, password: str, ip_address: str | None, user_agent: str | None
    ) -> AuthTokens:
        user = await self.users.get_by_email(email)

        if user is None or not verify_password(password, user.password_hash):
            await self.audit.log(
                event_type=AuditEvent.LOGIN_FAILURE, ip_address=ip_address, user_agent=user_agent,
                metadata={"email": email},
            )
            await self.db.commit()
            raise InvalidCredentialsError("Incorrect email or password")

        if not user.is_active:
            raise InactiveUserError("This account has been deactivated")

        session, raw_refresh_token = await self.sessions.start_session(
            user_id=user.id, user_agent=user_agent, ip_address=ip_address
        )
        access_token = create_access_token(user_id=user.id, session_id=session.id)

        await self.audit.log(
            event_type=AuditEvent.LOGIN_SUCCESS,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.db.commit()

        return AuthTokens(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            expires_in=settings.auth_access_token_expire_minutes * 60,
        )

    async def refresh(
        self, *, raw_refresh_token: str, ip_address: str | None, user_agent: str | None
    ) -> AuthTokens:
        session, _new_token_row, new_raw_refresh_token = await self.sessions.rotate_refresh_token(
            raw_refresh_token=raw_refresh_token
        )
        access_token = create_access_token(user_id=session.user_id, session_id=session.id)

        await self.audit.log(
            event_type=AuditEvent.TOKEN_REFRESH,
            user_id=session.user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.db.commit()

        return AuthTokens(
            access_token=access_token,
            refresh_token=new_raw_refresh_token,
            expires_in=settings.auth_access_token_expire_minutes * 60,
        )

    async def get_me(self, *, user_id: uuid.UUID) -> User:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User not found")
        return user

    async def logout(
        self, *, raw_refresh_token: str, user_id: uuid.UUID, ip_address: str | None, user_agent: str | None
    ) -> None:
        await self.sessions.revoke_session_by_refresh_token(raw_refresh_token=raw_refresh_token)
        await self.audit.log(
            event_type=AuditEvent.LOGOUT, user_id=user_id, ip_address=ip_address, user_agent=user_agent
        )
        await self.db.commit()

    async def logout_all(
        self, *, user_id: uuid.UUID, ip_address: str | None, user_agent: str | None
    ) -> None:
        await self.sessions.revoke_all_sessions_for_user(user_id=user_id)
        await self.audit.log(
            event_type=AuditEvent.LOGOUT_ALL, user_id=user_id, ip_address=ip_address, user_agent=user_agent
        )
        await self.db.commit()
