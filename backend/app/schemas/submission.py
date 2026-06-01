from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import SubmissionStatus

class SubmissionResponse(BaseModel):
    id: int

    assignment_id: int
    student_id: UUID

    status: SubmissionStatus

    submitted_at: datetime
    graded_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )