from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.enums import GradingMode


class AssignmentCreate(BaseModel):
    title: str
    description: str | None = None

    batch: str
    division: str
    department: str

    grading_mode: GradingMode

    grading_min_marks: int = 0
    grading_max_marks: int = 10

    due_date: datetime

    @model_validator(mode="after")
    def validate_marks_range(self):
        if self.grading_min_marks >= self.grading_max_marks:
            raise ValueError(
                "grading_min_marks must be less than grading_max_marks"
            )
        return self


class AssignmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

    batch: str | None = None
    division: str | None = None
    department: str | None = None

    grading_mode: GradingMode | None = None

    grading_min_marks: int | None = None
    grading_max_marks: int | None = None

    due_date: datetime | None = None


class AssignmentResponse(BaseModel):
    id: int

    title: str
    description: str | None

    teacher_id: UUID

    batch: str
    division: str
    department: str

    grading_mode: GradingMode

    grading_min_marks: int
    grading_max_marks: int

    due_date: datetime

    is_published: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ReferenceSolutionUploadResponse(BaseModel):
    message: str