from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment
from app.models.enums import UserRole
from app.models.grading_result import GradingResult
from app.models.submission import Submission
from app.models.user import User


class GradingResultService:

    @staticmethod
    async def get_submission_result(
        db: AsyncSession,
        submission_id: int,
    ) -> GradingResult:

        result = await db.execute(
            select(GradingResult).where(
                GradingResult.submission_id
                == submission_id
            )
        )

        grading_result = (
            result.scalar_one_or_none()
        )

        if not grading_result:
            raise HTTPException(
                status_code=404,
                detail="Grading result not found.",
            )

        return grading_result

    @staticmethod
    async def get_assignment_results(
        db: AsyncSession,
        assignment_id: int,
    ) -> list[GradingResult]:

        result = await db.execute(
            select(GradingResult)
            .join(Submission)
            .where(
                Submission.assignment_id
                == assignment_id
            )
        )

        return list(
            result.scalars().all()
        )

    @staticmethod
    async def update_result(
        db: AsyncSession,
        submission_id: int,
        marks: int,
        feedback: str,
        current_user: User,
    ) -> GradingResult:

        result = await db.execute(
            select(GradingResult).where(
                GradingResult.submission_id
                == submission_id
            )
        )

        grading_result = (
            result.scalar_one_or_none()
        )

        if not grading_result:
            raise HTTPException(
                status_code=404,
                detail="Grading result not found.",
            )

        result = await db.execute(
            select(Submission).where(
                Submission.id
                == submission_id
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

        grading_result.marks = marks
        grading_result.feedback = feedback

        await db.commit()
        await db.refresh(
            grading_result
        )

        return grading_result