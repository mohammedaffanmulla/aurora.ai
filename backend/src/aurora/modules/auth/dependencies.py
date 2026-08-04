import uuid
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.session import get_db
from aurora.database.models import User
from aurora.modules.auth.repositories.session_repository import SessionRepository
from aurora.modules.auth.repositories.user_repository import UserRepository
from aurora.modules.auth.security.jwt import TokenError, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


@dataclass
class AuthContext:
    """Everything a protected endpoint needs about the caller's current request."""

    user: User
    session_id: uuid.UUID


def get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> str | None:
    return request.headers.get("user-agent")


async def get_current_auth_context(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

    try:
        payload = decode_access_token(token)
    except TokenError:
        raise credentials_exception

    try:
        user_id = uuid.UUID(payload["sub"])
        session_id = uuid.UUID(payload["sid"])
    except (KeyError, ValueError, TypeError):
        raise credentials_exception

    session = await SessionRepository(db).get_by_id(session_id)
    if session is None or not session.is_active:
        raise credentials_exception

    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    return AuthContext(user=user, session_id=session_id)


async def get_current_user(ctx: AuthContext = Depends(get_current_auth_context)) -> User:
    return ctx.user
