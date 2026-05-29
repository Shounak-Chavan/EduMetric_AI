from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment
from app.models.enums import SubmissionStatus
from app.models.submission import Submission


class SubmissionService:

    @staticmethod
    async def upload_submission(
        db: AsyncSession,
        assignment_id: int,
        student_id: UUID,
        extracted_text: str,
    ) -> Submission:

        result = await db.execute(
            select(Assignment).where(
                Assignment.id == assignment_id
            )
        )

        assignment = result.scalar_one_or_none()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found",
            )

        if not assignment.is_published:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignment not published",
            )

        if assignment.due_date < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submission deadline has passed",
            )

        result = await db.execute(
            select(Submission).where(
                Submission.assignment_id == assignment_id,
                Submission.student_id == student_id,
            )
        )

        submission = result.scalar_one_or_none()

        if submission:

            submission.submission_text = extracted_text

            submission.status = (
                SubmissionStatus.PENDING
            )

            submission.submitted_at = (
                datetime.now(UTC)
            )

            submission.graded_at = None

        else:

            submission = Submission(
                assignment_id=assignment_id,
                student_id=student_id,
                submission_text=extracted_text,
                status=SubmissionStatus.PENDING,
            )

            db.add(submission)

        await db.commit()
        await db.refresh(submission)

        return submission

    @staticmethod
    async def get_submission_by_id(
        db: AsyncSession,
        submission_id: int,
    ) -> Submission | None:

        result = await db.execute(
            select(Submission).where(
                Submission.id == submission_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_student_submissions(
        db: AsyncSession,
        student_id: UUID,
    ) -> list[Submission]:

        result = await db.execute(
            select(Submission).where(
                Submission.student_id == student_id
            )
        )

        return list(result.scalars().all())