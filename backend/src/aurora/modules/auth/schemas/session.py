import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_agent: str | None
    ip_address: str | None
    created_at: datetime
    last_seen_at: datetime
    is_current: bool = False
