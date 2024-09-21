import requests
import json
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import desc
from sqlalchemy import func, select

from app.core.config import settings
from app.models import User, Order, OrderProduct


async def get_list_order(session: AsyncSession, user: User):
    statement = (
        select(
            Order.id,
            Order.created_at,
            Order.total_price,
            Order.fulfill_status,
            Order.shipping_method,
            User.email,
            func.sum(OrderProduct.quantity).label("total_quantity"),
        )
        .join(User, Order.user_id == User.id)
        .join(OrderProduct, Order.id == OrderProduct.order_id)
        .group_by(Order.id, User.email)
        .filter(User.id == user.id if not user.is_admin else Order.from_admin == True)
    )
    result = await session.execute(statement)
    return result.all()


async def get_user_order(session: AsyncSession, order_id: UUID):
    statement = (
        select(User, Order)
        .join(Order, User.id == Order.user_id)
        .filter(Order.id == order_id)
    )
    result = await session.execute(statement)
    return result.first()


def generate_shipping_label(data):
    payload = dict(data)
    payload["ship_to"] = dict(data.ship_to)
    payload["ship_from"] = dict(data.ship_from)
    payload["packages"] = [
        {"weight": dict(package.weight)} for package in data.packages
    ]

    headers = {
        "Host": "api.shipengine.com",
        "API-Key": settings.SHIPENGINE_API_KEY,
        "Content-Type": "application/json",
        "Content-Length": "1054",
    }

    #   Make a request
    try:
        response = requests.post(
            settings.SHIPENGINE_URL,
            headers=headers,
            data=json.dumps({"shipment": payload}),
        )
        response = response.json()
        shipping_label = response.get("label_download").get("pdf")
        tracking_number = response.get("packages")[0].get("tracking_number")
        return shipping_label, tracking_number
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
