from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.models import User
from aurora.modules.auth.repositories.user_repository import UserRepository
from aurora.modules.auth.security import (
    hash_password,
    verify_password,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)

    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
    ) -> User:
        existing = await self.users.get_by_email(email)

        if existing:
            raise ValueError("Email already registered")

        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            is_active=True,
            is_verified=False,
            is_superuser=False,
        )

        return await self.users.create(user)

    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> User:
        user = await self.users.get_by_email(email)

        if user is None:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is disabled")

        return user

    async def get_user(
        self,
        user_id: UUID,
    ) -> User | None:
        return await self.users.get_by_id(user_id)

    async def verify_user(
        self,
        user: User,
    ) -> User:
        return await self.users.verify_email(user)

    async def deactivate_user(
        self,
        user: User,
    ) -> User:
        return await self.users.deactivate(user)