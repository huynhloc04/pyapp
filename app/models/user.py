from uuid import UUID
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import BaseModel, Field

from app.models.base import IdMixin, TimestampMixin


class UserBase(SQLModel):
    name: str
    phone: str
    address: str
    email: str
    is_admin: bool = False


class UserUpdate(SQLModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None


class UserSignUp(UserBase):
    group_id: Optional[UUID] = None
    password: str


class UserResponse(IdMixin, TimestampMixin, UserBase): ...


class User(IdMixin, TimestampMixin, UserBase, table=True):
    __tablename__ = "users"

    group_id: Optional[UUID] = Field(None, foreign_key="groups.id")
    password: str


class GroupBase(SQLModel):
    name: str = Field(..., unique=True)
    discount_percent: float


class UpdateGroup(SQLModel):
    name: Optional[str] = None
    discount_percent: Optional[float] = None


class Group(IdMixin, TimestampMixin, GroupBase, table=True):
    __tablename__ = "groups"
    ...


class TokenSchema(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
