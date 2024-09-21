from sqlmodel import SQLModel

from app.models.base import IdMixin, TimestampMixin


class StoreBase(SQLModel):
    name: str
    address: str
    is_store: bool = True  #   warehouse or store


class Store(IdMixin, TimestampMixin, StoreBase, table=True):
    __tablename__ = "stores"

    ...


class ShippingMethod(SQLModel):
    shipping_method: str
