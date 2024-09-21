from uuid import UUID
from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

from app.models.base import IdMixin, TimestampMixin
from app.api.enums import FulfillStatus as FulfillStatusEnum


class OrderBase(SQLModel):
    shipping_method: str
    shipping_location: str
    total_price: float


class Order(IdMixin, TimestampMixin, OrderBase, table=True):
    __tablename__ = "orders"

    user_id: UUID = Field(..., foreign_key="users.id")
    fulfill_status: Optional[str] = FulfillStatusEnum.unfulfilled
    fulfill_at: Optional[datetime] = None
    from_admin: bool


class OrderProduct(SQLModel, table=True):
    __tablename__ = "order_products"

    order_id: Optional[UUID] = Field(
        default=None, foreign_key="orders.id", primary_key=True
    )
    product_id: Optional[UUID] = Field(
        default=None, foreign_key="products.id", primary_key=True
    )
    quantity: int


class OrderProductRequest(SQLModel):
    product_id: UUID
    quantity: int


class OrderCreate(OrderBase):
    customer_email: Optional[str] = None
    items: list[OrderProductRequest]


class ProductDiscountPrice(SQLModel):
    customer_email: Optional[str] = None
    product_id: UUID


class ProductPrice(SQLModel):
    discount_price: float
    quantity: int


class OrderResponse(SQLModel):
    id: UUID
    created_at: datetime
    total_price: float
    fulfill_status: str
    shipping_method: str
    email: str
    total_quantity: int


class FulfillResponse(SQLModel):
    shipping_label: str
    tracking_number: str


class ShipFrom(SQLModel):
    company_name: str
    name: str
    phone: str
    address_line1: str
    city_locality: str
    state_province: Optional[str] = "TX"
    postal_code: Optional[str] = "95128"
    country_code: Optional[str] = "US"


class ShipTo(SQLModel):
    name: str
    phone: str
    address_line1: str
    city_locality: str
    postal_code: Optional[str] = "95128"
    country_code: Optional[str] = "US"


class Weight(SQLModel):
    value: float
    unit: Optional[str] = "ounce"


class Package(SQLModel):
    weight: Weight


class ShippingLabel(SQLModel):
    service_code: Optional[str] = "usps_priority_mail"
    ship_to: ShipTo
    ship_from: ShipFrom
    packages: list[Package]
