from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.session import get_db
from app.dependencies.roles import (
    require_roles,
)
from app.models.enums import UserRole
from app.models.user import User
from app.services.grading_service import (
    GradingService,
)

router = APIRouter(
    prefix="/grading",
    tags=["Grading"],
)


@router.post(
    "/submission/{submission_id}",
)
async def grade_submission(
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
        GradingService
        .queue_submission_grading(
            db,
            submission_id,
            current_user,
        )
    )


@router.post(
    "/assignment/{assignment_id}",
)
async def grade_assignment(
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
        GradingService
        .queue_assignment_grading(
            db,
            assignment_id,
            current_user,
        )
    )