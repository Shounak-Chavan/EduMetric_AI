from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment
from app.models.enums import (
    SubmissionStatus,
    UserRole,
)
from app.models.grading_result import GradingResult
from app.models.submission import Submission
from app.models.user import User
from app.tasks.grading_tasks import (
    grade_submission_task,
)
from app.utils.grader import grade_text


class GradingService:

    @staticmethod
    async def grade_submission(
        db: AsyncSession,
        submission: Submission,
        assignment: Assignment,
    ) -> GradingResult:

        submission.status = (
            SubmissionStatus.GRADING
        )

        await db.commit()

        try:

            if not submission.submission_text.strip():

                grading_result = GradingResult(
                    submission_id=submission.id,
                    marks=assignment.grading_min_marks,
                    feedback=(
                        "No submission "
                        "content found."
                    ),
                    llm_provider="system",
                )

                db.add(grading_result)

                submission.status = (
                    SubmissionStatus.COMPLETED
                )

                submission.graded_at = (
                    datetime.now(UTC)
                )

                await db.commit()
                await db.refresh(
                    grading_result
                )

                return grading_result

            if not assignment.reference_solution_text:
                raise ValueError(
                    "Reference solution not found."
                )

            result, provider = await grade_text(
                reference_solution=(
                    assignment.reference_solution_text
                ),
                submission=(
                    submission.submission_text
                ),
            )

            normalized_marks = round(
                assignment.grading_min_marks
                + (
                    (result.marks / 10)
                    * (
                        assignment.grading_max_marks
                        - assignment.grading_min_marks
                    )
                )
            )

            grading_result = GradingResult(
                submission_id=submission.id,
                marks=normalized_marks,
                feedback=result.feedback,
                llm_provider=provider,
            )

            db.add(grading_result)

            submission.status = (
                SubmissionStatus.COMPLETED
            )

            submission.graded_at = (
                datetime.now(UTC)
            )

            await db.commit()
            await db.refresh(
                grading_result
            )

            return grading_result

        except Exception:

            await db.rollback()

            submission.status = (
                SubmissionStatus.FAILED
            )

            await db.commit()

            raise

    @staticmethod
    async def queue_submission_grading(
        db: AsyncSession,
        submission_id: int,
        current_user: User,
    ):

        result = await db.execute(
            select(Submission).where(
                Submission.id == submission_id
            )
        )

        submission = (
            result.scalar_one_or_none()
        )

        if not submission:
            raise HTTPException(
                status_code=404,
                detail="Submission not found.",
            )

        result = await db.execute(
            select(Assignment).where(
                Assignment.id
                == submission.assignment_id
            )
        )

        assignment = (
            result.scalar_one_or_none()
        )

        if (
            current_user.role
            != UserRole.SUPER_ADMIN
            and assignment.teacher_id
            != current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="Access denied.",
            )

        if submission.status != SubmissionStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Submission already graded.",
            )

        grade_submission_task.delay(
            submission.id
        )

        return {
            "message":
            "Grading task queued."
        }

    @staticmethod
    async def queue_assignment_grading(
        db: AsyncSession,
        assignment_id: int,
        current_user: User,
    ):

        result = await db.execute(
            select(Assignment).where(
                Assignment.id == assignment_id
            )
        )

        assignment = (
            result.scalar_one_or_none()
        )

        if not assignment:
            raise HTTPException(
                status_code=404,
                detail="Assignment not found.",
            )

        if (
            current_user.role
            != UserRole.SUPER_ADMIN
            and assignment.teacher_id
            != current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="Access denied.",
            )

        result = await db.execute(
            select(Submission).where(
                Submission.assignment_id
                == assignment_id,
                Submission.status
                == SubmissionStatus.PENDING,
            )
        )

        submissions = (
            result.scalars().all()
        )

        for submission in submissions:

            grade_submission_task.delay(
                submission.id
            )

        return {
            "message":
            f"{len(submissions)} "
            "submissions queued."
        }