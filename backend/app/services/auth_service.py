from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole
from app.models.teacher import Teacher
from app.models.user import User


def _extract_full_name(claims: dict[str, object], email: str) -> str:
    user_metadata = claims.get("user_metadata")

    if isinstance(user_metadata, dict):
        full_name = user_metadata.get("full_name") or user_metadata.get("name")
        if isinstance(full_name, str) and full_name.strip():
            return full_name.strip()

    for field_name in ("name", "full_name", "preferred_username"):
        field_value = claims.get(field_name)
        if isinstance(field_value, str) and field_value.strip():
            return field_value.strip()

    local_part = email.split("@", 1)[0].strip()
    return local_part or email


async def sync_authenticated_user(
    db: AsyncSession,
    claims: dict[str, object],
) -> User:
    user_id = claims.get("sub")
    email = claims.get("email")

    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("Token is missing a valid subject")

    if not isinstance(email, str) or not email.strip():
        raise ValueError("Token is missing a valid email")

    user_uuid = UUID(user_id)
    normalized_email = email.strip().lower()
    full_name = _extract_full_name(claims, normalized_email)

    result = await db.execute(
        select(User).where(
            User.id == user_uuid,
        )
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            id=user_uuid,
            email=normalized_email,
            full_name=full_name,
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add(user)
        await db.flush()
    else:
        if user.email != normalized_email:
            user.email = normalized_email

        if full_name and user.full_name != full_name:
            user.full_name = full_name

    if user.role != UserRole.SUPER_ADMIN:
        teacher_result = await db.execute(
            select(Teacher).where(
                Teacher.user_id == user.id,
            )
        )
        is_teacher = teacher_result.scalar_one_or_none() is not None
        expected_role = UserRole.TEACHER if is_teacher else UserRole.STUDENT

        if user.role != expected_role:
            user.role = expected_role

    await db.commit()
    await db.refresh(user)

    return user