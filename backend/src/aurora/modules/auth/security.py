from datetime import datetime, timedelta, UTC
from typing import Any

from jose import JWTError, jwt
from pwdlib import PasswordHash

from aurora.core.config import settings

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain text password using Argon2."""
    return password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plain text password against its hash."""
    return password_hasher.verify(password, hashed_password)


def create_access_token(subject: str) -> str:
    """Create a JWT access token."""
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
