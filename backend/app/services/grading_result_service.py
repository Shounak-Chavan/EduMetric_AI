from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grading_result import GradingResult
from app.models.submission import Submission


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

        grading_result.marks = marks
        grading_result.feedback = feedback

        await db.commit()
        await db.refresh(
            grading_result
        )

        return grading_result