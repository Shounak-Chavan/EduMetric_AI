from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LLMGradingResult(BaseModel):
    marks: int
    feedback: str


class GradingResultUpdate(BaseModel):
    marks: int
    feedback: str


class GradingResultResponse(BaseModel):
    id: UUID
    submission_id: int

    marks: int
    feedback: str

    llm_provider: str

    graded_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
