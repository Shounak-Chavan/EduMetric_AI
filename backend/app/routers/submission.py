from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.assignment_service import (
    AssignmentService,
)
from app.db.session import get_db
from app.dependencies.roles import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.submission import SubmissionResponse
from app.services.submission_service import (
    SubmissionService,
)
from app.utils.text_extractor import TextExtractor

router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"],
)


@router.post(
    "/{assignment_id}/upload",
    response_model=SubmissionResponse,
)
async def upload_submission(
    assignment_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.STUDENT, UserRole.SUPER_ADMIN])
    ),
):
    extracted_text = (
        await TextExtractor.extract_text(file)
    )

    return await (
        SubmissionService.upload_submission(
            db,
            assignment_id,
            current_user.id,
            extracted_text,
        )
    )


@router.get(
    "",
    response_model=list[SubmissionResponse],
)
async def get_my_submissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.STUDENT, UserRole.SUPER_ADMIN])
    ),
):
    return await (
        SubmissionService.get_student_submissions(
            db,
            current_user.id,
        )
    )


@router.get(
    "/{submission_id}",
    response_model=SubmissionResponse,
)
async def get_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.STUDENT, UserRole.SUPER_ADMIN])
    ),
):
    submission = (
        await SubmissionService.get_submission_by_id(
            db,
            submission_id,
        )
    )

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found",
        )

    if submission.student_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    return submission

@router.get(
    "/assignment/{assignment_id}",
    response_model=list[SubmissionResponse],
)
async def get_assignment_submissions(
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
    assignment = (
        await AssignmentService.get_assignment_by_id(
            db,
            assignment_id,
        )
    )

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found",
        )

    if (
        current_user.role
        != UserRole.SUPER_ADMIN
        and assignment.teacher_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    return await (
        SubmissionService
        .get_assignment_submissions(
            db,
            assignment_id,
        )
    )