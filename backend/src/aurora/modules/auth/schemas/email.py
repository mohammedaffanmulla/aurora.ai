from pydantic import BaseModel, EmailStr


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class EmailVerificationResponse(BaseModel):
    message: str


class EmailResponse(BaseModel):
    email: EmailStr
    verified: bool