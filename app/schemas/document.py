"""
Schemas do gerador de documentos.
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

from app.schemas.client import AddressSchema


class ClientDataForDoc(BaseModel):
    fullName: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    nationality: Optional[str] = None
    maritalStatus: Optional[str] = None
    profession: Optional[str] = None
    address: Optional[AddressSchema] = None

    model_config = ConfigDict(populate_by_name=True)


class CaseDetailsSchema(BaseModel):
    processNumber: Optional[str] = None
    courtName: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class GenerateDocumentRequest(BaseModel):
    templateId: str
    clientData: ClientDataForDoc
    caseDetails: Optional[CaseDetailsSchema] = None

    model_config = ConfigDict(populate_by_name=True)


class GenerateDocumentResponse(BaseModel):
    documentUrl: str
    fileName: str