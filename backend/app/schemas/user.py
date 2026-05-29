from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import UserRole


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str

    role: UserRole

    prn: str | None = None
    roll_number: str | None = None

    batch: str | None = None
    division: str | None = None
    department: str | None = None

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )