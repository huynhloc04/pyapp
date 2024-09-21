from enum import Enum


class ItemStatus(str, Enum):
    created = "created"
    updated = "updated"
    deleted = "deleted"
    failed = "failed"


class UserStatus(str, Enum):
    created = "created"
    updated = "updated"
    deleted = "deleted"
    inactive = "inactive"
    active = "active"
    failed = "failed"


class Group(str, Enum):
    starter = "starter"
    professional = "professional"
    vip = "vip"


class ShippingMethod(str, Enum):
    pickup = "pickup"
    freeship = "freeship"


class FulfillStatus(str, Enum):
    unfulfilled = "unfulfilled"
    fulfilled = "fulfilled"
