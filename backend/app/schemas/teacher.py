from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TeacherCreate(BaseModel):
    user_id: UUID


class TeacherResponse(BaseModel):
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )