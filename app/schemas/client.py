"""
Schemas de cliente.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class AddressSchema(BaseModel):
    street: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = Field(None, alias='zipCode')

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class ClientBase(BaseModel):
    full_name: str = Field(..., alias='fullName')
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = Field(None, alias='maritalStatus')
    profession: Optional[str] = None
    address: Optional[AddressSchema] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    full_name: Optional[str] = Field(None, alias='fullName')
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = Field(None, alias='maritalStatus')
    profession: Optional[str] = None
    address: Optional[AddressSchema] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class Client(ClientBase):
    id: UUID
    owner_id: UUID = Field(..., alias='lawyerId')
    created_at: datetime = Field(..., alias='createdAt')
    updated_at: datetime = Field(..., alias='updatedAt')

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)