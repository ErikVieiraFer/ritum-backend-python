# ritum-backend/app/schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Union, Dict, Any
from datetime import datetime, date
from uuid import UUID

# ==============================================================================
# SCHEMAS DE AUTENTICAÇÃO E USUÁRIO
# ==============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    name: str
    oab_number: Optional[str] = None
    oab_state: Optional[str] = None
    cpf: Optional[str] = None
    address: Optional['AddressSchema'] = None # Forward reference
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID # Changed to UUID
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    oab_number: Optional[str] = None
    oab_state: Optional[str] = None
    cpf: Optional[str] = None
    address: Optional['AddressSchema'] = None
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

# ==============================================================================
# SCHEMAS DE CLIENTES, PROCESSOS E KANBAN (Existentes)
# ==============================================================================

# --- Clientes ---
class AddressSchema(BaseModel):
    street: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = Field(None, alias='zipCode')

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

# Update forward reference for AddressSchema
UserBase.model_rebuild()

class ClientBase(BaseModel):
    full_name: str = Field(..., alias='fullName') # Changed from 'name' to 'full_name'
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

class ClientUpdate(BaseModel): # Inherits from BaseModel, not ClientBase, to make all fields optional
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
    id: UUID # Changed to UUID
    owner_id: UUID = Field(..., alias='lawyerId') # Changed to UUID
    created_at: datetime = Field(..., alias='createdAt')
    updated_at: datetime = Field(..., alias='updatedAt')

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# --- Processos ---
class ProcessUpdateBase(BaseModel):
    date: datetime
    description: str

class ProcessUpdateCreate(ProcessUpdateBase):
    pass

class ProcessUpdate(ProcessUpdateBase):
    id: int
    process_id: int
    model_config = ConfigDict(from_attributes=True)

class ProcessBase(BaseModel):
    number: str
    client_name: str
    type: str
    status: Optional[str] = "Ativo"

class ProcessCreate(ProcessBase):
    pass

class Process(ProcessBase):
    id: int
    owner_id: UUID # Changed to UUID
    updates: List[ProcessUpdate] = []
    model_config = ConfigDict(from_attributes=True)

# --- Kanban ---
class TaskCardBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskCardCreate(TaskCardBase):
    pass

class TaskCard(TaskCardBase):
    id: int
    column_id: int
    model_config = ConfigDict(from_attributes=True)

class TaskCardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskCardMove(BaseModel):
    new_column_id: int

class TaskColumnBase(BaseModel):
    title: str
    position: int

class TaskColumnCreate(TaskColumnBase):
    pass

class TaskColumn(TaskColumnBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TaskColumnWithCards(TaskColumn):
    cards: List[TaskCard] = []

class TaskColumnUpdate(BaseModel):
    title: str

# ==============================================================================
# SCHEMAS DO REDATOR EXTRAJUDICIAL (Mantidos, mas AddressSchema foi movido)
# ==============================================================================

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

# --- Schemas para os Endpoints da API ---

class CaseCreateRequest(BaseModel):
    case_type: str = Field(..., alias='caseType')
    case_name: str = Field(..., alias='caseName')
    model_config = ConfigDict(populate_by_name=True)

class CaseUpdateRequest(BaseModel):
    # Simplificado para Dict para evitar problemas de carregamento no Swagger UI
    data: Dict[str, Any]
    model_config = ConfigDict(populate_by_name=True)

class CaseResponse(BaseModel):
    id: UUID
    owner_id: UUID # Changed to UUID
    case_type: str = Field(..., alias='caseType')
    case_name: str = Field(..., alias='caseName')
    status: str
    # Simplificado para Dict para evitar problemas de carregamento no Swagger UI
    data: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(..., alias='createdAt')
    updated_at: datetime = Field(..., alias='updatedAt')

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# ==============================================================================
# SCHEMAS DE INTELIGÊNCIA ARTIFICIAL (Restaurados)
# ==============================================================================

class PromptGenerationRequest(BaseModel):
    facts: str

class PromptGenerationResponse(BaseModel):
    generated_prompt: str

class PetitionGenerationRequest(BaseModel):
    prompt: str

class PetitionGenerationResponse(BaseModel):
    generated_petition: str

# ==============================================================================
# SCHEMAS DE BUSCA DE JURISPRUDÊNCIA (DATAJUD)
# ==============================================================================

class JurisprudenceSearchRequest(BaseModel):
    """Schema para a requisição de busca de jurisprudência."""
    q: str = Field(..., description="A query de busca do usuário, contendo a descrição do caso ou palavras-chave.")

class DataJudResult(BaseModel):
    """Schema para um único resultado da busca na API DataJud."""
    score: Optional[float] = None
    processo: Optional[str] = None
    tribunal: Optional[str] = None
    data_ajuizamento: Optional[str] = None # Mantido como string para simplicidade
    classe: Optional[str] = None
    assuntos: List[str] = []
    orgao_julgador: Optional[str] = None

class DataJudSearchResponse(BaseModel):
    """Schema para a resposta completa da busca na API DataJud."""
    results: List[DataJudResult]

# ==============================================================================
# SCHEMAS DO GERADOR DE DOCUMENTOS
# ==============================================================================

class ClientDataForDoc(BaseModel):
    # Este schema é flexível para aceitar os dados do cliente diretamente.
    # Os campos são opcionais para não quebrar se algo não for enviado.
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
    # Adicione outros campos específicos do caso conforme necessário
    
    model_config = ConfigDict(populate_by_name=True)

class GenerateDocumentRequest(BaseModel):
    templateId: str
    clientData: ClientDataForDoc
    caseDetails: Optional[CaseDetailsSchema] = None

    model_config = ConfigDict(populate_by_name=True)

class GenerateDocumentResponse(BaseModel):
    documentUrl: str
    fileName: str

# ==============================================================================
# SCHEMAS DE INTIMAÇÕES
# ==============================================================================

class IntimationBase(BaseModel):
    publication_date: date
    process_number: str
    content: str

class Intimation(IntimationBase):
    id: UUID
    owner_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class IntimationStats(BaseModel):
    count: int

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
