from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_name: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    expires_at: datetime
    created_at: datetime


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]


class RevokeSessionRequest(BaseModel):
    session_id: UUID


class RevokeAllSessionsResponse(BaseModel):
    message: str