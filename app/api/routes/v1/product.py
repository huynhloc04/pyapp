from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.db.session import get_session
from app.core.deps import get_current_user
from app.repository import BaseRepository, get_user_group
from app.models import (
    User,
    Product,
    ProductBase,
    UpdateProduct,
    ProductDiscountPrice,
    ProductPrice,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "", response_model=Product, status_code=201, summary="Create a new product."
)
async def create_product(
    data: ProductBase,
    session: AsyncSession = Depends(get_session),
) -> Product:
    data_to_add = dict(data)
    product_db = await BaseRepository(Product).create(session=session, **data_to_add)
    return product_db


@router.get(
    "", response_model=List[Product], status_code=200, summary="Get all products"
)
async def list_product(session: AsyncSession = Depends(get_session)) -> List[Product]:
    products = await BaseRepository(Product).get_all(session=session)
    return products


@router.get(
    "/{product_id}",
    response_model=Product,
    status_code=200,
    summary="Get product by index.",
)
async def get_product(
    product_id: UUID, session: AsyncSession = Depends(get_session)
) -> Product:
    product = await BaseRepository(Product).get_by_id(session=session, id=product_id)
    return product


@router.patch(
    "/{product_id}",
    response_model=Product,
    status_code=200,
    summary="Update product.",
)
async def update_product(
    product_id: UUID,
    data: UpdateProduct,
    session: AsyncSession = Depends(get_session),
) -> Product:
    product = await BaseRepository(Product).get_by_id(session=session, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found!",
        )
    data_to_update = dict(data)
    product_db = await BaseRepository(Product).update(
        session=session, item=product, **data_to_update
    )
    return product_db


@router.delete("/{product_id}", status_code=200, summary="Delete product.")
async def delete_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Product:
    product = await BaseRepository(Product).get_by_id(session=session, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found!",
        )
    await BaseRepository(Product).delete(session=session, item=product)
    return {"message": "Delete product successfully!"}


@router.post(
    "/discount-price",
    status_code=200,
    summary="Get price of product after applying discount.",
)
async def get_product_discount_price(
    data: ProductDiscountPrice,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Dict:
    #   Admin place order for customer, so we must get customer information, not Admin
    if user.is_admin and data.customer_email:
        user = await BaseRepository(User).get_by_item(
            session=session, email=data.customer_email
        )
    #   Get added user information
    user_join_group = await get_user_group(session=session, user_id=user.id)
    product = await BaseRepository(Product).get_by_id(
        session=session, id=data.product_id
    )

    #   Calculate discount amount
    discount_amount = product.base_price * user_join_group.Group.discount_percent
    return {"price": product.base_price - discount_amount}


@router.post(
    "/price",
    status_code=200,
    summary="Get total price of a product.",
)
async def get_product_price(data: ProductPrice) -> Dict:
    product_price = data.discount_price * data.quantity
    return {"price": product_price}
