from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from datetime import datetime
from typing import Any, List, Optional
from sqlalchemy import select, func
from app.logging.logger import item_logger
from sqlalchemy.sql.expression import desc
from app.api.enums import ItemStatus


class BaseRepository:
    def __init__(self, model):
        self.model = model

    async def count_all(self, session: AsyncSession) -> int:
        """Count all records"""
        statement = select(func.count()).select_from(self.model)
        count = await session.execute(statement)
        count = count.scalar()
        return count

    async def count_by(self, session: AsyncSession, **kwargs) -> int:
        """Count all records by a filter"""
        statement = select(func.count()).select_from(self.model).filter_by(**kwargs)
        count = await session.execute(statement)
        count = count.scalar()
        return count

    async def get_all(self, session: AsyncSession) -> Any:
        """Retrieve all records"""
        statement = select(self.model)
        items = await session.execute(statement)
        items = items.scalars().all()
        return items

    async def get_all_by(self, session: AsyncSession, **kwargs) -> Any:
        """Retrieve all records"""
        statement = select(self.model).filter_by(**kwargs)
        items = await session.execute(statement)
        items = items.scalars().all()
        return items

    async def get_all_paginated(
        self, session: AsyncSession, skip: int = 0, limit: int = 10
    ) -> Any:
        """Retrieve all records"""
        statement = select(self.model).offset(skip).limit(limit)
        items = await session.execute(statement)
        items = items.scalars().all()
        return items

    async def get_all_paginated_by(
        self, session: AsyncSession, skip: int = 0, limit: int = 10, **kwargs
    ) -> Any:
        """Retrieve all records by a filter"""
        statement = (
            select(self.model)
            .order_by(desc(self.model.created_at))
            .filter_by(**kwargs)
            .offset(skip)
            .limit(limit)
        )
        items = await session.execute(statement)
        items = items.scalars().all()
        return items

    async def get_by_id(self, session: AsyncSession, id: str) -> Any:
        """Retrieve a record by id"""
        item = await session.get(self.model, id)
        if item:
            return item
        else:
            raise HTTPException(
                status_code=404, detail=f"No record found with id: {id}"
            )

    async def get_by_item(self, session: AsyncSession, **kwargs) -> Any:
        """Retrieve a record by id"""
        statement = select(self.model).filter_by(**kwargs)
        item = await session.execute(statement)
        item = item.scalars().first()
        if item:
            return item

    async def update_by_id(self, session: AsyncSession, id: str, **kwargs) -> Any:
        """Update a record by id"""
        item = await session.get(self.model, id)
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return await self.update(session, item, **kwargs)

    async def check_exist(self, session: AsyncSession, **kwargs) -> Any:
        """Check if a record exists"""
        try:
            statement = select(self.model).filter_by(**kwargs)
            item = await session.execute(statement)
            item = item.scalar()
            return item
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error checking record: {e}")

    async def create(self, session: AsyncSession, **kwargs) -> Any:
        """Create a record"""
        try:
            item = self.model(**kwargs)
            session.add(item)
            await session.commit()
            await session.refresh(item)
            # Log the item creation
            if hasattr(item, "id"):  # Some models may not have an id
                item_logger(item_id=item.id, status=ItemStatus.created, message=kwargs)
            else:
                item_logger(status=ItemStatus.created, message=kwargs)
            return item
        except Exception as e:
            await session.rollback()
            # Log the item creation failure
            item_logger(status=ItemStatus.failed, message=f"Error creating record: {e}")
            raise HTTPException(status_code=400, detail=f"Error creating record: {e}")

    async def update(self, session: AsyncSession, item: Any, **kwargs) -> Any:
        """Update a record"""
        try:
            for key, value in kwargs.items():
                if value:
                    setattr(item, key, value)
            await session.commit()
            # Log the item update
            if hasattr(item, "id"):
                item_logger(item_id=item.id, status=ItemStatus.updated, message=kwargs)
            else:
                item_logger(status=ItemStatus.updated, message=kwargs)
            return item
        except Exception as e:
            await session.rollback()
            # Log the item update failure
            if hasattr(item, "id"):  # Some models may not have an id
                item_logger(
                    item_id=item.id,
                    status=ItemStatus.failed,
                    message=f"Error updating record: {e}",
                )
            else:
                item_logger(
                    status=ItemStatus.failed, message=f"Error updating record: {e}"
                )
            raise HTTPException(status_code=400, detail=f"Error updating record: {e}")

    async def create_all(self, session: AsyncSession, data_lst: List[dict]) -> Any:
        """Create a record"""
        try:
            items = [self.model(**kwargs) for kwargs in data_lst]
            session.add_all(items)
            await session.commit()
            for item in items:
                await session.refresh(item)
            return items
        except Exception as e:
            await session.rollback()
            # Log the item creation failure
            item_logger(status=ItemStatus.failed, message=f"Error creating record: {e}")
            raise HTTPException(status_code=400, detail=f"Error creating record: {e}")

    async def delete(self, session: AsyncSession, item: Any) -> Any:
        """Delete a record"""
        try:
            await session.delete(item)
            await session.commit()
            # Log the item deletion
            if hasattr(item, "id"):
                item_logger(item_id=item.id, status=ItemStatus.deleted, message=None)
            else:
                item_logger(status=ItemStatus.deleted, message=None)
        except Exception as e:
            await session.rollback()
            # Log the item deletion failure
            if hasattr(item, "id"):
                item_logger(
                    item_id=item.id,
                    status=ItemStatus.failed,
                    message=f"Error deleting record: {e}",
                )
            else:
                item_logger(
                    status=ItemStatus.failed, message=f"Error deleting record: {e}"
                )
            raise HTTPException(status_code=400, detail=f"Error deleting record: {e}")

    async def delete_by_id(self, session: AsyncSession, id: str) -> Any:
        """Delete a record by id"""
        item = await session.get(self.model, id)
        if item:
            await self.delete(session, item)
        else:
            raise HTTPException(
                status_code=404, detail=f"No record found with id: {id}"
            )

    async def delete_all(self, session: AsyncSession, **kwargs) -> Any:
        """Delete a list of record"""
        statement = self.model.__table__.delete().filter_by(**kwargs)
        await session.execute(statement)
        await session.commit()
