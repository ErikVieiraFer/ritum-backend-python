"""
Schemas de usuário.
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from uuid import UUID

from app.schemas.client import AddressSchema


class UserBase(BaseModel):
    email: EmailStr
    name: str
    oab_number: Optional[str] = None
    oab_state: Optional[str] = None
    cpf: Optional[str] = None
    address: Optional[AddressSchema] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    oab_number: Optional[str] = None
    oab_state: Optional[str] = None
    cpf: Optional[str] = None
    address: Optional[AddressSchema] = None
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str