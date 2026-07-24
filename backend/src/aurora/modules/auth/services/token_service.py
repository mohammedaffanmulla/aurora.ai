from __future__ import annotations

from uuid import UUID

from aurora.modules.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)


class TokenService:
    def create_access(self, user_id: UUID | str) -> str:
        return create_access_token(user_id)

    def create_refresh(self, user_id: UUID | str) -> str:
        return create_refresh_token(user_id)

    def create_token_pair(
        self,
        user_id: UUID | str,
    ) -> dict[str, str]:
        access = self.create_access(user_id)
        refresh = self.create_refresh(user_id)

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
        }

    def verify_access(
        self,
        token: str,
    ) -> dict:
        return decode_access_token(token)

    def verify_refresh(
        self,
        token: str,
    ) -> dict:
        return decode_refresh_token(token)