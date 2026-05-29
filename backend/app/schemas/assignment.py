from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import GradingMode


class AssignmentCreate(BaseModel):
    title: str
    description: str | None = None

    batch: str
    division: str
    department: str

    grading_mode: GradingMode

    due_date: datetime


class AssignmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

    batch: str | None = None
    division: str | None = None
    department: str | None = None

    grading_mode: GradingMode | None = None

    due_date: datetime | None = None


class AssignmentResponse(BaseModel):
    id: int

    title: str
    description: str | None

    teacher_id: str

    batch: str
    division: str
    department: str

    grading_mode: GradingMode

    due_date: datetime

    is_published: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ReferenceSolutionUploadResponse(BaseModel):
    message: str