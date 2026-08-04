"""
JWT access-token handling plus opaque-token helpers.

Access tokens are short-lived JWTs (stateless, verified via signature).
Refresh / password-reset / email-verification tokens are random opaque
strings: the raw value is handed to the client, only its SHA-256 hash is
persisted server-side (so a DB leak doesn't expose usable tokens), and they
are looked up + revoked directly in Postgres. This is why they are NOT JWTs.
"""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any

from jose import JWTError, jwt

from aurora.modules.auth.config import settings


class TokenType(StrEnum):
    ACCESS = "access"


class TokenError(Exception):
    """Raised for any invalid/expired/malformed JWT."""


def create_access_token(
    *, user_id: uuid.UUID, session_id: uuid.UUID, extra_claims: dict[str, Any] | None = None
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.auth_access_token_expire_minutes)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "sid": str(session_id),
        "type": TokenType.ACCESS,
        "iat": now,
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.auth_jwt_secret_key, algorithm=settings.auth_jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode + validate an access token. Raises TokenError on any failure."""
    try:
        payload = jwt.decode(token, settings.auth_jwt_secret_key, algorithms=[settings.auth_jwt_algorithm])
    except JWTError as exc:
        raise TokenError("Invalid or expired access token") from exc

    if payload.get("type") != TokenType.ACCESS:
        raise TokenError("Unexpected token type")

    return payload


# ---------------------------------------------------------------------------
# Opaque tokens (refresh tokens, password reset, email verification)
# ---------------------------------------------------------------------------

def generate_opaque_token() -> str:
    """A URL-safe, cryptographically random token to hand to the client."""
    return secrets.token_urlsafe(48)


def hash_opaque_token(raw_token: str) -> str:
    """One-way hash of an opaque token for safe DB storage/lookup."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def refresh_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.auth_refresh_token_expire_days)


def password_reset_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=settings.auth_password_reset_token_expire_minutes)


def email_verification_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=settings.auth_email_verification_token_expire_hours)
