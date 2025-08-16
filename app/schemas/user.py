from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
