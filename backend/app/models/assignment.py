from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import GradingMode


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    teacher_id: Mapped[UUID] = mapped_column(
        ForeignKey("teachers.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reference_solution_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    batch: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    division: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    department: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    grading_mode: Mapped[GradingMode] = mapped_column(
        Enum(GradingMode),
        nullable=False,
        default=GradingMode.MEDIUM,
    )

    grading_min_marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    grading_max_marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
    )

    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    teacher = relationship(
        "Teacher",
    )