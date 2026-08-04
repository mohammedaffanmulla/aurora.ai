"""Password hashing helpers built on Passlib's bcrypt backend."""
from passlib.context import CryptContext

from aurora.modules.auth.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.auth_bcrypt_rounds,
)


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password for storage."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """True if the stored hash was made with outdated params (e.g. rounds changed)."""
    return pwd_context.needs_update(hashed_password)
