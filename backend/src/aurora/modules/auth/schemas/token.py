from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshToken(BaseModel):
    refresh_token: str
    token_type: str = "bearer"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    type: str
    exp: datetime


class RefreshTokenPayload(BaseModel):
    sub: str
    type: str = "refresh"
    exp: datetime


class TokenBlacklistResponse(BaseModel):
    message: str


class TokenValidationResponse(BaseModel):
    valid: bool
    expires_at: datetime | None = None


class TokenMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    token_id: str
    user_id: str
    issued_at: datetime
    expires_at: datetime
    revoked: bool