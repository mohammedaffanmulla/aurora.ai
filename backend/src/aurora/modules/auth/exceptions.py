"""
Domain-level exceptions for the auth module.

Services raise these; `router.py` maps them to HTTP status codes. Keeping
them separate from HTTPException lets the service layer stay framework
agnostic and testable without spinning up FastAPI.
"""


class AuthError(Exception):
    """Base class for all auth-domain errors."""


class EmailAlreadyRegisteredError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


class InactiveUserError(AuthError):
    pass


class InvalidTokenError(AuthError):
    """Invalid/expired access, refresh, reset, or verification token."""


class SessionNotFoundError(AuthError):
    pass


class EmailAlreadyVerifiedError(AuthError):
    pass


class UserNotFoundError(AuthError):
    pass
