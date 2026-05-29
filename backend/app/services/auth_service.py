from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserRole
from app.models.user import User


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    result = await db.execute(
        select(User).where(
            User.email == email
        )
    )

    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    *,
    user_id,
    email: str,
    full_name: str,
    role: UserRole = UserRole.STUDENT,
) -> User:
    user = User(
        id=user_id,
        email=email,
        full_name=full_name,
        role=role,
        is_active=True,
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user