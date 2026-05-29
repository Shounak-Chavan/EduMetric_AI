from uuid import UUID

from pydantic import BaseModel

from app.models.enums import UserRole


class CurrentUser(BaseModel):
    id: UUID
    email: str
    role: UserRole