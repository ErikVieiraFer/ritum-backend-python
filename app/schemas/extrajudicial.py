"""
Schemas do assistente extrajudicial.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID

from app.schemas.client import AddressSchema


class PersonSchema(BaseModel):
    full_name: Optional[str] = Field(None, alias='fullName')
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = Field(None, alias='maritalStatus')
    profession: Optional[str] = None
    rg: Optional[str] = None
    cpf: Optional[str] = None
    address: Optional[AddressSchema] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class AssetSchema(BaseModel):
    description: str
    value: float
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class DebtSchema(BaseModel):
    description: str
    value: float
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class ChildSchema(PersonSchema):
    birth_date: Optional[date] = Field(None, alias='birthDate')
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class CaseCreateRequest(BaseModel):
    case_type: str = Field(..., alias='caseType')
    case_name: str = Field(..., alias='caseName')
    model_config = ConfigDict(populate_by_name=True)


class CaseUpdateRequest(BaseModel):
    data: Dict[str, Any]
    model_config = ConfigDict(populate_by_name=True)


class CaseResponse(BaseModel):
    id: UUID
    owner_id: UUID
    case_type: str = Field(..., alias='caseType')
    case_name: str = Field(..., alias='caseName')
    status: str
    data: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(..., alias='createdAt')
    updated_at: datetime = Field(..., alias='updatedAt')

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)