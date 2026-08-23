from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, hash_password, verify_password
from app.infrastructure.tables import UserRecord


async def register_user(session: AsyncSession, email: str, password: str) -> str:
    normalized = email.strip().lower()
    existing = await session.scalar(select(UserRecord).where(UserRecord.email == normalized))
    if existing:
        raise ValueError("User already exists")
    user = UserRecord(email=normalized, password_hash=hash_password(password))
    session.add(user)
    await session.commit()
    return create_access_token(str(user.id))


async def authenticate_user(session: AsyncSession, email: str, password: str) -> str | None:
    normalized = email.strip().lower()
    user = await session.scalar(select(UserRecord).where(UserRecord.email == normalized))
    if not user or not verify_password(password, user.password_hash):
        return None
    return create_access_token(str(user.id))
