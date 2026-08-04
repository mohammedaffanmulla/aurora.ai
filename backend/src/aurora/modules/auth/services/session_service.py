import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from aurora.modules.auth.config import settings
from aurora.modules.auth.exceptions import (
    InvalidTokenError,
    SessionNotFoundError,
)
from aurora.database.models import RefreshToken, Session
from aurora.modules.auth.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from aurora.modules.auth.repositories.session_repository import (
    SessionRepository,
)
from aurora.modules.auth.security.jwt import (
    generate_opaque_token,
    hash_opaque_token,
    refresh_token_expiry,
)


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sessions = SessionRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

    async def start_session(
        self,
        *,
        user_id: uuid.UUID,
        user_agent: str | None,
        ip_address: str | None,
    ) -> tuple[Session, str]:
        """
        Create a new session and its first refresh token.
        Returns (session, raw_refresh_token).
        """

        active = await self.sessions.list_active_for_user(user_id)

        if len(active) >= settings.auth_max_active_sessions_per_user:
            oldest = min(
                active,
                key=lambda s: s.last_seen_at or s.created_at,
            )
            await self.sessions.revoke(oldest)
            await self.refresh_tokens.revoke_all_for_session(oldest.id)

        session = await self.sessions.create(
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        raw_refresh_token = await self._issue_refresh_token(
            user_id=user_id,
            session_id=session.id,
        )

        return session, raw_refresh_token

    async def _issue_refresh_token(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> str:
        raw_token = generate_opaque_token()

        await self.refresh_tokens.create(
            user_id=user_id,
            session_id=session_id,
            token_hash=hash_opaque_token(raw_token),
            expires_at=refresh_token_expiry(),
        )

        return raw_token

    async def rotate_refresh_token(
        self,
        *,
        raw_refresh_token: str,
    ) -> tuple[Session, RefreshToken, str]:

        token_hash = hash_opaque_token(raw_refresh_token)

        existing = await self.refresh_tokens.get_by_hash(token_hash)

        if existing is None:
            raise InvalidTokenError("Invalid refresh token")

        if not existing.is_active:
            await self.refresh_tokens.revoke_all_for_session(
                existing.session_id
            )
            await self.sessions.revoke_all_for_user(existing.user_id)
            raise InvalidTokenError(
                "Refresh token has already been used or revoked"
            )

        session = await self.sessions.get_by_id(existing.session_id)

        if session is None or not session.is_active:
            raise InvalidTokenError("Session no longer active")

        new_raw_token = generate_opaque_token()

        new_token_row = await self.refresh_tokens.create(
            user_id=existing.user_id,
            session_id=existing.session_id,
            token_hash=hash_opaque_token(new_raw_token),
            expires_at=refresh_token_expiry(),
        )

        await self.refresh_tokens.revoke(
            existing,
            replaced_by_token_id=new_token_row.id,
        )

        await self.sessions.touch_last_used(session)

        return session, new_token_row, new_raw_token

    async def revoke_session_by_refresh_token(
        self,
        *,
        raw_refresh_token: str,
    ) -> None:

        token_hash = hash_opaque_token(raw_refresh_token)

        existing = await self.refresh_tokens.get_by_hash(token_hash)

        if existing is None:
            raise SessionNotFoundError("Session not found")

        session = await self.sessions.get_by_id(existing.session_id)

        if session:
            await self.sessions.revoke(session)

        await self.refresh_tokens.revoke_all_for_session(existing.session_id)

    async def revoke_all_sessions_for_user(
        self,
        *,
        user_id: uuid.UUID,
    ) -> None:

        await self.sessions.revoke_all_for_user(user_id)
        await self.refresh_tokens.revoke_all_for_user(user_id)