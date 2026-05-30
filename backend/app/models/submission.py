from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.models.enums import SubmissionStatus


class Submission(Base):
    __tablename__ = "submissions"

    __table_args__ = (
        UniqueConstraint(
            "assignment_id",
            "student_id",
            name="uq_assignment_student",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    assignment_id: Mapped[int] = mapped_column(
        ForeignKey(
            "assignments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    student_id = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    submission_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus),
        nullable=False,
        default=SubmissionStatus.PENDING,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    graded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    assignment = relationship(
        "Assignment",
    )

    student = relationship(
        "User",
    )
    grading_result = relationship(
        "GradingResult",
        back_populates="submission",
        uselist=False,
)