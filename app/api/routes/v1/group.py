from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.db.session import get_session
from app.core.deps import get_current_user
from app.models.user import User, Group, GroupBase, UpdateGroup
from app.repository.base import BaseRepository

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", response_model=Group, status_code=201, summary="Create a new group.")
async def create_group(
    data: GroupBase, session: AsyncSession = Depends(get_session)
) -> Group:
    #   Querying database to check group already exist
    group_name = await BaseRepository(Group).get_by_item(
        session=session, name=data.name
    )
    if group_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This group is already exist. Please create a new one!",
        )
    group_db = await BaseRepository(Group).create(
        session=session,
        name=data.name,
        discount_percent=data.discount_percent,
    )
    return group_db


@router.get("", response_model=List[Group], status_code=200, summary="Get all groups")
async def list_group(session: AsyncSession = Depends(get_session)) -> List[Group]:
    groups = await BaseRepository(Group).get_all(session=session)
    return groups


@router.get(
    "/{group_id}", response_model=Group, status_code=200, summary="Get current group."
)
async def get_group(
    group_id: UUID, session: AsyncSession = Depends(get_session)
) -> Group:
    group = await BaseRepository(Group).get_by_id(session=session, id=group_id)
    return group


@router.patch(
    "/{group_id}", response_model=Group, status_code=200, summary="Update group."
)
async def update_group(
    group_id: UUID,
    data: UpdateGroup,
    session: AsyncSession = Depends(get_session),
) -> Group:
    group = await BaseRepository(Group).get_by_id(session=session, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found!",
        )
    data_to_update = dict(data)
    group_db = await BaseRepository(Group).update(
        session=session, item=group, **data_to_update
    )
    return group_db


@router.delete("/{group_id}", status_code=200, summary="Delete group.")
async def delete_group(
    group_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Group:
    group = await BaseRepository(Group).get_by_id(session=session, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found!",
        )
    await BaseRepository(Group).delete(session=session, item=group)
    return {"message": "Delete group successfully!"}
