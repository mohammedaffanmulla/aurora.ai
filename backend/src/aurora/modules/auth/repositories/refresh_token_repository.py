import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            session_id=session_id,
            token_hash=token_hash,
            family_id=uuid.uuid4(),
            expires_at=expires_at,
        )
        self.db.add(token)
        await self.db.flush()
        return token

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def revoke(
        self,
        token: RefreshToken,
        *,
        replaced_by_token_id: uuid.UUID | None = None,
    ) -> None:
        token.revoked = True

        if replaced_by_token_id is not None:
            token.replaced_by_token = str(replaced_by_token_id)

        await self.db.flush()

    async def revoke_all_for_session(
        self,
        session_id: uuid.UUID,
    ) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.session_id == session_id,
                RefreshToken.revoked.is_(False),
            )
            .values(revoked=True)
        )
        await self.db.flush()

    async def revoke_all_for_user(
        self,
        user_id: uuid.UUID,
    ) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False),
            )
            .values(revoked=True)
        )
        await self.db.flush()