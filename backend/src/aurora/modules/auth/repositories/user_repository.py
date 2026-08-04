import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        password_hash: str,
        full_name: str | None,
    ) -> User:
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def update_password(
        self,
        user: User,
        *,
        password_hash: str,
    ) -> User:
        user.password_hash = password_hash
        await self.db.flush()
        return user

    async def mark_email_verified(self, user: User) -> User:
        user.is_verified = True
        await self.db.flush()
        return user

    async def set_active(
        self,
        user: User,
        *,
        is_active: bool,
    ) -> User:
        user.is_active = is_active
        await self.db.flush()
        return user