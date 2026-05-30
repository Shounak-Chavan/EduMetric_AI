from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return UserResponse.model_validate(
        current_user
    )


@router.post(
    "/sync",
    response_model=UserResponse,
)
async def sync_user(
    current_user: User = Depends(
        get_current_user
    ),
):
    return UserResponse.model_validate(
        current_user
    )