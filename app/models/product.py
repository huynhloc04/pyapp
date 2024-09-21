from typing import Optional
from sqlmodel import SQLModel

from app.models.base import IdMixin, TimestampMixin


class ProductBase(SQLModel):
    name: str
    base_price: float
    description: Optional[str] = None


class UpdateProduct(SQLModel):
    name: Optional[str] = None
    base_price: Optional[float] = None
    description: Optional[str] = None


class Product(IdMixin, TimestampMixin, ProductBase, table=True):
    __tablename__ = "products"
    ...
