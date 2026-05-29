from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.enums import UserRole
from app.models.user import User


def require_roles(
    allowed_roles: list[UserRole],
):
    def dependency(
        current_user: User = Depends(
            get_current_user
        ),
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Access denied. "
                    f"Required roles: "
                    f"{[r.value for r in allowed_roles]}"
                ),
            )

        return current_user

    return dependency