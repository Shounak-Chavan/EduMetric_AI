from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.roles import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentUpdate,
)
from app.services.assignment_service import (
    AssignmentService,
)
from app.utils.text_extractor import TextExtractor

router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"],
)


@router.post(
    "",
    response_model=AssignmentResponse,
)
async def create_assignment(
    data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.TEACHER])
    ),
):
    return await AssignmentService.create_assignment(
        db=db,
        teacher_id=current_user.id,
        data=data,
    )


@router.get(
    "",
    response_model=list[AssignmentResponse],
)
async def get_my_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.TEACHER])
    ),
):
    return await AssignmentService.get_teacher_assignments(
        db,
        current_user.id,
    )


@router.get(
    "/available",
    response_model=list[AssignmentResponse],
)
async def get_available_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.STUDENT])
    ),
):
    """
    Get all published assignments matching student's
    batch, division, and department.
    """
    if not current_user.batch or not current_user.division or not current_user.department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile incomplete. Missing batch, division, or department.",
        )

    return await AssignmentService.get_student_assignments(
        db,
        batch=current_user.batch,
        division=current_user.division,
        department=current_user.department,
    )


@router.get(
    "/{assignment_id}",
    response_model=AssignmentResponse,
)
async def get_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
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

    return assignment


@router.put(
    "/{assignment_id}",
    response_model=AssignmentResponse,
)
async def update_assignment(
    assignment_id: int,
    data: AssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.TEACHER])
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

    if assignment.teacher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    return await AssignmentService.update_assignment(
        db,
        assignment,
        data,
    )


@router.post(
    "/{assignment_id}/publish",
    response_model=AssignmentResponse,
)
async def publish_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.TEACHER])
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

    if assignment.teacher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    return await AssignmentService.publish_assignment(
        db,
        assignment,
    )


@router.delete(
    "/{assignment_id}",
)
async def delete_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.TEACHER])
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

    if assignment.teacher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    await AssignmentService.delete_assignment(
        db,
        assignment,
    )

    return {
        "message":
        "Assignment deleted successfully"
    }

@router.post(
    "/{assignment_id}/reference-solution",
    response_model=AssignmentResponse,
)
async def upload_reference_solution(
    assignment_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.TEACHER])
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

    if assignment.teacher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    extracted_text = (
        await TextExtractor.extract_text(
            file
        )
    )

    return (
        await AssignmentService
        .upload_reference_solution(
            db,
            assignment,
            extracted_text,
        )
    )