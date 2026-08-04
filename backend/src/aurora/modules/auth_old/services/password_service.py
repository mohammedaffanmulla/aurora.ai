from __future__ import annotations

from aurora.modules.auth.security import (
    hash_password,
    verify_password,
)


class PasswordService:
    @staticmethod
    def hash(password: str) -> str:
        """
        Hash a plain-text password.
        """
        return hash_password(password)

    @staticmethod
    def verify(
        password: str,
        password_hash: str,
    ) -> bool:
        """
        Verify a plain-text password against its hash.
        """
        return verify_password(
            password,
            password_hash,
        )

    @staticmethod
    def validate(password: str) -> None:
        """
        Basic password validation.
        """
        if len(password) < 8:
            raise ValueError(
                "Password must contain at least 8 characters."
            )

        if len(password) > 128:
            raise ValueError(
                "Password must not exceed 128 characters."
            )