from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentUpdate,
)


class AssignmentService:

    @staticmethod
    async def create_assignment(
        db: AsyncSession,
        teacher_id: UUID,
        data: AssignmentCreate,
    ) -> Assignment:

        assignment = Assignment(
            title=data.title,
            description=data.description,
            teacher_id=teacher_id,
            batch=data.batch,
            division=data.division,
            department=data.department,
            grading_mode=data.grading_mode,
            grading_min_marks=data.grading_min_marks,
            grading_max_marks=data.grading_max_marks,
            due_date=data.due_date,
        )

        db.add(assignment)

        await db.commit()
        await db.refresh(assignment)

        return assignment

    @staticmethod
    async def get_assignment_by_id(
        db: AsyncSession,
        assignment_id: int,
    ) -> Assignment | None:

        result = await db.execute(
            select(Assignment).where(
                Assignment.id == assignment_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_teacher_assignments(
        db: AsyncSession,
        teacher_id: UUID,
    ) -> list[Assignment]:

        result = await db.execute(
            select(Assignment).where(
                Assignment.teacher_id == teacher_id
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def get_student_assignments(
        db: AsyncSession,
        batch: str,
        division: str,
        department: str,
    ) -> list[Assignment]:
        """
        Get all published assignments matching student's
        batch, division, and department.
        """
        result = await db.execute(
            select(Assignment).where(
                Assignment.is_published == True,
                Assignment.batch == batch,
                Assignment.division == division,
                Assignment.department == department,
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def update_assignment(
        db: AsyncSession,
        assignment: Assignment,
        data: AssignmentUpdate,
    ) -> Assignment:

        if assignment.is_published:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Published assignments "
                    "cannot be modified."
                ),
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                assignment,
                key,
                value,
            )

        await db.commit()
        await db.refresh(assignment)

        return assignment

    @staticmethod
    async def upload_reference_solution(
        db: AsyncSession,
        assignment: Assignment,
        extracted_text: str,
    ) -> Assignment:

        if assignment.is_published:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Published assignments "
                    "cannot be modified."
                ),
            )

        assignment.reference_solution_text = (
            extracted_text
        )

        await db.commit()
        await db.refresh(assignment)

        return assignment

    @staticmethod
    async def publish_assignment(
        db: AsyncSession,
        assignment: Assignment,
    ) -> Assignment:

        if not assignment.reference_solution_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Reference solution "
                    "required before publishing."
                ),
            )

        assignment.is_published = True

        await db.commit()
        await db.refresh(assignment)

        return assignment

    @staticmethod
    async def delete_assignment(
        db: AsyncSession,
        assignment: Assignment,
    ) -> None:

        if assignment.is_published:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Published assignments "
                    "cannot be deleted."
                ),
            )

        await db.delete(assignment)
        await db.commit()
    