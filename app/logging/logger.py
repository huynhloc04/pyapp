from typing import Any
import logging
from app.api.enums import UserStatus, ItemStatus
from typing import Optional


def user_logger(
    status: str, user_id: Optional[str] = None, message: Optional[str] = None
) -> Any:
    logging.basicConfig(
        filename="app/logging/user.log",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
    )
    if status == UserStatus.created:
        logging.info(f"User {user_id}: Created, {message}")
    elif status == UserStatus.updated:
        logging.info(f"User {user_id}: Updated, {message}")


def email_logger(email_to: str, message: str) -> Any:
    logging.basicConfig(
        filename="app/logging/email.log",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
    )
    logging.info(f"Mail to {email_to}: {message}")


def item_logger(
    status: str, item_id: Optional[str] = None, message: Optional[str] = None
) -> Any:
    logging.basicConfig(
        filename="app/logging/item.log",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
    )
    if status == ItemStatus.created:
        logging.info(f"Item {item_id}: Created, {message}")
    elif status == ItemStatus.updated:
        logging.info(f"Item {item_id}: Updated, {message}")
    elif status == ItemStatus.deleted:
        logging.info(f"Item {item_id}: Deleted, {message}")
    elif status == ItemStatus.failed:
        logging.error(f"Item {item_id}: Error, {message}")
