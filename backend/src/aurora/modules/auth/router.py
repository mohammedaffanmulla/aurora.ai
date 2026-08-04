from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from aurora.database.session import get_db
from aurora.modules.auth.dependencies import (
    AuthContext,
    get_client_ip,
    get_current_auth_context,
    get_user_agent,
)
from aurora.modules.auth.exceptions import (
    EmailAlreadyRegisteredError,
    EmailAlreadyVerifiedError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    SessionNotFoundError,
    UserNotFoundError,
)
from aurora.modules.auth.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from aurora.modules.auth.schemas.email import ResendVerificationRequest, VerifyEmailRequest
from aurora.modules.auth.schemas.password import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from aurora.modules.auth.services.auth_service import AuthService
from aurora.modules.auth.services.email_service import EmailService
from aurora.modules.auth.services.password_service import PasswordService

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# POST /register
# ---------------------------------------------------------------------------
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = AuthService(db)
    try:
        user = await service.register(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UserResponse.model_validate(user)


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------
@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    try:
        tokens = await service.login(
            email=payload.email,
            password=payload.password,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc
    except InactiveUserError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
    )


# ---------------------------------------------------------------------------
# POST /refresh
# ---------------------------------------------------------------------------
@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    try:
        tokens = await service.refresh(
            raw_refresh_token=payload.refresh_token,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc

    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
    )


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------
@router.get("/me", response_model=UserResponse)
async def get_me(
    ctx: AuthContext = Depends(get_current_auth_context),
) -> UserResponse:
    return UserResponse.model_validate(ctx.user)


# ---------------------------------------------------------------------------
# POST /logout
# ---------------------------------------------------------------------------
@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: RefreshRequest,
    request: Request,
    ctx: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = AuthService(db)
    try:
        await service.logout(
            raw_refresh_token=payload.refresh_token,
            user_id=ctx.user.id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return MessageResponse(message="Logged out successfully")


# ---------------------------------------------------------------------------
# POST /logout-all
# ---------------------------------------------------------------------------
@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(
    request: Request,
    ctx: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = AuthService(db)
    await service.logout_all(
        user_id=ctx.user.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return MessageResponse(message="Logged out of all devices successfully")


# ---------------------------------------------------------------------------
# POST /change-password
# ---------------------------------------------------------------------------
@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    ctx: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = PasswordService(db)
    try:
        await service.change_password(
            user_id=ctx.user.id,
            current_password=payload.current_password,
            new_password=payload.new_password,
            current_session_id=ctx.session_id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return MessageResponse(message="Password changed successfully")


# ---------------------------------------------------------------------------
# POST /forgot-password
# ---------------------------------------------------------------------------
@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = PasswordService(db)
    await service.forgot_password(
        email=payload.email,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    # Always return the same message whether or not the email exists,
    # to avoid leaking account existence.
    return MessageResponse(
        message="If an account with that email exists, a password reset link has been sent"
    )


# ---------------------------------------------------------------------------
# POST /reset-password
# ---------------------------------------------------------------------------
@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = PasswordService(db)
    try:
        await service.reset_password(
            token=payload.token,
            new_password=payload.new_password,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return MessageResponse(message="Password has been reset successfully")


# ---------------------------------------------------------------------------
# POST /verify-email
# ---------------------------------------------------------------------------
@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = EmailService(db)
    try:
        await service.verify_email(
            token=payload.token,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except EmailAlreadyVerifiedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return MessageResponse(message="Email verified successfully")


# ---------------------------------------------------------------------------
# POST /resend-verification
# ---------------------------------------------------------------------------
@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    payload: ResendVerificationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    service = EmailService(db)
    await service.resend_verification(
        email=payload.email,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return MessageResponse(
        message="If an account with that email exists and is unverified, a new verification email has been sent"
    )
