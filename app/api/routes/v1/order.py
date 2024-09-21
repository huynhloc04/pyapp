from uuid import UUID
from typing import Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from app.db.session import get_session
from app.core.deps import get_current_user
from app.core.tasks import send_email_task
from app.api.enums import (
    FulfillStatus as FulfillStatusEnum,
    ShippingMethod as ShippingMethodEnum,
)
from app.repository import (
    BaseRepository,
    get_list_order,
    generate_shipping_label,
    get_user_order,
)
from app.models import (
    User,
    Order,
    Product,
    OrderCreate,
    OrderProduct,
    OrderResponse,
    ShippingLabel,
)


router = APIRouter(prefix="/orders", tags=["orders"])


@router.get(
    "/emails",
    response_model=list[str],
    status_code=200,
    summary="List all customer's emails.",
)
async def get_user_emails(session: AsyncSession = Depends(get_session)) -> list[str]:
    emails = await BaseRepository(User.email).get_all_by(
        session=session, is_admin=False
    )
    return emails


@router.post(
    "",
    response_model=Order,
    status_code=201,
    summary="Place an order.",
    description="shipping_method: 'freeship' or 'pickup'.",
)
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Order:
    #   Get user_id if admin places order
    from_admin = False
    if user.is_admin and data.customer_email:
        user = await BaseRepository(User).get_by_item(
            session=session, email=data.customer_email
        )
        from_admin = True

    #   Check whether product is in stock?
    for item in data.items:
        try:
            _ = await BaseRepository(Product).get_by_id(
                session=session, id=item.product_id
            )
        except:
            raise HTTPException(
                status_code=404,
                detail=f"Product #{item.product_id} is not available now!",
            )

    #   Place an order
    order_db = await BaseRepository(Order).create(
        session=session,
        user_id=user.id,
        total_price=data.total_price,
        shipping_method=data.shipping_method,
        shipping_location=data.shipping_location,
        from_admin=from_admin,
    )

    #   Attach order with products
    data_to_add = [{**dict(item), "order_id": order_db.id} for item in data.items]
    _ = await BaseRepository(OrderProduct).create_all(
        session=session, data_lst=data_to_add
    )

    return order_db


@router.get(
    "",
    response_model=list[OrderResponse],
    status_code=200,
    summary="Get all orders according to specific users",
)
async def list_order(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[OrderResponse]:
    orders = await get_list_order(session=session, user=user)
    return orders


@router.get(
    "/{order_id}",
    response_model=Order,
    status_code=200,
    summary="Get order detail.",
)
async def get_user_emails(
    order_id: UUID, session: AsyncSession = Depends(get_session)
) -> Order:
    order = await BaseRepository(Order).get_by_id(session=session, id=order_id)
    return order


@router.delete("/{order_id}", status_code=200, summary="Delete order.")
async def delete_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Dict:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Do not have sufficient rights!",
        )
    order = await BaseRepository(Order).get_by_id(session=session, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found!",
        )
    await BaseRepository(Order).delete(session=session, item=order)
    return {"message": "Delete order successfully!"}


@router.post(
    "/{order_id}/fulfill",
    status_code=201,
    summary="Fulfill an order.",
)
async def fulfill_order(
    order_id: UUID, data: ShippingLabel, session: AsyncSession = Depends(get_session)
) -> Dict:

    user_order = await get_user_order(session=session, order_id=order_id)

    #   Specify mail content based on shipping location/method
    mail_subject = f"The Order {user_order.Order.id} has been fulfilled."
    response = {"message": "Order is fulfilled!"}

    if user_order.Order.shipping_method == ShippingMethodEnum.freeship:  #   warehouse
        #   Fulfill the order
        shipping_label, tracking_number = generate_shipping_label(data)

        #   Send mail
        mail_body = f"""
            Dear {user_order.User.name},

            We're excited to inform you that your order #{user_order.Order.id} has been successfully fulfilled.

            Order details:
             - Shipping Method: {user_order.Order.shipping_method.capitalize()}
             - Tracking Number: {tracking_number}

            Your order is on its way. You can track your order using the tracking number provided above.
            Thank you for shopping with {data.ship_from.company_name}. If you have any questions or require further assistance, please don't hesitate to contact our customer support.

            Best regards,
            {data.ship_from.company_name}
        """

        response = {
            "shipping_label": shipping_label,
            "tracking_number": tracking_number,
        }
    else:  #   pickup
        mail_body = f"""
            Dear {user_order.User.name},

            We're excited to inform you that your order #{user_order.Order.id} has been successfully fulfilled.

            Order details:
             - Shipping Method: {user_order.Order.shipping_method.capitalize()}

            Please visit our store at {user_order.Order.shipping_location} to collect your order.
            Thank you for shopping with {data.ship_from.company_name}. If you have any questions or require further assistance, please don't hesitate to contact our customer support.

            Best regards,
            {data.ship_from.company_name}
        """
    #   Use celery to send mail
    _ = send_email_task.delay(mail_subject, mail_body, user_order.User.email)

    #   Update order status
    _ = await BaseRepository(Order).update_by_id(
        session=session,
        id=order_id,
        fulfill_status=FulfillStatusEnum.fulfilled,
        fulfill_at=datetime.now(),
    )

    return response
