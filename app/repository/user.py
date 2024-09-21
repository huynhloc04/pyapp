from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import desc
from sqlalchemy import select

from app.models.user import User, Group
from app.repository.base import BaseRepository


async def get_user_group(session: AsyncSession, user_id: UUID):
    statement = (
        select(User, Group)
        .join(Group, User.group_id == Group.id)
        .filter(User.id == user_id)
    )
    result = await session.execute(statement)
    return result.first()
