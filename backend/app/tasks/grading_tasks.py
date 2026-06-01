from datetime import UTC, datetime
import asyncio

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.db.session import create_task_async_sessionmaker
from app.models.assignment import Assignment
from app.models.enums import SubmissionStatus
from app.models.submission import Submission
from app.services.grading_service import GradingService


@celery_app.task
def grade_submission_task(
    submission_id: int,
):
    asyncio.run(_grade_submission(submission_id))


async def _grade_submission(
    submission_id: int,
):
    engine, session_factory = create_task_async_sessionmaker()

    try:
        async with session_factory() as db:

            result = await db.execute(
                select(Submission).where(
                    Submission.id == submission_id
                )
            )

            submission = result.scalar_one_or_none()

            if not submission:
                return

            result = await db.execute(
                select(Assignment).where(
                    Assignment.id
                    == submission.assignment_id
                )
            )

            assignment = result.scalar_one_or_none()

            if not assignment:
                return

            await GradingService.grade_submission(
                db=db,
                submission=submission,
                assignment=assignment,
            )
    finally:
        if engine is not None:
            await engine.dispose()


@celery_app.task
def check_due_assignments():
    asyncio.run(_check_due_assignments())


async def _check_due_assignments():
    engine, session_factory = create_task_async_sessionmaker()

    try:
        async with session_factory() as db:

            result = await db.execute(
                select(Submission)
                .join(Assignment)
                .where(
                    Assignment.due_date
                    <= datetime.now(UTC),
                    Assignment.is_published.is_(True),
                    Submission.status
                    == SubmissionStatus.PENDING,
                )
            )

            submissions = result.scalars().all()

            for submission in submissions:

                grade_submission_task.delay(
                    submission.id
                )
    finally:
        if engine is not None:
            await engine.dispose()