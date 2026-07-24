from pydantic import BaseModel, Field


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(
        min_length=8,
        max_length=128,
    )


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(
        min_length=8,
        max_length=128,
    )


class PasswordResetResponse(BaseModel):
    message: str


class PasswordValidationResponse(BaseModel):
    valid: bool
    message: str