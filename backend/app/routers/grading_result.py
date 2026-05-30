from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.roles import (
    require_roles,
)
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.grading_result import (
    GradingResultResponse,
    GradingResultUpdate,
)
from app.services.grading_result_service import (
    GradingResultService,
)

router = APIRouter(
    prefix="/grading-results",
    tags=["Grading Results"],
)


@router.get(
    "/submission/{submission_id}",
    response_model=GradingResultResponse,
)
async def get_submission_result(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [
                UserRole.TEACHER,
                UserRole.SUPER_ADMIN,
            ]
        )
    ),
):

    return await (
        GradingResultService
        .get_submission_result(
            db,
            submission_id,
        )
    )


@router.get(
    "/assignment/{assignment_id}",
    response_model=list[
        GradingResultResponse
    ],
)
async def get_assignment_results(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [
                UserRole.TEACHER,
                UserRole.SUPER_ADMIN,
            ]
        )
    ),
):

    return await (
        GradingResultService
        .get_assignment_results(
            db,
            assignment_id,
        )
    )


@router.patch(
    "/submission/{submission_id}",
    response_model=GradingResultResponse,
)
async def update_result(
    submission_id: int,
    data: GradingResultUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [
                UserRole.TEACHER,
                UserRole.SUPER_ADMIN,
            ]
        )
    ),
):

    return await (
        GradingResultService
        .update_result(
            db=db,
            submission_id=submission_id,
            marks=data.marks,
            feedback=data.feedback,
            current_user=current_user,
        )
    )