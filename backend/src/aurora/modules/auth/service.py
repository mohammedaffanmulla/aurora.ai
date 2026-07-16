from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models.user import User
from aurora.modules.auth.security import (
    hash_password,
    verify_password,
)


class AuthService:

    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        email: str,
    ) -> User | None:

        result = await db.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        db: AsyncSession,
        *,
        email: str,
        password: str,
        full_name: str,
    ) -> User:

        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
        )

        db.add(user)

        await db.commit()

        await db.refresh(user)

        return user

    @staticmethod
    async def authenticate(
        db: AsyncSession,
        email: str,
        password: str,
    ) -> User | None:

        user = await AuthService.get_user_by_email(
            db,
            email,
        )

        if user is None:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user