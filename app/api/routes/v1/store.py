from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.db.session import get_session
from app.core.deps import get_current_user
from app.api.enums import ShippingMethod as ShippingMethodEnum
from app.models import User, Store, StoreBase, ShippingMethod
from app.repository import BaseRepository

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post("", response_model=Store, status_code=201, summary="Create a new store.")
async def create_store(
    data: StoreBase,
    session: AsyncSession = Depends(get_session),
) -> Store:
    data_to_add = dict(data)
    store_db = await BaseRepository(Store).create(session=session, **data_to_add)
    return store_db


@router.post(
    "/locations",
    response_model=List[str],
    status_code=200,
    summary="Get all store locations",
    description="shipping_method: 'freeship' or 'pickup'.",
)
async def list_store_address(
    data: ShippingMethod, session: AsyncSession = Depends(get_session)
) -> List[str]:
    if data.shipping_method == ShippingMethodEnum.pickup:
        warehouse = await BaseRepository(Store.address).get_all_by(
            session=session, is_store=True
        )
        return warehouse
    #   Shipping method is Pickup
    stores = await BaseRepository(Store.address).get_all_by(
        session=session, is_store=False
    )
    return stores


@router.delete("/{store_id}", status_code=200, summary="Delete store.")
async def delete_store(
    store_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Dict:
    store = await BaseRepository(Store).get_by_id(session=session, id=store_id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found!",
        )
    await BaseRepository(Store).delete(session=session, item=store)
    return {"message": "Delete store successfully!"}
